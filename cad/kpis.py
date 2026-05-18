"""KPIs centralizados del proyecto.

Mirror en `web/js/kpis.js` — modificar ambos cuando cambies una fórmula.
Test de consistencia en `tests/test_kpis_consistency.py` (TODO).
"""
from __future__ import annotations

from dataclasses import dataclass
from math import hypot

from parameters import Params, Prices, load_params, load_prices


@dataclass(frozen=True)
class SteelLengths:
    """Longitudes totales por categoría, sin desperdicio (en metros)."""
    columns: float
    main_beams: float
    secondary_joists: float
    bracing: float
    rafters: float
    tie_beams: float
    ridge: float
    purlins: float

    @property
    def total(self) -> float:
        return (self.columns + self.main_beams + self.secondary_joists
                + self.bracing + self.rafters + self.tie_beams
                + self.ridge + self.purlins)


def steel_lengths(p: Params) -> SteelLengths:
    """Longitudes de acero antes de desperdicio."""
    width = p.width_m
    depth = p.depth_m
    cols = int(p.raw["platform"]["column_grid_cols"])
    rows = int(p.raw["platform"]["column_grid_rows"])

    columns = p.total_column_length_m
    main_beams = rows * width + cols * depth
    secondary_spacing = float(p.raw["platform_structure"]["joist_spacing_m"])
    joist_count = max(2, int(round(depth / secondary_spacing)) + 1)
    secondary_joists = joist_count * width
    bracing = 24.0  # estimación X-bracing entre postes (mejorable)

    n_portals = int(p.raw["aframe"]["portal_count"])
    rafter_len = p.rafter_length_m
    enclosed = p.enclosed_depth_m
    rafters = n_portals * 2 * rafter_len
    tie_beams = n_portals * width
    ridge = enclosed + 0.4  # con overhang
    purlin_rows = int(p.raw["aframe"]["purlin_rows_per_side"])
    purlins = purlin_rows * 2 * (enclosed + 0.4)

    return SteelLengths(
        columns=columns,
        main_beams=main_beams,
        secondary_joists=secondary_joists,
        bracing=bracing,
        rafters=rafters,
        tie_beams=tie_beams,
        ridge=ridge,
        purlins=purlins,
    )


def steel_weight_kg(p: Params, lengths: SteelLengths) -> float:
    return (
        lengths.columns          * p.profile(p.raw["columns"]["profile"]).kg_per_m
        + lengths.main_beams       * p.profile(p.raw["platform_structure"]["main_beam_profile"]).kg_per_m
        + lengths.secondary_joists * p.profile(p.raw["platform_structure"]["secondary_joist_profile"]).kg_per_m
        + lengths.bracing          * p.profile(p.raw["platform_structure"]["bracing_profile"]).kg_per_m
        + lengths.rafters          * p.profile(p.raw["aframe"]["rafter_profile"]).kg_per_m
        + lengths.tie_beams        * p.profile(p.raw["aframe"]["tie_beam_profile"]).kg_per_m
        + lengths.ridge            * p.profile(p.raw["aframe"]["ridge_profile"]).kg_per_m
        + lengths.purlins          * p.profile(p.raw["aframe"]["purlin_profile"]).kg_per_m
    )


def fabricated_steel_kg(raw_kg: float, fabrication_uplift: float = 1.125) -> float:
    """Acero crudo + 12.5% (promedio del rango 10–15%) por placas, soldadura,
    pernos y margen de fabricación."""
    return raw_kg * fabrication_uplift


@dataclass(frozen=True)
class AreaKPIs:
    enclosed_m2: float
    terrace_m2: float
    platform_m2: float
    roof_m2: float


def areas(p: Params) -> AreaKPIs:
    enclosed = p.width_m * p.enclosed_depth_m
    terrace = p.width_m * p.terrace_depth_m
    platform = enclosed + terrace
    overhang = float(p.raw["envelope"]["roof_overhang_m"])
    roof = 2 * p.rafter_length_m * (p.enclosed_depth_m + 2 * overhang)
    return AreaKPIs(enclosed_m2=enclosed, terrace_m2=terrace,
                    platform_m2=platform, roof_m2=roof)


@dataclass(frozen=True)
class CostKPIs:
    direct_cop: float
    indirect_cop: float
    contingency_cop: float
    pre_iva_cop: float
    iva_cop: float
    total_cop: float
    total_usd: float
    per_m2_enclosed_cop: float


