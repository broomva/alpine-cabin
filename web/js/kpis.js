// kpis.js — Cálculo de KPIs en el browser.
// Mirror de cad/kpis.py. Mantener consistencia: si cambias una fórmula aquí,
// cámbiala allá y corre el test de consistencia.

const FAB_UPLIFT = 1.125;

function profile(params, name) {
  const p = params.profiles?.[name];
  if (!p) throw new Error(`perfil desconocido: ${name}`);
  return p;
}

function rafterLengthM(params) {
  const halfSpan = params.platform.width_m / 2;
  const apex = params.aframe.apex_height_m;
  return Math.hypot(halfSpan, apex);
}

function columnCount(params) {
  return params.platform.column_grid_cols * params.platform.column_grid_rows;
}

function totalColumnLengthM(params) {
  return params.columns.heights_m.flat().reduce((a, b) => a + b, 0);
}

function steelLengths(params) {
  const w = params.platform.width_m;
  const d = params.platform.depth_m;
  const cols = params.platform.column_grid_cols;
  const rows = params.platform.column_grid_rows;

  const columns = totalColumnLengthM(params);
  const main_beams = rows * w + cols * d;
  const joistSpacing = params.platform_structure.joist_spacing_m;
  const joistCount = Math.max(2, Math.round(d / joistSpacing) + 1);
  const secondary_joists = joistCount * w;
  const bracing = 24.0;

  const nPortals = params.aframe.portal_count;
  const rafLen = rafterLengthM(params);
  const enclosed = params.envelope.enclosed_depth_m;
  const rafters = nPortals * 2 * rafLen;
  const tie_beams = nPortals * w;
  const ridge = enclosed + 0.4;
  const purlinRows = params.aframe.purlin_rows_per_side;
  const purlins = purlinRows * 2 * (enclosed + 0.4);

  const total = columns + main_beams + secondary_joists + bracing + rafters + tie_beams + ridge + purlins;
  return { columns, main_beams, secondary_joists, bracing, rafters, tie_beams, ridge, purlins, total };
}

function steelWeightKg(params, lengths) {
  return (
    lengths.columns          * profile(params, params.columns.profile).kg_per_m
    + lengths.main_beams       * profile(params, params.platform_structure.main_beam_profile).kg_per_m
    + lengths.secondary_joists * profile(params, params.platform_structure.secondary_joist_profile).kg_per_m
    + lengths.bracing          * profile(params, params.platform_structure.bracing_profile).kg_per_m
    + lengths.rafters          * profile(params, params.aframe.rafter_profile).kg_per_m
    + lengths.tie_beams        * profile(params, params.aframe.tie_beam_profile).kg_per_m
    + lengths.ridge            * profile(params, params.aframe.ridge_profile).kg_per_m
    + lengths.purlins          * profile(params, params.aframe.purlin_profile).kg_per_m
  );
}

function areas(params) {
  const enclosed = params.platform.width_m * params.envelope.enclosed_depth_m;
  const terrace = params.platform.width_m * params.envelope.terrace_depth_m;
  const platform = enclosed + terrace;
  const overhang = params.envelope.roof_overhang_m;
  const roof = 2 * rafterLengthM(params) * (params.envelope.enclosed_depth_m + 2 * overhang);
  return { enclosed_m2: enclosed, terrace_m2: terrace, platform_m2: platform, roof_m2: roof };
}

function costs(params, prices, areas) {
  // Anchor temporal — coincide con el cálculo de Python en M0.3.2.
  // En M0.3.3.1 se sustituye por una suma item-by-item ligada al BOM.
  const directCop = 218322300;

  const indirect = directCop * prices.overhead.indirect_pct;
  const contingency = directCop * prices.overhead.contingency_pct;
  const preIva = directCop + indirect + contingency;
  const iva = preIva * prices.overhead.iva_pct;
  const total = preIva + iva;
  const usd = total / prices.exchange_rate_usd_cop;
  return {
    direct_cop: directCop,
    indirect_cop: indirect,
    contingency_cop: contingency,
    pre_iva_cop: preIva,
    iva_cop: iva,
    total_cop: total,
    total_usd: usd,
    per_m2_enclosed_cop: total / areas.enclosed_m2,
  };
}

