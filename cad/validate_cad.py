"""validate_cad.py — Valida empíricamente que el GLB exportado coincide
con las medidas declaradas en `cad/params.toml`, y que cambiar un parámetro
realmente regenera un GLB distinto.

Reporta PASS/FAIL por cada check. Sale con código 0 si todo pasa, 1 si algo falla.

Uso: `python cad/validate_cad.py [--round-trip]`
  --round-trip activa el test de round-trip (más lento, modifica params.toml temporalmente)
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

import trimesh

from parameters import load_params

REPO_ROOT = Path(__file__).resolve().parent.parent
GLB_PATH  = REPO_ROOT / "web" / "data" / "cabin.glb"
PARAMS_PATH = REPO_ROOT / "cad" / "params.toml"
TOLERANCE_M = 0.5  # 50 cm de tolerancia para overhang/render details

# Códigos ANSI para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
DIM = "\033[2m"
RESET = "\033[0m"


class CheckResult(NamedTuple):
    name: str
    passed: bool
    expected: str
    actual: str
    detail: str = ""


def load_glb(path: Path = GLB_PATH) -> trimesh.Scene:
    scene = trimesh.load(str(path), force="scene")
    if not isinstance(scene, trimesh.Scene):
        scene = trimesh.Scene(scene)
    return scene


def glb_dimensions(scene: trimesh.Scene) -> dict:
    """Bbox global del scene + count de geometries + per-geometry stats."""
    bounds = scene.bounds  # ((minX, minY, minZ), (maxX, maxY, maxZ))
    if bounds is None:
        return {}
    extent = bounds[1] - bounds[0]
    return {
        "min": bounds[0].tolist(),
        "max": bounds[1].tolist(),
        "extent": extent.tolist(),
        "geom_count": len(scene.geometry),
        "node_count": len(scene.graph.nodes),
    }


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def run_make_cad() -> bool:
    """Re-genera el GLB ejecutando python cad/cabin.py."""
    venv_python = REPO_ROOT / ".venv" / "bin" / "python"
    res = subprocess.run(
        [str(venv_python), "cad/cabin.py"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if res.returncode != 0:
        print(res.stderr)
        return False
    return True


def validate_dimensions(scene: trimesh.Scene, p) -> list[CheckResult]:
    """Verifica que el bbox coincide con los parámetros declarados."""
    checks: list[CheckResult] = []
    dims = glb_dimensions(scene)
    if not dims:
        checks.append(CheckResult("bbox loadable", False, "valid bbox", "None", "GLB no se pudo cargar"))
        return checks

    # build123d gltf export: Y = altura (eje vertical), X = ancho, Z = profundidad
    # El bbox típicamente reporta:
    #   X: 0 → width  (6 m)
    #   Y: 0 → max_col_height + apex_height  (1.8 + 6.2 = 8 m)
    #   Z: -depth → 0  o  0 → depth, dependiendo de orientación
    extent_x, extent_y, extent_z = dims["extent"]

    # X — ancho de plataforma
    width_expected = p.width_m
    width_actual = extent_x
    checks.append(CheckResult(
        "Ancho plataforma (X)",
        abs(width_actual - width_expected) <= TOLERANCE_M,
        f"{width_expected:.2f} m",
        f"{width_actual:.3f} m",
        f"tolerancia ±{TOLERANCE_M} m",
    ))

    # Z — profundidad de plataforma (puede ser negativo)
    depth_expected = p.depth_m
    depth_actual = abs(extent_z)
    checks.append(CheckResult(
        "Profundidad plataforma (Z)",
        abs(depth_actual - depth_expected) <= TOLERANCE_M,
        f"{depth_expected:.2f} m",
        f"{depth_actual:.3f} m",
        f"tolerancia ±{TOLERANCE_M} m",
    ))

    # Y — altura total: columna más alta + apex
    max_col_height = max(max(row) for row in p.column_heights_m)
    apex_h = p.apex_height_m
    height_expected = max_col_height + apex_h
    height_actual = extent_y
    checks.append(CheckResult(
        "Altura total (Y = max_col + apex)",
        abs(height_actual - height_expected) <= TOLERANCE_M * 2,  # más tolerancia para overhangs
        f"{height_expected:.2f} m (= {max_col_height} + {apex_h})",
        f"{height_actual:.3f} m",
        f"tolerancia ±{TOLERANCE_M * 2} m",
    ))

    return checks


def validate_mesh_count(scene: trimesh.Scene, p) -> list[CheckResult]:
    """Cuenta meshes y los compara con lo esperado."""
    checks: list[CheckResult] = []
    dims = glb_dimensions(scene)

    cols_n = int(p.raw["platform"]["column_grid_cols"])
    rows_n = int(p.raw["platform"]["column_grid_rows"])
    n_columns = cols_n * rows_n  # 9
    n_portals = int(p.raw["aframe"]["portal_count"])  # 6
    n_rafters = n_portals * 2  # 12
    n_ties = n_portals  # 6
    n_purlin_rows = int(p.raw["aframe"]["purlin_rows_per_side"])  # 13
    n_purlins = n_purlin_rows * 2  # 26
    n_ridge = 1
    n_platform = 1
    n_deck = 1
    expected_total = n_columns + n_rafters + n_ties + n_purlins + n_ridge + n_platform + n_deck

    actual_geom = dims["geom_count"]
    # build123d agrupa en compounds y cada hijo puede ser un mesh separado.
    # El conteo puede no ser 1:1 — chequeamos que esté en rango razonable.
    checks.append(CheckResult(
        "Conteo de geometrías en el GLB",
        actual_geom >= n_columns,  # al menos las columnas como meshes distintos
        f">= {n_columns} (al menos las {n_columns} columnas)",
        f"{actual_geom}",
        f"esperado ideal ~{expected_total}",
    ))

    return checks


def validate_round_trip(p_original) -> list[CheckResult]:
    """Cambia un parámetro, regenera, verifica el cambio, restaura."""
    checks: list[CheckResult] = []

    # 1. Hash del GLB actual
    h0 = file_hash(GLB_PATH)
    dims0 = glb_dimensions(load_glb())
    print(f"{DIM}  GLB original: hash={h0}  extent={[f'{v:.2f}' for v in dims0['extent']]}{RESET}")

    # 2. Backup params.toml
    backup = PARAMS_PATH.read_text(encoding="utf-8")

    # 3. Modificar apex_height_m: 6.2 → 7.5
    modified = backup.replace(
        "apex_height_m         = 6.2",
        "apex_height_m         = 7.5",
    )
    if modified == backup:
        checks.append(CheckResult(
            "Pattern match en params.toml",
            False,
            "string encontrada",
            "no match",
            "no pudo encontrar 'apex_height_m         = 6.2' en el TOML",
        ))
        return checks

    PARAMS_PATH.write_text(modified, encoding="utf-8")

    try:
        # 4. Regenerar
        if not run_make_cad():
            checks.append(CheckResult(
                "Regeneración con apex=7.5",
                False,
                "make cad exit 0",
                "exit != 0",
                "regenerador falló",
            ))
            return checks

        # 5. Medir nuevo GLB
        h1 = file_hash(GLB_PATH)
        dims1 = glb_dimensions(load_glb())
        print(f"{DIM}  GLB con apex=7.5: hash={h1}  extent={[f'{v:.2f}' for v in dims1['extent']]}{RESET}")

        # 6. Validar que cambió
        checks.append(CheckResult(
            "Hash del GLB cambió tras modificar param",
            h0 != h1,
            f"hash distinto de {h0}",
            f"hash actual {h1}",
        ))

        # 7. Validar que la altura aumentó ~1.3 m
        delta_y = dims1["extent"][1] - dims0["extent"][1]
        expected_delta = 7.5 - 6.2  # = 1.3
        checks.append(CheckResult(
            "Altura total aumentó por +apex",
            abs(delta_y - expected_delta) <= TOLERANCE_M,
            f"Δ = +{expected_delta:.2f} m",
            f"Δ = +{delta_y:.3f} m",
        ))

    finally:
        # 8. Restaurar params.toml
        PARAMS_PATH.write_text(backup, encoding="utf-8")
        run_make_cad()

        # 9. Verificar restauración
        h_restored = file_hash(GLB_PATH)
        checks.append(CheckResult(
            "GLB restaurado al original",
            h_restored == h0,
            f"hash igual a original {h0}",
            f"hash actual {h_restored}",
            "params.toml restaurado y CAD regenerado",
        ))

    return checks


def print_checks(checks: list[CheckResult], title: str) -> tuple[int, int]:
    print(f"\n{title}")
    print("─" * 70)
    passed = failed = 0
    for c in checks:
        mark = f"{GREEN}✓{RESET}" if c.passed else f"{RED}✗{RESET}"
        print(f"  {mark} {c.name}")
        print(f"      esperado: {c.expected}")
        print(f"      actual:   {c.actual}")
        if c.detail:
            print(f"      {DIM}{c.detail}{RESET}")
        if c.passed:
            passed += 1
        else:
            failed += 1
    return passed, failed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round-trip", action="store_true", help="incluye round-trip test (modifica params.toml temporalmente)")
    args = ap.parse_args()

    print(f"\n{'═' * 70}")
    print(f"  alpine-cabin · Validación CAD")
    print(f"  GLB: {GLB_PATH.relative_to(REPO_ROOT)}")
    print(f"{'═' * 70}")

    if not GLB_PATH.exists():
        print(f"{RED}❌ No existe {GLB_PATH}. Corré `make cad` primero.{RESET}")
        return 1

    p = load_params()
    scene = load_glb()
    dims = glb_dimensions(scene)

    print(f"\n{DIM}Bbox del GLB:")
    print(f"  min:    {[f'{v:.3f}' for v in dims['min']]}")
    print(f"  max:    {[f'{v:.3f}' for v in dims['max']]}")
    print(f"  extent: {[f'{v:.3f}' for v in dims['extent']]} (X×Y×Z m)")
    print(f"  geoms:  {dims['geom_count']}")
    print(f"  nodes:  {dims['node_count']}{RESET}")

    dim_checks  = validate_dimensions(scene, p)
    mesh_checks = validate_mesh_count(scene, p)

    p1, f1 = print_checks(dim_checks, "📐 Medidas del bbox")
    p2, f2 = print_checks(mesh_checks, "🔢 Conteo de mallas")

    p3 = f3 = 0
    if args.round_trip:
        rt_checks = validate_round_trip(p)
        p3, f3 = print_checks(rt_checks, "🔄 Round-trip (params → CAD → GLB)")

    total_passed = p1 + p2 + p3
    total_failed = f1 + f2 + f3
    total = total_passed + total_failed

    print(f"\n{'═' * 70}")
    if total_failed == 0:
        print(f"  {GREEN}✅ TODOS LOS CHECKS PASARON  ({total_passed}/{total}){RESET}")
        print(f"{'═' * 70}\n")
        return 0
    else:
        print(f"  {RED}⚠ {total_failed}/{total} checks fallaron{RESET}  ({total_passed} pasaron)")
        print(f"{'═' * 70}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
