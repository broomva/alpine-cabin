"""budget_generator.py — Regenera PRESUPUESTO.md desde params + prices + plantilla.

Calcula cantidades del BOM × precios unitarios mid, suma por fase, aplica
indirectos/contingencia/IVA, renderiza la plantilla Jinja2.

Uso: `python cad/budget_generator.py`
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from parameters import load_params, load_prices, PARAMS_PATH, PRICES_PATH
from kpis import all_kpis

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
OUT_PATH = REPO_ROOT / "PRESUPUESTO.md"


@dataclass
class LineItem:
    name: str
    qty: float | int
    unit: str
    unit_price: float

    @property
    def subtotal(self) -> float:
        return self.qty * self.unit_price


# =============================================================================
# Cálculos de cantidades por partida (mapeo BOM → línea de procura)
# =============================================================================

def m1_lines(p, pr) -> list[LineItem]:
    """Fase M1 — Levantamiento + estudios previos."""
    enclosed_area = p.width_m * p.depth_m  # huella total
    return [
        LineItem("Levantamiento topográfico",                1, "servicio", pr.get("m1_studies", "topo_survey")),
        LineItem("Estudio geotécnico",                       1, "servicio", pr.get("m1_studies", "geotech")),
        LineItem("Replanteo + marcación",                    1, "servicio", pr.get("m1_studies", "layout_marking")),
        LineItem("Limpieza + desbroce",                      enclosed_area, "m²", pr.get("m1_studies", "site_clearing")),
        LineItem("Consulta de licencia",                     1, "gestión", pr.get("m1_studies", "permit_initial")),
    ]


def m2_lines(p, pr) -> list[LineItem]:
    """Fase M2 — Ingeniería estructural (honorarios)."""
    return [
        LineItem("Diseño estructural + memoria",   1, "servicio", pr.get("m2_engineering", "structural_design")),
        LineItem("Planos arquitectónicos",         1, "servicio", pr.get("m2_engineering", "architectural_plans")),
        LineItem("Diseño eléctrico",               1, "servicio", pr.get("m2_engineering", "electrical_design")),
        LineItem("Diseño hidrosanitario",          1, "servicio", pr.get("m2_engineering", "plumbing_design")),
        LineItem("Trámite de licencia",            1, "gestión",  pr.get("m2_engineering", "permit_application")),
    ]


def m3_lines(p, pr, k) -> list[LineItem]:
    """Fase M3 — Procura de materiales, derivada de cantidades del BOM."""
    n_cols   = p.column_count
    anchors  = k.anchors
    fab_kg   = k.steel_fabricated_kg
    roof_m2  = k.areas.roof_m2 * 1.10
    enc_m2   = k.areas.enclosed_m2 * 1.10
    deck_m2  = k.areas.terrace_m2 * 1.15
    glaze_m2 = float(p.raw["envelope"]["front_glazing_m2"])
    rear_m2  = float(p.raw["envelope"]["rear_gable_m2"])
    n_anchors_with_margin = int(math.ceil(anchors * 1.15))

    # Tableros OSB: 1.22 × 2.44 = 2.98 m² c/u
    osb_panels  = max(1, int(math.ceil(enc_m2 / 2.98)))
    # Tablones deck: 0.42 m² c/u
    deck_boards = max(1, int(math.ceil(deck_m2 / 0.42)))
    # Railing
    railing_m   = float(p.raw["access"]["railing_perimeter_m"])

    return [
        # Acero
        LineItem("Acero estructural fabricado",        fab_kg,                 "kg",   pr.get("m3_procurement", "steel_fabricated")),
        LineItem("Placas base 250×250×12",             math.ceil(n_cols*1.10), "u",    pr.get("m3_procurement", "base_plate_250x250x12")),
        LineItem("Placas capitel 200×200×10",          math.ceil(n_cols*1.10), "u",    pr.get("m3_procurement", "cap_plate_200x200x10")),
        LineItem("Cartelas / rigidizadores",           math.ceil(n_cols*4*1.10),"u",   pr.get("m3_procurement", "gusset_plate")),
        LineItem("Pernos estructurales M12-M16",       220,                    "u",    pr.get("m3_procurement", "structural_bolt")),
        # Anclaje
        LineItem("Anclajes a roca M16-M20",            n_anchors_with_margin,  "u",    pr.get("m3_procurement", "rock_anchor")),
        LineItem("Epoxi de anclaje químico",           12,                     "u",    pr.get("m3_procurement", "chemical_epoxy_cartridge")),
        LineItem("Grout sin retracción",               2,                      "u",    pr.get("m3_procurement", "non_shrink_grout")),
        LineItem("Tuercas + arandelas",                n_anchors_with_margin,  "juego",pr.get("m3_procurement", "galvanized_nut_washer_set")),
        LineItem("Brocas SDS-max",                     4,                      "u",    pr.get("m3_procurement", "sds_max_bit")),
        # Cubierta
        LineItem("Lámina metálica negra",              roof_m2,                "m²",   pr.get("m3_procurement", "metal_roof_standing_seam")),
        LineItem("Bajo-cubierta impermeable",          roof_m2,                "m²",   pr.get("m3_procurement", "roof_underlayment")),
        LineItem("Aislamiento cubierta PIR",           roof_m2,                "m²",   pr.get("m3_procurement", "roof_insulation_pir")),
        LineItem("Cielo raso machimbre",               roof_m2,                "m²",   pr.get("m3_procurement", "ceiling_machimbre")),
        LineItem("Caballete (ridge)",                  6.2,                    "m",    pr.get("m3_procurement", "ridge_cap")),
        LineItem("Flashing de borde",                  31.8,                   "m",    pr.get("m3_procurement", "rake_flashing")),
        LineItem("Vierteaguas",                        12.4,                   "m",    pr.get("m3_procurement", "drip_edge")),
        LineItem("Tornillos/clips cubierta",           700,                    "u",    pr.get("m3_procurement", "roof_screw_clip")),
        # Piso + deck
        LineItem("Tableros OSB estructural",           osb_panels,             "u",    pr.get("m3_procurement", "osb_panel")),
        LineItem("Aislamiento piso",                   enc_m2,                 "m²",   pr.get("m3_procurement", "floor_insulation")),
        LineItem("Barrera de vapor",                   enc_m2,                 "m²",   pr.get("m3_procurement", "vapor_barrier")),
        LineItem("Acabado piso interior",              enc_m2,                 "m²",   pr.get("m3_procurement", "floor_finish_laminate")),
        LineItem("Tablones deck exterior",             deck_boards,            "u",    pr.get("m3_procurement", "deck_board_treated")),
        LineItem("Tornillos deck",                     800,                    "u",    pr.get("m3_procurement", "deck_screw")),
        LineItem("Aceite/sellador deck",               2,                      "galón",pr.get("m3_procurement", "deck_oil_gallon")),
        # Ventanal + carpintería
        LineItem("Ventanal frontal templado",          glaze_m2,               "m²",   pr.get("m3_procurement", "glass_facade_tempered")),
        LineItem("Puerta corrediza vidrio",            2,                      "u",    pr.get("m3_procurement", "sliding_door_glass")),
        LineItem("Trim madera frontal",                7,                      "m²",   pr.get("m3_procurement", "front_wood_trim")),
        LineItem("Sellos vidriería",                   1,                      "lote", pr.get("m3_procurement", "glazing_sealant_lot")),
        # Muro trasero
        LineItem("Estructura + siding muro trasero",   rear_m2,                "m²",   pr.get("m3_procurement", "rear_wall_structure_siding")),
        LineItem("Aislamiento muro trasero",           rear_m2,                "m²",   pr.get("m3_procurement", "rear_wall_insulation")),
        LineItem("Acabado interior muro",              rear_m2,                "m²",   pr.get("m3_procurement", "rear_wall_interior_finish")),
        LineItem("Ventana/puerta trasera",             1,                      "u",    pr.get("m3_procurement", "rear_window_door")),
        # Barandales + escalera
        LineItem("Barandal terraza",                   railing_m,              "m",    pr.get("m3_procurement", "railing_per_m")),
        LineItem("Escalera lateral",                   1,                      "u",    pr.get("m3_procurement", "lateral_stair")),
        # MEP
        LineItem("Eléctrico rough-in",                 k.areas.enclosed_m2,    "m²",   pr.get("m3_procurement", "electrical_rough_per_m2")),
        LineItem("Hidrosanitario rough-in",            k.areas.enclosed_m2,    "m²",   pr.get("m3_procurement", "plumbing_rough_per_m2")),
        LineItem("Punto cocina",                       1,                      "kit",  pr.get("m3_procurement", "kitchen_point_kit")),
        LineItem("Baño completo",                      1,                      "set",  pr.get("m3_procurement", "bathroom_set")),
        LineItem("Calentador agua",                    1,                      "u",    pr.get("m3_procurement", "water_heater")),
        LineItem("Estufa leña + ducto",                1,                      "u",    pr.get("m3_procurement", "wood_stove_kit")),
        # Impermeabilización
        LineItem("Imprimante epóxico",                 4,                      "galón",pr.get("m3_procurement", "epoxy_primer_gallon")),
        LineItem("Acabado poliuretano",                4,                      "galón",pr.get("m3_procurement", "polyurethane_finish_gallon")),
        LineItem("Protector madera",                   3,                      "galón",pr.get("m3_procurement", "wood_protector_gallon")),
        LineItem("Sellador poliuretano",               20,                     "tubo", pr.get("m3_procurement", "poly_sealant_tube")),
        LineItem("Cinta flashing",                     50,                     "m",    pr.get("m3_procurement", "flashing_tape")),
        LineItem("Drenaje perimetral 4\"",             25,                     "m",    pr.get("m3_procurement", "drainage_pipe_4in")),
        LineItem("Gravilla drenaje",                   2,                      "m³",   pr.get("m3_procurement", "drainage_gravel")),
        LineItem("Geotextil",                          30,                     "m²",   pr.get("m3_procurement", "geotextile")),
        # Consumibles
        LineItem("Hardware/tornillería lote",          1,                      "lote", pr.get("m3_procurement", "hardware_lot")),
        LineItem("Consumibles soldadura",              1,                      "lote", pr.get("m3_procurement", "welding_consumables_lot")),
        LineItem("Discos corte/pulido",                40,                     "u",    pr.get("m3_procurement", "cutting_disc")),
        LineItem("Adhesivo estructural",               15,                     "tubo", pr.get("m3_procurement", "structural_adhesive_tube")),
    ]


def m4_labor_lines(p, pr) -> list[LineItem]:
    """Mano de obra por cuadrilla-día."""
    days = pr.raw["m4_labor_days"]
    name_map = {
        "rock_anchor_crew":        "Cuadrilla anclaje a roca",
        "structural_crew":         "Cuadrilla montaje estructural",
        "envelope_crew":           "Cuadrilla envolvente",
        "finishing_crew":          "Cuadrilla acabados",
        "electrical_crew":         "Cuadrilla eléctrica",
        "plumbing_crew":           "Cuadrilla hidrosanitaria",
        "site_director_half_time": "Dirección residente",
    }
    out: list[LineItem] = []
    for key, label in name_map.items():
        d = days.get(key, 0)
        unit_price = pr.get("m4_labor", key)
        out.append(LineItem(label, d, "día", unit_price))
    return out


def m4_equipment_lines(p, pr) -> list[LineItem]:
    units = pr.raw["m4_equipment_units"]
    name_map = {
        "scaffold_rental_2m":         "Andamio (alquiler 2 meses)",
        "crane_day":                  "Pluma/grúa pequeña",
        "welding_set_rental_1m":      "Equipo soldadura (alquiler)",
        "drill_compressor_rental":    "Taladro + compresor",
        "steel_transport_trip":       "Transporte acero",
        "envelope_transport_trip":    "Transporte envolvente",
        "site_hauling_disposal":      "Acarreo + retiro escombros",
    }
    out: list[LineItem] = []
    for key, label in name_map.items():
        q = units.get(key, 0)
        unit = pr.unit("m4_equipment", key)
        unit_price = pr.get("m4_equipment", key)
        out.append(LineItem(label, q, unit, unit_price))
    return out


# =============================================================================
# Renderer
# =============================================================================

def inputs_hash() -> str:
    """Hash determinístico de params + prices. Reemplaza git_commit que era
    no-determinístico (cambia con cada push aunque los inputs no cambien)."""
    h = hashlib.sha256()
    h.update(PARAMS_PATH.read_bytes())
    h.update(PRICES_PATH.read_bytes())
    return h.hexdigest()[:12]


def fmt_cop(v: float) -> str:
    return f"$ {v:,.0f} COP".replace(",", ".")


def main():
    p = load_params()
    pr = load_prices()
    k = all_kpis(p, pr)

    m1 = m1_lines(p, pr)
    m2 = m2_lines(p, pr)
    m3 = m3_lines(p, pr, k)
    labor = m4_labor_lines(p, pr)
    equip = m4_equipment_lines(p, pr)

    m1_sub = sum(it.subtotal for it in m1)
    m2_sub = sum(it.subtotal for it in m2)
    m3_sub = sum(it.subtotal for it in m3)
    labor_sub = sum(it.subtotal for it in labor)
    equip_sub = sum(it.subtotal for it in equip)
    m4_sub = labor_sub + equip_sub

    direct = m1_sub + m2_sub + m3_sub + m4_sub
    indirect = direct * pr.indirect_pct
    contingency = direct * pr.contingency_pct
    pre_iva = direct + indirect + contingency
    iva = pre_iva * pr.iva_pct
    total = pre_iva + iva

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
        undefined=StrictUndefined,
        trim_blocks=False,
        lstrip_blocks=False,
    )
    tpl = env.get_template("PRESUPUESTO.md.j2")

    md = tpl.render(
        p=p, pr=pr,
        experiment_name=p.raw["experiment"]["name"],
        git_commit=inputs_hash(),
        steel_fabricated_kg=k.steel_fabricated_kg,
        anchors=k.anchors,
        roof_m2=k.areas.roof_m2,
        enclosed_m2=k.areas.enclosed_m2,
        platform_m2=k.areas.platform_m2,
        m1_items=m1, m2_items=m2, m3_items=m3,
        m4_labor=labor, m4_equipment=equip,
        m1_subtotal=m1_sub, m2_subtotal=m2_sub, m3_subtotal=m3_sub,
        m4_labor_subtotal=labor_sub, m4_equipment_subtotal=equip_sub,
        m4_subtotal=m4_sub,
        direct_total=direct,
        indirect=indirect, contingency=contingency,
        pre_iva=pre_iva, iva=iva, total=total,
        fmt=fmt_cop,
    )

    OUT_PATH.write_text(md, encoding="utf-8")
    print(f"✅ PRESUPUESTO regenerado → {OUT_PATH.name} ({len(md):,} bytes)")
    print(f"   Total estimado: {fmt_cop(total)}  (≈ USD {total / pr.usd_cop:,.0f})")


if __name__ == "__main__":
    main()