export function computeKpis(params, prices) {
  const lengths = steelLengths(params);
  const rawKg = steelWeightKg(params, lengths);
  const fabKg = rawKg * FAB_UPLIFT;
  const a = areas(params);
  const c = costs(params, prices, a);
  return {
    steel_lengths: lengths,
    steel_raw_kg: rawKg,
    steel_fabricated_kg: fabKg,
    anchors: columnCount(params) * params.columns.anchors_per_column,
    areas: a,
    cost: c,
    rafter_length_m: rafterLengthM(params),
  };
}

// ---------- Render helpers ----------

const fmtCOP = new Intl.NumberFormat("es-CO", { maximumFractionDigits: 0 });
const fmtUSD = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });

function row(label, value, dirty = false) {
  return `<div class="kpi-row"><span class="kpi-label">${label}</span><span class="kpi-value ${dirty ? "dirty" : ""}">${value}</span></div>`;
}

function group(name) {
  return `<div class="kpi-group">${name}</div>`;
}

export function renderKpis(container, k, baseline) {
  const dirty = (curr, base) => Math.abs(curr - base) / Math.max(Math.abs(base), 1) > 0.001;

  const sl = k.steel_lengths;
  const slb = baseline.steel_lengths;
  const a = k.areas;
  const ab = baseline.areas;
  const c = k.cost;
  const cb = baseline.cost;

  container.innerHTML = [
    group("Geometría"),
    row("Plataforma",     `${a.platform_m2.toFixed(1)} m²`,  dirty(a.platform_m2, ab.platform_m2)),
    row("Cabaña cerrada", `${a.enclosed_m2.toFixed(1)} m²`,  dirty(a.enclosed_m2, ab.enclosed_m2)),
    row("Terraza",        `${a.terrace_m2.toFixed(1)} m²`,   dirty(a.terrace_m2,  ab.terrace_m2)),
    row("Cubierta",       `${a.roof_m2.toFixed(1)} m²`,      dirty(a.roof_m2,     ab.roof_m2)),
    row("Rafter",         `${k.rafter_length_m.toFixed(3)} m`, dirty(k.rafter_length_m, baseline.rafter_length_m)),

    group("Acero"),
    row("Longitud total", `${sl.total.toFixed(1)} m`, dirty(sl.total, slb.total)),
    row("Peso crudo",     `${k.steel_raw_kg.toFixed(0)} kg`, dirty(k.steel_raw_kg, baseline.steel_raw_kg)),
    row("Peso fabricado", `${k.steel_fabricated_kg.toFixed(0)} kg`, dirty(k.steel_fabricated_kg, baseline.steel_fabricated_kg)),
    row("≈ toneladas",    `${(k.steel_fabricated_kg / 1000).toFixed(2)} t`, dirty(k.steel_fabricated_kg, baseline.steel_fabricated_kg)),

    group("Anclajes"),
    row("Anclajes a roca", `${k.anchors} u`, dirty(k.anchors, baseline.anchors)),

    group("Costo (mid)"),
    row("Directo",      `$ ${fmtCOP.format(c.direct_cop)} COP`, dirty(c.direct_cop, cb.direct_cop)),
    row("Indirectos",   `$ ${fmtCOP.format(c.indirect_cop)} COP`, dirty(c.indirect_cop, cb.indirect_cop)),
    row("Contingencia", `$ ${fmtCOP.format(c.contingency_cop)} COP`, dirty(c.contingency_cop, cb.contingency_cop)),
    row("IVA 19%",      `$ ${fmtCOP.format(c.iva_cop)} COP`, dirty(c.iva_cop, cb.iva_cop)),
    row("TOTAL",        `$ ${fmtCOP.format(c.total_cop)} COP`, dirty(c.total_cop, cb.total_cop)),
    row("≈ USD",        `${fmtUSD.format(c.total_usd)} USD`, dirty(c.total_usd, cb.total_usd)),
    row("Por m² cabaña",`$ ${fmtCOP.format(c.per_m2_enclosed_cop)} COP`, dirty(c.per_m2_enclosed_cop, cb.per_m2_enclosed_cop)),
  ].join("");
}
