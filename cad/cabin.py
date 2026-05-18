"""cabin.py — Modelo CAD paramétrico de la cabaña usando build123d.

Genera la geometría completa (columnas, plataforma, A-frame, correas, cumbrera)
a partir de los parámetros de params.toml. Exporta STEP, STL y GLTF.

Uso: `python cad/cabin.py` (genera cad/exports/cabin.{step,stl,glb,png}).
"""
from __future__ import annotations

from math import atan2, degrees
from pathlib import Path

import build123d as bd

from parameters import Params, load_params

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORTS_DIR = REPO_ROOT / "cad" / "exports"
WEB_DATA_DIR = REPO_ROOT / "web" / "data"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)


def make_steel_member(length_m: float, profile_width_mm: float, profile_height_mm: float) -> bd.Part:
    """Modela un miembro estructural como un prisma rectangular.

    Para M0.3.4 no modelamos secciones huecas (HSS) ni I-beams reales —
    suficiente para visualización 3D y validación de geometría / ensamble.
    Las secciones reales se introducen en M0.3.4.1 cuando el ingeniero
    estructural cierre los perfiles definitivos.
    """
    L = length_m * 1000  # mm en build123d
    w = profile_width_mm
    h = profile_height_mm
    return bd.Box(L, w, h, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER))


def build_columns(p: Params) -> bd.Compound:
    """9 columnas en malla 3 × 3, alturas variables por roca."""
    prof = p.profile(p.raw["columns"]["profile"])
    cols_n = int(p.raw["platform"]["column_grid_cols"])
    rows_n = int(p.raw["platform"]["column_grid_rows"])
    width_m = p.width_m
    depth_m = p.depth_m
    heights = p.column_heights_m

    parts: list[bd.Part] = []
    for row in range(rows_n):
        for col in range(cols_n):
            x = (col / (cols_n - 1)) * width_m * 1000 if cols_n > 1 else 0
            y = (row / (rows_n - 1)) * depth_m * 1000 if rows_n > 1 else 0
            h_m = heights[row][col]
            # Columna vertical: caja (prof.width × prof.height) × altura
            col_part = bd.Box(
                prof.width_mm, prof.height_mm, h_m * 1000,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
            )
            col_part = col_part.translate((x, y, 0))
            parts.append(col_part)

    return bd.Compound(label="columns", children=parts)


def build_platform(p: Params, platform_z_mm: float) -> bd.Compound:
    """Plataforma: vigas perimetrales + viguetas + losa indicativa."""
    # Para el modelo visual M0.3.4, simplifico: una losa rectangular
    # representando el conjunto plataforma + tablero.
    plataforma = bd.Box(
        p.width_m * 1000, p.depth_m * 1000, 160,  # 160 mm = IPE160 + tablero
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).translate((-p.width_m * 1000 / 2 + (p.width_m * 1000 / 2),
                 -p.depth_m * 1000 / 2 + (p.depth_m * 1000 / 2),
                 platform_z_mm - 160))
    # Ajustar para que la plataforma comience en x=0, y=0
    plataforma = bd.Box(
        p.width_m * 1000, p.depth_m * 1000, 160,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).translate((0, 0, platform_z_mm - 160))
    return bd.Compound(label="platform", children=[plataforma])


