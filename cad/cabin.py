"""cabin.py — Modelo CAD paramétrico de la cabaña usando build123d.

Genera la geometría completa (columnas, plataforma, A-frame, correas, cumbrera)
a partir de los parámetros de params.toml. Exporta STEP, STL y GLTF.

Uso: `python cad/cabin.py` (genera cad/exports/cabin.{step,stl,glb,png}).
"""
from __future__ import annotations

import random
from math import atan2, degrees
from pathlib import Path

import build123d as bd

from parameters import Params, load_params
from envelope import build_envelope

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

    Convención de alineación:
      - X = MIN (origen en el extremo izquierdo, longitud extiende a +X)
      - Y = CENTER (perfil simétrico horizontal)
      - Z = MIN (apoya en z=0, espesor extiende a +Z)
    Esto hace que las rotaciones alrededor de Y o Z pivoteen sobre la
    cara inferior del miembro, no su centro (fix M0.3.8 BRO-1177).
    """
    L = length_m * 1000  # mm en build123d
    w = profile_width_mm
    h = profile_height_mm
    return bd.Box(L, w, h, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN))


def build_columns(p: Params) -> bd.Compound:
    """9 columnas en malla 3 × 3, alturas variables por roca.

    Cada columna se ancla con su BASE sobre el terreno (z variable) y su TOPE
    en `platform_z_mm` (constante = max altura). El terreno sube para llenar
    el espacio bajo las columnas cortas; las columnas largas pisan piso bajo.
    """
    prof = p.profile(p.raw["columns"]["profile"])
    cols_n = int(p.raw["platform"]["column_grid_cols"])
    rows_n = int(p.raw["platform"]["column_grid_rows"])
    width_m = p.width_m
    depth_m = p.depth_m
    heights = p.column_heights_m
    max_h_m = max(max(row) for row in heights)

    parts: list[bd.Part] = []
    for row in range(rows_n):
        for col in range(cols_n):
            x = (col / (cols_n - 1)) * width_m * 1000 if cols_n > 1 else 0
            y = (row / (rows_n - 1)) * depth_m * 1000 if rows_n > 1 else 0
            h_m = heights[row][col]
            # Top de columna alineado a platform_z; base sube en columnas cortas.
            z_bottom_mm = (max_h_m - h_m) * 1000
            col_part = bd.Box(
                prof.width_mm, prof.height_mm, h_m * 1000,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
            )
            col_part = col_part.translate((x, y, z_bottom_mm))
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

        # Rafter izquierdo: de columna izquierda al ápice (sube hacia +Z).
        # En build123d (Z-up), rotar +X por -angle_deg alrededor de +Y manda
        # el extremo a (cos·L, 0, +sin·L) — ascendente. El signo positivo
        # mandaría a -Z (descendente), bug detectado en M0.3.8.
        rafter_l = make_steel_member(p.rafter_length_m, rafter_prof.width_mm, rafter_prof.height_mm)
        rafter_l = rafter_l.rotate(bd.Axis.Y, -angle_deg)
        rafter_l = rafter_l.translate((0, y_mm, platform_z_mm))
        parts.append(rafter_l)

        # Rafter derecho: espejo del izquierdo, también ascendente.
        # Rotación -(180 - angle_deg) = angle_deg - 180. Esto manda +X a
        # (-cos·L, 0, +sin·L) — apex hacia el centro y arriba.
        rafter_r = make_steel_member(p.rafter_length_m, rafter_prof.width_mm, rafter_prof.height_mm)
        rafter_r = rafter_r.rotate(bd.Axis.Y, angle_deg - 180)
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


def build_terrain(p: Params) -> bd.Compound:
    """Loza sólida del terreno inclinado.

    La cara superior pasa por las bases de las columnas. La pendiente va desde
    `z = (max_h - h_back) * 1000` en y=0 hasta `z = (max_h - h_front) * 1000`
    en y=depth_m, extrapolada linealmente más allá del footprint.
    """
    heights = p.column_heights_m
    max_h = max(max(r) for r in heights)
    rows_n = len(heights)
    h_back  = heights[0][0]
    h_front = heights[rows_n - 1][0]
    back_z_mm  = (max_h - h_back)  * 1000.0
    front_z_mm = (max_h - h_front) * 1000.0
    depth_mm = p.depth_m * 1000.0
    width_mm = p.width_m * 1000.0
    slope = (front_z_mm - back_z_mm) / depth_mm if depth_mm > 0 else 0.0

    margin_y_mm = 3500.0
    margin_x_mm = 4000.0
    thickness_mm = 1500.0

    y_back  = -margin_y_mm
    y_front = depth_mm + margin_y_mm
    z_top_back  = back_z_mm + slope * (y_back  - 0.0)
    z_top_front = back_z_mm + slope * (y_front - 0.0)
    z_bottom = min(z_top_back, z_top_front) - thickness_mm

    # Polígono en YZ (counterclockwise desde +X): top-back → top-front → bot-front → bot-back.
    pts_yz = [
        (y_back,  z_top_back),
        (y_front, z_top_front),
        (y_front, z_bottom),
        (y_back,  z_bottom),
    ]
    extrude_x = width_mm + 2 * margin_x_mm
    with bd.BuildPart() as bp:
        with bd.BuildSketch(bd.Plane.YZ):
            bd.Polygon(*pts_yz, align=None)
        bd.extrude(amount=extrude_x)

    terrain = bp.part
    # extrude empuja en +X normal al plano YZ; centramos sobre el ancho.
    terrain = terrain.translate((-margin_x_mm, 0, 0))
    terrain.label = "cabin/terrain"
    return bd.Compound(label="cabin/terrain", children=[terrain])


def build_rocks(p: Params) -> bd.Compound:
    """Cúmulos rocosos en la base de cada columna.

    Cada columna lleva un cluster de 4 boulders angulares (Box rotados) enterrados
    en el terreno, justificando visualmente la altura variable de las columnas:
    las columnas cortas pisan rocas más grandes (terreno elevado), las largas
    pisan rocas pequeñas. Mismo principio que la foto de referencia.

    Usamos Box rotados en vez de Sphere porque OCCT tessela esferas con ~8k
    triángulos por defecto, y 36 esferas hacen un GLB de ~5MB; con Box el GLB
    queda en ~200KB con calidad visual equivalente a esta escala/iluminación.
    """
    rng = random.Random(42)  # determinístico por estabilidad del GLB
    cols_n = int(p.raw["platform"]["column_grid_cols"])
    rows_n = int(p.raw["platform"]["column_grid_rows"])
    heights = p.column_heights_m
    max_h = max(max(r) for r in heights)
    width_m = p.width_m
    depth_m = p.depth_m

    def boulder(size_mm: float) -> bd.Part:
        # Box ligeramente irregular + 3 rotaciones aleatorias = look facetado tipo roca.
        sx = size_mm * rng.uniform(0.85, 1.25)
        sy = size_mm * rng.uniform(0.85, 1.25)
        sz = size_mm * rng.uniform(0.6, 1.05)  # más bajo que ancho (boulders aplastados)
        b = bd.Box(sx, sy, sz, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
        b = b.rotate(bd.Axis.X, rng.uniform(-25, 25))
        b = b.rotate(bd.Axis.Y, rng.uniform(-25, 25))
        b = b.rotate(bd.Axis.Z, rng.uniform(0, 360))
        return b

    parts: list[bd.Part] = []
    for row in range(rows_n):
        for col in range(cols_n):
            x = (col / (cols_n - 1)) * width_m * 1000 if cols_n > 1 else 0
            y = (row / (rows_n - 1)) * depth_m * 1000 if rows_n > 1 else 0
            h_m = heights[row][col]
            z_base = (max_h - h_m) * 1000.0  # nivel del terreno bajo esta columna

            # Roca central grande bajo la columna — más alta donde la columna es más corta.
            r0 = 760.0 + (1.8 - h_m) * 300.0  # 760mm (h=1.8) hasta 1120mm (h=0.6)
            rock0 = boulder(r0)
            rock0 = rock0.translate((x, y, z_base - r0 * 0.2))
            parts.append(rock0)

            # 3 boulders satélite alrededor.
            for _ in range(3):
                rx = rng.uniform(-650, 650)
                ry = rng.uniform(-650, 650)
                size = rng.uniform(380, 620)
                rock = boulder(size)
                rz = z_base - size * 0.2 + rng.uniform(-30, 80)
                rock = rock.translate((x + rx, y + ry, rz))
                parts.append(rock)

    return bd.Compound(label="cabin/rocks", children=parts)


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
    envelope = build_envelope(p, platform_z_mm)
    terrain = build_terrain(p)
    rocks = build_rocks(p)

    # Etiquetas para que viewer.js detecte tipo de superficie.
    columns.label = "cabin/columns"
    platform.label = "cabin/platform"
    aframe.label = "cabin/aframe"
    terrain.label = "cabin/terrain"
    rocks.label = "cabin/rocks"

    return bd.Compound(
        label="cabin",
        children=[terrain, rocks, columns, platform, aframe, envelope],
    )


def export_all(cabin: bd.Compound, envelope_only: bd.Compound | None = None) -> dict[str, Path]:
    """Exporta STEP (ingeniero), STL (fabricación), GLB (web).

    Si `envelope_only` se provee, también exporta `cabin_envelope.glb` —
    versión sin terreno ni rocas, usada por validate_cad.py para checks de
    dimensiones (que de otra forma estarían dominadas por los márgenes del
    terreno).
    """
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

    # GLB va a web/data/ para que GitHub Pages lo sirva al HTML interactivo.
    # Bajamos la fidelidad de teselado para terreno + rocas (sphere/extrude pesado)
    # — el tamaño cae de ~6.7MB a ~1MB sin pérdida visible en el viewer.
    glb_path = WEB_DATA_DIR / "cabin.glb"
    try:
        bd.export_gltf(
            cabin, str(glb_path), binary=True,
            linear_deflection=0.05, angular_deflection=0.8,
        )
        out["glb"] = glb_path
    except Exception as exc:
        print(f"⚠ GLB export falló: {exc}")

    if envelope_only is not None:
        env_path = WEB_DATA_DIR / "cabin_envelope.glb"
        try:
            bd.export_gltf(envelope_only, str(env_path), binary=True)
            out["envelope_glb"] = env_path
        except Exception as exc:
            print(f"⚠ envelope GLB export falló: {exc}")

    return out


def main() -> None:
    p = load_params()
    print(f"Construyendo cabaña: {p.width_m} × {p.depth_m} m, apex {p.apex_height_m} m...")
    cabin = build_cabin(p)

    # Sub-compound sin terreno/rocas — para regression tests de dimensiones.
    # Importante: build123d re-parenta hijos asignados a otro Compound. Para no
    # robarle hijos a `cabin`, construimos el envelope-only PARALELAMENTE
    # (sin reusar nodos). Como las funciones build_*() son determinísticas,
    # llamarlas otra vez produce idénticos sólidos.
    columns = build_columns(p)
    heights = p.column_heights_m
    platform_z_mm = max(max(row) for row in heights) * 1000.0
    platform = build_platform(p, platform_z_mm)
    aframe = build_aframe(p, platform_z_mm)
    envelope = build_envelope(p, platform_z_mm)
    columns.label = "cabin/columns"
    platform.label = "cabin/platform"
    aframe.label = "cabin/aframe"
    envelope_only = bd.Compound(
        label="cabin_envelope",
        children=[columns, platform, aframe, envelope],
    )

    out = export_all(cabin, envelope_only=envelope_only)
    for fmt, path in out.items():
        size_kb = path.stat().st_size / 1024
        print(f"  ✅ {fmt.upper():4}  {path.relative_to(EXPORTS_DIR.parent.parent)}  ({size_kb:,.0f} KB)")


if __name__ == "__main__":
    main()
