"""apply_experiment.py — Aplica un JSON exportado del HTML al repo.

Lee el JSON (formato definido en ARCHITECTURE.md §5.2), valida el schema,
muestra diff contra `cad/params.toml` actual, pide confirmación, escribe
los nuevos valores y regenera todos los derivados (BOM + CAD + web data).

Uso:
    python cad/apply_experiment.py path/al/experimento.json
    python cad/apply_experiment.py path/al/experimento.json --yes  # sin prompt

Schema esperado del JSON:
    {
      "schema_version": "1.0",
      "exported_at": "...",
      "exported_from": "...",
      "base_commit": "...",
      "delta_paths": {                           # paths que cambiaron vs baseline
        "platform.width_m": 6.5,
        "aframe.apex_height_m": 7.0,
        ...
      },
      "full_params": { ... },                    # estado completo (no usado, redundante)
      "kpis_snapshot": { ... },                  # snapshot informativo
      "annotations": "..."
    }

Solo se aplican los paths declarados en `delta_paths`. Cada path se mapea
a una sección.clave en `cad/params.toml`. Tipos preservados.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT  = Path(__file__).resolve().parent.parent
PARAMS_PATH = REPO_ROOT / "cad" / "params.toml"
SCHEMA_VERSION = "1.0"

# Paths permitidos para escritura (whitelist explícita por seguridad).
# Cualquier path fuera de esta lista es rechazado con error claro.
ALLOWED_PATHS = {
    "platform.width_m":              ("float", None),
    "platform.depth_m":              ("float", None),
    "envelope.enclosed_depth_m":     ("float", None),
    "envelope.terrace_depth_m":      ("float", None),
    "aframe.apex_height_m":          ("float", None),
    "aframe.portal_count":           ("int",   None),
    "aframe.portal_spacing_m":       ("float", None),
    "aframe.purlin_rows_per_side":   ("int",   None),
    "columns.anchors_per_column":    ("int",   None),
    "envelope.front_glazing_m2":     ("float", None),
    "envelope.rear_gable_m2":        ("float", None),
}

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
DIM = "\033[2m"
RESET = "\033[0m"


def validate_experiment(exp: dict) -> tuple[bool, list[str]]:
    """Valida estructura mínima del experiment JSON. Retorna (ok, errores)."""
    errs: list[str] = []
    if exp.get("schema_version") != SCHEMA_VERSION:
        errs.append(f"schema_version != {SCHEMA_VERSION} (encontrado: {exp.get('schema_version')!r})")

    delta = exp.get("delta_paths", {})
    if not isinstance(delta, dict):
        errs.append("delta_paths debe ser un objeto/dict")
        return False, errs

    for path, value in delta.items():
        if path not in ALLOWED_PATHS:
            errs.append(f"path no permitido: {path!r} (whitelist en cad/apply_experiment.py)")
            continue
        kind, _ = ALLOWED_PATHS[path]
        if kind == "float" and not isinstance(value, (int, float)):
            errs.append(f"{path}: esperaba número, recibió {type(value).__name__}")
        elif kind == "int" and not isinstance(value, int):
            # JSON puede entregar float incluso si conceptualmente es int
            if isinstance(value, float) and value.is_integer():
                continue
            errs.append(f"{path}: esperaba entero, recibió {type(value).__name__}={value}")

    return len(errs) == 0, errs


def toml_path_pattern(path: str) -> tuple[str, str]:
    """Para un path tipo 'aframe.apex_height_m' retorna (section, key)."""
    parts = path.split(".")
    if len(parts) != 2:
        raise ValueError(f"path debe ser 'seccion.clave', recibido: {path!r}")
    return parts[0], parts[1]


def read_toml_value(content: str, section: str, key: str) -> str | None:
    """Extrae el valor actual de un key dentro de una sección, como string."""
    sec_re = re.compile(rf"^\[{re.escape(section)}\]\s*$", re.MULTILINE)
    m = sec_re.search(content)
    if not m:
        return None
    # Buscar siguiente sección
    next_sec = re.search(r"^\[[^\]]+\]\s*$", content[m.end():], re.MULTILINE)
    section_body = content[m.end(): m.end() + (next_sec.start() if next_sec else len(content))]
    key_re = re.compile(rf"^\s*{re.escape(key)}\s*=\s*(.+?)\s*$", re.MULTILINE)
    km = key_re.search(section_body)
    return km.group(1).strip() if km else None


def write_toml_value(content: str, section: str, key: str, new_value: str) -> tuple[str, bool]:
    """Reescribe el valor de section.key. Retorna (nuevo_content, modificado)."""
    sec_re = re.compile(rf"^\[{re.escape(section)}\]\s*$", re.MULTILINE)
    m = sec_re.search(content)
    if not m:
        return content, False

    body_start = m.end()
    next_sec = re.search(r"^\[[^\]]+\]\s*$", content[body_start:], re.MULTILINE)
    body_end = body_start + (next_sec.start() if next_sec else len(content) - body_start)
    section_body = content[body_start: body_end]

    key_pattern = re.compile(rf"^(\s*{re.escape(key)}\s*=\s*)(.+?)(\s*)$", re.MULTILINE)
    new_body, n = key_pattern.subn(rf"\g<1>{new_value}\3", section_body, count=1)
    if n == 0:
        return content, False

    return content[:body_start] + new_body + content[body_end:], True


def format_value(value: Any, kind: str) -> str:
    if kind == "int":
        return str(int(value))
    elif kind == "float":
        # Normaliza con punto decimal si es entero
        f = float(value)
        if f == int(f):
            return f"{f:.1f}"
        return f"{f:g}"
    else:
        return repr(value)


def run_make_all() -> int:
    """Regenera BOM + CAD + web data."""
    venv_python = REPO_ROOT / ".venv" / "bin" / "python"
    if not venv_python.exists():
        venv_python = Path(sys.executable)

    steps = [
        ("BOM", "bom_generator.py"),
        ("CAD", "cabin.py"),
        ("web data", "export_web_data.py"),
    ]
    for label, script in steps:
        print(f"{BLUE}→ Regenerando {label} ({script})...{RESET}")
        res = subprocess.run(
            [str(venv_python), f"cad/{script}"],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
        if res.returncode != 0:
            print(f"{RED}❌ Falló: {res.stderr or res.stdout}{RESET}")
            return res.returncode
        print(f"{DIM}{res.stdout.strip()}{RESET}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path", help="JSON exportado del HTML interactivo")
    ap.add_argument("--yes", "-y", action="store_true",
                    help="aplica sin pedir confirmación (úsalo con cuidado)")
    ap.add_argument("--regenerate/--no-regenerate", dest="regenerate",
                    action=argparse.BooleanOptionalAction, default=True,
                    help="corre make all tras aplicar (default: sí)")
    args = ap.parse_args()

    json_path = Path(args.json_path)
    if not json_path.exists():
        print(f"{RED}❌ No existe {json_path}{RESET}")
        return 1

    exp = json.loads(json_path.read_text(encoding="utf-8"))

    # 1. Validar
    ok, errs = validate_experiment(exp)
    if not ok:
        print(f"{RED}❌ JSON inválido:{RESET}")
        for e in errs:
            print(f"   - {e}")
        return 2

    delta = exp["delta_paths"]
    if not delta:
        print(f"{YELLOW}⚠ El experimento no tiene cambios respecto al baseline. Nada que aplicar.{RESET}")
        return 0

    # 2. Leer params.toml actual
    original = PARAMS_PATH.read_text(encoding="utf-8")
    modified = original

    # 3. Calcular cambios + mostrar diff
    print(f"\n{BLUE}Cambios propuestos desde {json_path.name}:{RESET}")
    print(f"{DIM}  base_commit:  {exp.get('base_commit', 'unknown')}")
    print(f"  exported_at:  {exp.get('exported_at', 'unknown')}")
    print(f"  annotations:  {exp.get('annotations', '') or '(ninguna)'}{RESET}")
    print()

    changes_applied: list[tuple[str, str, str]] = []
    for path, new_value in delta.items():
        section, key = toml_path_pattern(path)
        kind, _ = ALLOWED_PATHS[path]
        new_value_str = format_value(new_value, kind)
        current_value = read_toml_value(modified, section, key)
        if current_value is None:
            print(f"{YELLOW}  ⚠ {path}: clave no encontrada en params.toml — se omite{RESET}")
            continue
        if current_value == new_value_str:
            print(f"{DIM}  · {path}: ya está en {new_value_str} — sin cambio{RESET}")
            continue

        modified, ok = write_toml_value(modified, section, key, new_value_str)
        if not ok:
            print(f"{RED}  ❌ {path}: fallo al reescribir{RESET}")
            continue

        print(f"  {GREEN}✎{RESET} {path:<32}  {current_value:>10}  →  {GREEN}{new_value_str}{RESET}")
        changes_applied.append((path, current_value, new_value_str))

    if not changes_applied:
        print(f"\n{YELLOW}Nada para aplicar (todos los valores ya coinciden).{RESET}")
        return 0

    # 4. Confirmar
    if not args.yes:
        print()
        resp = input(f"{BLUE}¿Aplicar estos {len(changes_applied)} cambio(s) a cad/params.toml? [y/N] {RESET}")
        if resp.strip().lower() not in ("y", "yes", "s", "si", "sí"):
            print(f"{YELLOW}Cancelado por el usuario.{RESET}")
            return 0

    # 5. Escribir
    PARAMS_PATH.write_text(modified, encoding="utf-8")
    print(f"\n{GREEN}✅ cad/params.toml actualizado.{RESET}")

    # 6. Regenerar derivados
    if args.regenerate:
        rc = run_make_all()
        if rc != 0:
            print(f"{RED}⚠ Regeneración falló. params.toml ya fue modificado — revisa manualmente.{RESET}")
            return rc

    # 7. Sugerir commit
    print(f"\n{BLUE}Listo. Próximos pasos sugeridos:{RESET}")
    print(f"  git diff cad/params.toml BOM.md web/data/")
    print(f"  git add -A && git commit -m \"experiment: aplicar {json_path.stem}\"")
    print(f"  git push")

    return 0


if __name__ == "__main__":
    sys.exit(main())