def build_aframe(p: Params, platform_z_mm: float) -> bd.Compound:
    """Pórticos A-frame: rafters + tirantes + cumbrera + correas."""
    n_portals = int(p.raw["aframe"]["portal_count"])
    spacing_m = float(p.raw["aframe"]["portal_spacing_m"])
    width_m = p.width_m
    apex_m = p.apex_height_m
    rafter_len_mm = p.rafter_length_m * 1000

    half_span_mm = width_m * 1000 / 2

    rafter_prof = p.profile(p.raw["aframe"]["rafter_profile"])
    tie_prof = p.profile(p.raw["aframe"]["tie_beam_profile"])
    ridge_prof = p.profile(p.raw["aframe"]["ridge_profile"])
    purlin_prof = p.profile(p.raw["aframe"]["purlin_profile"])

    # Ángulo del rafter respecto al horizontal (en plano frontal XZ)
    angle_deg = degrees(atan2(apex_m, width_m / 2))

    parts: list[bd.Part] = []

    # Posición Y de cada pórtico — empieza a 1 m del frente, termina a 1 m de back
    enclosed_depth_m = float(p.raw["envelope"]["enclosed_depth_m"])
    y_start_m = (p.depth_m - enclosed_depth_m) / 2
    for i in range(n_portals):
        y_m = y_start_m + i * spacing_m
        y_mm = y_m * 1000

        # Rafter izquierdo (de columna izquierda al ápice)
        rafter_l = make_steel_member(p.rafter_length_m, rafter_prof.width_mm, rafter_prof.height_mm)
        rafter_l = rafter_l.rotate(bd.Axis.Y, angle_deg)
        rafter_l = rafter_l.translate((0, y_mm, platform_z_mm))
        parts.append(rafter_l)

        # Rafter derecho (espejado)
        rafter_r = make_steel_member(p.rafter_length_m, rafter_prof.width_mm, rafter_prof.height_mm)
        rafter_r = rafter_r.rotate(bd.Axis.Y, 180 - angle_deg)
        rafter_r = rafter_r.translate((width_m * 1000, y_mm, platform_z_mm))
        parts.append(rafter_r)

        # Tirante (lower tie beam)
        tie = make_steel_member(width_m, tie_prof.width_mm, tie_prof.height_mm)
        tie = tie.translate((0, y_mm, platform_z_mm))
        parts.append(tie)

    # Cumbrera (ridge) — corre a lo largo de los pórticos en el ápice
    ridge_length_m = (n_portals - 1) * spacing_m + 0.4  # con un poco de overhang
    ridge = make_steel_member(ridge_length_m, ridge_prof.width_mm, ridge_prof.height_mm)
    ridge = ridge.rotate(bd.Axis.Z, 90)  # alinear con Y
    ridge = ridge.translate((width_m * 1000 / 2 - ridge_prof.height_mm / 2,
                              y_start_m * 1000 - 200,
                              platform_z_mm + apex_m * 1000))
    parts.append(ridge)

    # Correas (purlins) — distribuidas a lo largo del rafter
    purlin_rows = int(p.raw["aframe"]["purlin_rows_per_side"])
    purlin_length_m = (n_portals - 1) * spacing_m + 0.4
    for side_sign in (-1, 1):  # izquierda y derecha
        for j in range(purlin_rows):
            # Distancia desde la columna hasta el ápice, a lo largo del rafter
            fraction = (j + 0.5) / purlin_rows
            # Punto medio en el plano XZ
            x_mid = half_span_mm - side_sign * (half_span_mm * (1 - fraction))
            z_mid = platform_z_mm + fraction * apex_m * 1000
            purlin = make_steel_member(purlin_length_m, purlin_prof.width_mm, purlin_prof.height_mm)
            purlin = purlin.rotate(bd.Axis.Z, 90)
            purlin = purlin.translate((x_mid - purlin_prof.height_mm / 2,
                                        y_start_m * 1000 - 200,
                                        z_mid))
            parts.append(purlin)

    return bd.Compound(label="aframe", children=parts)


def build_deck_marker(p: Params, platform_z_mm: float) -> bd.Compound:
    """Marcador visual de la terraza frontal — losa thin para distinguirla."""
    enclosed = float(p.raw["envelope"]["enclosed_depth_m"])
    terrace_depth_m = p.terrace_depth_m
    # Terraza al frente (Y bajo)
    deck = bd.Box(
        p.width_m * 1000, terrace_depth_m * 1000, 30,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    ).translate((0, 0, platform_z_mm + 20))  # un poco encima de la plataforma
    return bd.Compound(label="deck", children=[deck])


def build_cabin(p: Params) -> bd.Compound:
    """Assembly raíz."""
    # Z de la plataforma = altura promedio máxima de columnas (top de la columna más alta)
    heights = p.column_heights_m
    max_h_m = max(max(row) for row in heights)
    platform_z_mm = max_h_m * 1000

    columns = build_columns(p)
    platform = build_platform(p, platform_z_mm)
    aframe = build_aframe(p, platform_z_mm)
    deck = build_deck_marker(p, platform_z_mm)

    return bd.Compound(label="cabin", children=[columns, platform, aframe, deck])


def export_all(cabin: bd.Compound) -> dict[str, Path]:
    """Exporta STEP (ingeniero), STL (fabricación), GLB (web)."""
    out: dict[str, Path] = {}

    step_path = EXPORTS_DIR / "cabin.step"
    bd.export_step(cabin, str(step_path))
    out["step"] = step_path

    stl_path = EXPORTS_DIR / "cabin.stl"
    try:
        bd.export_stl(cabin, str(stl_path))
        out["stl"] = stl_path
    except Exception as exc:
        print(f"⚠ STL export falló: {exc}")

    # GLB va a web/data/ para que GitHub Pages lo sirva al HTML interactivo
    glb_path = WEB_DATA_DIR / "cabin.glb"
    try:
        bd.export_gltf(cabin, str(glb_path), binary=True)
        out["glb"] = glb_path
    except Exception as exc:
        print(f"⚠ GLB export falló: {exc}")

    return out


def main() -> None:
    p = load_params()
    print(f"Construyendo cabaña: {p.width_m} × {p.depth_m} m, apex {p.apex_height_m} m...")
    cabin = build_cabin(p)
    out = export_all(cabin)
    for fmt, path in out.items():
        size_kb = path.stat().st_size / 1024
        print(f"  ✅ {fmt.upper():4}  {path.relative_to(EXPORTS_DIR.parent.parent)}  ({size_kb:,.0f} KB)")


if __name__ == "__main__":
    main()
