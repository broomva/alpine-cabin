"""envelope.py — Modela la envolvente de la cabaña como meshes separados.

Cada componente lleva una etiqueta `cabin/envelope/<tipo>` que viewer.js
detecta para asignar materiales distintos (vidrio, cubierta negra, deck
de madera, muro trasero).

Componentes:
  - Cubierta (2 paneles inclinados, izquierdo y derecho)
  - Gable frontal de vidrio (triángulo en plano YZ)
  - Muro trasero (panel rectangular en plano YZ)
  - Deck de terraza (losa delgada sobre la plataforma)
"""
from __future__ import annotations

from math import atan2, cos, degrees, hypot, sin

import build123d as bd

from parameters import Params


ROOF_THICKNESS_MM   = 60   # bajo-cubierta + aislamiento + lámina
GLASS_THICKNESS_MM  = 12   # vidrio templado + marco
WALL_THICKNESS_MM   = 120  # estructura + aislamiento + acabado
DECK_THICKNESS_MM   = 30


def build_roof_panels(p: Params, platform_z_mm: float) -> bd.Compound:
    """Dos paneles inclinados, uno por agua del A-frame.

    Cada panel cubre la luz del A-frame (rafter_length_m × portal_span + overhang).
    El panel se construye como un Box plano y luego se rota para encajar
    sobre la pendiente del techo.
    """
    width_m = p.width_m
    rafter_length_m = p.rafter_length_m
    apex_m = p.apex_height_m
    angle_deg = degrees(atan2(apex_m, width_m / 2))

    enclosed_depth_m = p.enclosed_depth_m
    overhang_m = float(p.raw["envelope"]["roof_overhang_m"])
    n_portals = int(p.raw["aframe"]["portal_count"])
    spacing_m = float(p.raw["aframe"]["portal_spacing_m"])
    y_start_m = (p.depth_m - enclosed_depth_m) / 2

    panel_length_mm = rafter_length_m * 1000
    panel_depth_mm  = ((n_portals - 1) * spacing_m + 2 * overhang_m) * 1000

    panels: list[bd.Part] = []

    # AGUA IZQUIERDA: panel desde la columna izquierda hacia el ápice, inclinado.
    left_panel = bd.Box(
        panel_length_mm, panel_depth_mm, ROOF_THICKNESS_MM,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    )
    # Rotate convention: same as rafters (M0.3.8 fix) — negative angle = ascend.
    left_panel = left_panel.rotate(bd.Axis.Y, -angle_deg)
    left_panel = left_panel.translate((
        0,
        (y_start_m + (n_portals - 1) * spacing_m / 2) * 1000,
        platform_z_mm,
    ))
    left_panel.label = "cabin/envelope/roof_left"
    panels.append(left_panel)

    # AGUA DERECHA: panel desde la columna derecha hacia el ápice, inclinado al otro lado.
    right_panel = bd.Box(
        panel_length_mm, panel_depth_mm, ROOF_THICKNESS_MM,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    )
    right_panel = right_panel.rotate(bd.Axis.Y, angle_deg - 180)
    right_panel = right_panel.translate((
        width_m * 1000,
        (y_start_m + (n_portals - 1) * spacing_m / 2) * 1000,
        platform_z_mm,
    ))
    right_panel.label = "cabin/envelope/roof_right"
    panels.append(right_panel)

    return bd.Compound(label="cabin/envelope/roof", children=panels)


def build_front_glass(p: Params, platform_z_mm: float) -> bd.Compound:
    """Gable frontal de vidrio: triángulo isósceles en plano XZ ubicado
    al frente de la cabaña (Y mínimo de la zona cerrada).

    Aproximación: prisma triangular con espesor GLASS_THICKNESS_MM
    en dirección Y, área = ½ × width × apex.
    """
    width_m = p.width_m
    apex_m = p.apex_height_m
    y_start_m = (p.depth_m - p.enclosed_depth_m) / 2

    # Construcción del triángulo en plano XZ:
    pts = [(0, 0), (width_m * 1000, 0), (width_m * 1000 / 2, apex_m * 1000)]
    sketch = bd.Polygon(*pts, align=None)
    # Plano XZ (vertical) — extrudimos en dirección Y.
    with bd.BuildPart() as bp:
        with bd.BuildSketch(bd.Plane.XZ) as sk:
            bd.Polygon(*pts, align=None)
        bd.extrude(amount=GLASS_THICKNESS_MM)

    glass = bp.part
    glass = glass.translate((0, y_start_m * 1000, platform_z_mm))
    glass.label = "cabin/envelope/glass_front"

    return bd.Compound(label="cabin/envelope/glass", children=[glass])


def build_rear_wall(p: Params, platform_z_mm: float) -> bd.Compound:
    """Muro trasero: panel triangular sólido (mismo perfil que gable frontal)
    pero en madera tratada. Se coloca al final del volumen cerrado."""
    width_m = p.width_m
    apex_m = p.apex_height_m
    enclosed_depth_m = p.enclosed_depth_m
    y_start_m = (p.depth_m - enclosed_depth_m) / 2
    y_end_m = y_start_m + enclosed_depth_m

    pts = [(0, 0), (width_m * 1000, 0), (width_m * 1000 / 2, apex_m * 1000)]
    with bd.BuildPart() as bp:
        with bd.BuildSketch(bd.Plane.XZ) as sk:
            bd.Polygon(*pts, align=None)
        bd.extrude(amount=WALL_THICKNESS_MM)

    wall = bp.part
    # Posición: justo después del último pórtico, espesor extiende hacia atrás
    wall = wall.translate((0, (y_end_m - WALL_THICKNESS_MM / 1000) * 1000, platform_z_mm))
    wall.label = "cabin/envelope/rear_wall"

    return bd.Compound(label="cabin/envelope/rear_wall", children=[wall])


def build_deck(p: Params, platform_z_mm: float) -> bd.Compound:
    """Losa delgada de madera tratada sobre la terraza (frente de la plataforma)."""
    width_m = p.width_m
    terrace_depth_m = p.terrace_depth_m
    y_start_m = (p.depth_m - p.enclosed_depth_m) / 2  # comienzo de zona cerrada
    # La terraza es la franja entre el frente de la plataforma (Y=0) y y_start_m

    deck = bd.Box(
        width_m * 1000, y_start_m * 1000, DECK_THICKNESS_MM,
        align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN),
    )
    deck = deck.translate((0, 0, platform_z_mm + 30))  # justo sobre la plataforma
    deck.label = "cabin/envelope/deck"
    return bd.Compound(label="cabin/envelope/deck", children=[deck])


def build_envelope(p: Params, platform_z_mm: float) -> bd.Compound:
    """Assembly raíz de envolvente: cubierta + gable + muro trasero + deck."""
    parts: list[bd.Compound] = []
    parts.append(build_roof_panels(p, platform_z_mm))
    parts.append(build_front_glass(p, platform_z_mm))
    parts.append(build_rear_wall(p, platform_z_mm))
    parts.append(build_deck(p, platform_z_mm))
    return bd.Compound(label="cabin/envelope", children=parts)