def costs(p: Params, pr: Prices) -> CostKPIs:
    """Costo total estimado usando precios mid de prices.toml.

    Implementación M0.3.2 — simplificada. Itera el BOM completo en M0.3.3.
    Para este snapshot inicial uso el total mid del PRESUPUESTO.md manual
    (≈ $218.3 M directos) como anchor y aplicaré indirectos/contingencia/IVA
    desde prices.toml. Los generators de M0.3.3 producirán el cálculo
    detallado partida por partida.
    """
    # Anchor temporal — reemplazar en M0.3.3 con suma detallada del BOM.
    direct_cop = 218_322_300

    indirect = direct_cop * pr.indirect_pct
    contingency = direct_cop * pr.contingency_pct
    pre_iva = direct_cop + indirect + contingency
    iva = pre_iva * pr.iva_pct
    total = pre_iva + iva
    a = areas(p)

    return CostKPIs(
        direct_cop=direct_cop,
        indirect_cop=indirect,
        contingency_cop=contingency,
        pre_iva_cop=pre_iva,
        iva_cop=iva,
        total_cop=total,
        total_usd=total / pr.usd_cop,
        per_m2_enclosed_cop=total / a.enclosed_m2,
    )


@dataclass(frozen=True)
class AllKPIs:
    steel_lengths: SteelLengths
    steel_raw_kg: float
    steel_fabricated_kg: float
    anchors: int
    areas: AreaKPIs
    cost: CostKPIs


def all_kpis(p: Params, pr: Prices) -> AllKPIs:
    sl = steel_lengths(p)
    raw_kg = steel_weight_kg(p, sl)
    fab_kg = fabricated_steel_kg(raw_kg)
    return AllKPIs(
        steel_lengths=sl,
        steel_raw_kg=raw_kg,
        steel_fabricated_kg=fab_kg,
        anchors=p.anchor_count,
        areas=areas(p),
        cost=costs(p, pr),
    )


if __name__ == "__main__":
    p = load_params()
    pr = load_prices()
    k = all_kpis(p, pr)

    print("== Acero ==")
    print(f"  Longitud cruda total:    {k.steel_lengths.total:>8.1f} m")
    print(f"    columnas:              {k.steel_lengths.columns:>8.1f} m")
    print(f"    vigas principales:     {k.steel_lengths.main_beams:>8.1f} m")
    print(f"    viguetas:              {k.steel_lengths.secondary_joists:>8.1f} m")
    print(f"    arriostramiento:       {k.steel_lengths.bracing:>8.1f} m")
    print(f"    pares A-frame:         {k.steel_lengths.rafters:>8.1f} m")
    print(f"    tirantes:              {k.steel_lengths.tie_beams:>8.1f} m")
    print(f"    cumbrera:              {k.steel_lengths.ridge:>8.1f} m")
    print(f"    correas:               {k.steel_lengths.purlins:>8.1f} m")
    print(f"  Peso crudo:              {k.steel_raw_kg:>8.0f} kg")
    print(f"  Peso fabricado (×1.125): {k.steel_fabricated_kg:>8.0f} kg")

    print("\n== Áreas ==")
    print(f"  Cabaña cerrada:      {k.areas.enclosed_m2:>6.1f} m²")
    print(f"  Terraza:             {k.areas.terrace_m2:>6.1f} m²")
    print(f"  Plataforma total:    {k.areas.platform_m2:>6.1f} m²")
    print(f"  Cubierta:            {k.areas.roof_m2:>6.1f} m²")

    print(f"\n== Anclajes ==  {k.anchors}")

    print("\n== Costo ==")
    print(f"  Directo:        $ {k.cost.direct_cop:>14,.0f} COP")
    print(f"  Indirecto:      $ {k.cost.indirect_cop:>14,.0f} COP")
    print(f"  Contingencia:   $ {k.cost.contingency_cop:>14,.0f} COP")
    print(f"  Subtotal:       $ {k.cost.pre_iva_cop:>14,.0f} COP")
    print(f"  IVA 19%:        $ {k.cost.iva_cop:>14,.0f} COP")
    print(f"  TOTAL:          $ {k.cost.total_cop:>14,.0f} COP  (≈ USD {k.cost.total_usd:,.0f})")
    print(f"  Por m² cabaña:  $ {k.cost.per_m2_enclosed_cop:>14,.0f} COP")
