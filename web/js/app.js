// app.js — Controller principal del digital twin.

import { mountViewer } from "./viewer.js";
import { mountSliders } from "./ui.js";
import { renderKpis, computeKpis } from "./kpis.js";
import { loadExperimentFromHash, saveExperimentToHash, downloadExperiment, copyExperimentUrl } from "./state.js";
import { initTabs, onTabChange, currentTab } from "./tabs.js";
import {
  initProgress, getState as getProgressState, onChange as onProgressChange,
  toggleSubstep, markPhaseDone, reopenPhase, setNote,
  phaseProgressFraction, overallProgress, nextPhase,
  exportJson as exportProgressJson, importJson as importProgressJson, resetAll as resetProgress,
} from "./progress.js";

const DATA_BASE = "data";

async function fetchJson(name) {
  const res = await fetch(`${DATA_BASE}/${name}`);
  if (!res.ok) throw new Error(`No pude cargar ${name}: ${res.status}`);
  return res.json();
}

// ============================================================
// Globals
// ============================================================

let params, prices, baselineKpis, phasesData;
let liveParams;
let baseline;

// ============================================================
// Boot
// ============================================================

async function main() {
  // Cargar TODO en paralelo
  [params, prices, baselineKpis, phasesData] = await Promise.all([
    fetchJson("params.json"),
    fetchJson("prices.json"),
    fetchJson("kpis.json"),
    fetchJson("construction-phases.json"),
  ]);

  baseline = structuredClone(params);
  liveParams = structuredClone(params);

  const fromHash = loadExperimentFromHash();
  if (fromHash) Object.assign(liveParams, fromHash);

  await initProgress(phasesData);
  initTabs();

  // Inicialmente solo el viewer del Overview existe y se monta tarde
  // El viewer-full se monta lazy cuando se entra a la tab "3D"
  await mountViewer(document.getElementById("viewer"), `${DATA_BASE}/cabin.glb`, () => {
    const status = document.getElementById("viewer-status");
    if (status) status.textContent = "Modelo listo · arrastra para rotar";
  });

  // Sliders en la tab Parámetros
  mountSliders(document.getElementById("sliders"), liveParams, baseline, onSliderChange);

  // KPIs iniciales
  updateAllKpis();

  // Construir tab — render de las 8 fases
  renderPhases();

  // Progreso tab — render del avance
  renderProgressTab();
  onProgressChange(() => {
    renderProgressTab();
    refreshPhaseContent();
    updateConstruirBadge();
  });
  updateConstruirBadge();

  // BOM + Presupuesto tabs
  renderBomTable();
  renderBudgetTab();

  // Action bindings
  bindActions();

  // Tab change side-effects
  onTabChange((tab) => {
    if (tab === "cad3d") ensureFullViewerMounted();
  });
}

// ============================================================
// KPIs
// ============================================================

function updateAllKpis() {
  const k = computeKpis(liveParams, prices);
  const base = computeKpis(baseline, prices);
  for (const id of ["kpi-list", "kpi-list-params"]) {
    const el = document.getElementById(id);
    if (el) renderKpis(el, k, base);
  }
  saveExperimentToHash(liveParams, baseline);
}

function onSliderChange(path, value) {
  setByPath(liveParams, path, value);
  updateAllKpis();
}

function setByPath(obj, path, value) {
  const parts = path.split(".");
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) cur = cur[parts[i]];
  cur[parts[parts.length - 1]] = value;
}

// ============================================================
// Phases (Construir tab)
// ============================================================

let activePhaseIdx = 0;

function renderPhases() {
  const sidebar = document.getElementById("phases-sidebar");
  if (!sidebar) return;
  sidebar.innerHTML = phasesData.phases.map((ph, i) => {
    const f = phaseProgressFraction(ph.id);
    const done = f >= 1;
    return `
      <button class="phase-btn ${done ? "done" : ""} ${i === activePhaseIdx ? "active" : ""}"
              data-idx="${i}">
        <span class="num"><span>${ph.number}</span></span>
        <span>${ph.name}</span>
      </button>
    `;
  }).join("");

  sidebar.querySelectorAll(".phase-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      activePhaseIdx = parseInt(btn.dataset.idx, 10);
      renderPhases();
      refreshPhaseContent();
    });
  });

  refreshPhaseContent();
}

function refreshPhaseContent() {
  const phase = phasesData.phases[activePhaseIdx];
  const container = document.getElementById("phase-content");
  if (!phase || !container) return;

  const progressState = getProgressState();
  const phaseState = progressState.phases[phase.id] || { substeps: {}, notes: "" };
  const completedCount = Object.keys(phaseState.substeps).length;

  container.innerHTML = `
    <header>
      <div style="display: flex; gap: 1rem; align-items: baseline; justify-content: space-between; flex-wrap: wrap">
        <div>
          <span style="font-family: var(--font-mono); font-size: 0.78rem; color: var(--ai-blue); text-transform: uppercase; letter-spacing: 0.1em">Fase ${phase.number} de ${phasesData.phases.length}</span>
          <h3>${phase.name}</h3>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: var(--text-mid)">
          <span class="mono">${completedCount} / ${phase.substeps.length}</span>
          <div style="width: 120px"><div class="progress-bar"><div class="fill" style="width: ${(completedCount / phase.substeps.length * 100).toFixed(0)}%"></div></div></div>
        </div>
      </div>
      <p class="phase-intro">${phase.intro}</p>
    </header>

    <section class="phase-meta">
      <div class="phase-meta-item"><span class="label">Duración</span><span class="value">${phase.duration_days} día${phase.duration_days > 1 ? "s" : ""}</span></div>
      <div class="phase-meta-item"><span class="label">Cuadrilla</span><span class="value">${phase.crew}</span></div>
      <div class="phase-meta-item"><span class="label">Sub-pasos</span><span class="value">${phase.substeps.length}</span></div>
      <div class="phase-meta-item"><span class="label">Dependencias</span><span class="value">${phase.deps?.length ? phase.deps.map(d => "Fase " + phasesData.phases.find(p => p.id === d)?.number).join(", ") : "Ninguna"}</span></div>
    </section>

    <section>
      <div class="card-eyebrow">Objetivo</div>
      <p style="margin: 0">${phase.objective}</p>
    </section>

    <section>
      <div class="card-eyebrow">Herramientas</div>
      <div class="tag-row">${phase.tools.map((t) => `<span class="tag">${t}</span>`).join("")}</div>
    </section>

    <section>
      <div class="card-eyebrow">Paso a paso · marca los completados</div>
      <div class="checklist">
        ${phase.substeps.map((step, idx) => {
          const isDone = !!phaseState.substeps[idx];
          return `
            <div class="checklist-item ${isDone ? "done" : ""}" data-step-idx="${idx}">
              <span class="checklist-num">${idx + 1}.</span>
              <span class="checklist-checkbox">${isDone ? "✓" : ""}</span>
              <span class="checklist-text">${step}</span>
            </div>
          `;
        }).join("")}
      </div>
    </section>

    <section class="dod-block">
      <strong>Definición de done</strong>
      ${phase.definition_of_done}
    </section>

    <section>
      <div class="card-eyebrow">Riesgos conocidos</div>
      <ul class="risk-list">${phase.risks.map(r => `<li class="risk-item">${r}</li>`).join("")}</ul>
    </section>

    <section>
      <div class="card-eyebrow">Entregables esperados</div>
      <div class="tag-row">${phase.outputs.map(o => `<span class="tag">${o}</span>`).join("")}</div>
    </section>

    <section>
      <div class="card-eyebrow">Notas</div>
      <textarea id="phase-notes-${phase.id}" placeholder="Observaciones, contactos de proveedores, decisiones tomadas..." rows="3">${phaseState.notes || ""}</textarea>
    </section>

    <div class="phase-actions">
      ${phaseState.done
        ? `<button data-act="reopen">Reabrir fase</button>`
        : `<button data-act="markdone" class="primary">Marcar fase ${phase.number} como completada</button>`}
      ${activePhaseIdx > 0 ? `<button data-act="prev">← Fase ${phase.number - 1}</button>` : ""}
      ${activePhaseIdx < phasesData.phases.length - 1 ? `<button data-act="next">Fase ${phase.number + 1} →</button>` : ""}
    </div>
  `;

  // Bind substeps
  container.querySelectorAll(".checklist-item").forEach((item) => {
    item.addEventListener("click", () => {
      const idx = parseInt(item.dataset.stepIdx, 10);
      toggleSubstep(phase.id, idx);
    });
  });

  // Bind notes
  const notes = document.getElementById(`phase-notes-${phase.id}`);
  if (notes) {
    notes.addEventListener("blur", () => setNote(phase.id, notes.value));
  }

  // Actions
  container.querySelectorAll("[data-act]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const act = btn.dataset.act;
      if (act === "markdone") markPhaseDone(phase.id);
      else if (act === "reopen") reopenPhase(phase.id);
      else if (act === "next") { activePhaseIdx = Math.min(phasesData.phases.length - 1, activePhaseIdx + 1); renderPhases(); }
      else if (act === "prev") { activePhaseIdx = Math.max(0, activePhaseIdx - 1); renderPhases(); }
    });
  });
}

function updateConstruirBadge() {
  const o = overallProgress();
  const badge = document.getElementById("construir-badge");
  if (badge) badge.textContent = `${o.doneCount}/${o.totalPhases}`;
}

// ============================================================
// Progreso tab
// ============================================================

function renderProgressTab() {
  const o = overallProgress();
  const pct = (o.fraction * 100).toFixed(0);
  const pctEl = document.getElementById("overall-pct");
  const fillEl = document.getElementById("overall-fill");
  if (pctEl) pctEl.textContent = pct + "%";
  if (fillEl) fillEl.style.width = pct + "%";

  // Phase cards
  const list = document.getElementById("phase-progress-list");
  if (list) {
    list.innerHTML = phasesData.phases.map((ph) => {
      const f = phaseProgressFraction(ph.id);
      const ps = getProgressState().phases[ph.id] || { substeps: {} };
      const completed = Object.keys(ps.substeps).length;
      const isDone = ps.done;
      return `
        <div class="phase-progress-card ${isDone ? "done" : ""}">
          <span class="num">${isDone ? "✓" : ph.number}</span>
          <div class="info">
            <h4>${ph.name}</h4>
            <div class="meta">${completed} / ${ph.substeps.length} pasos · ${ph.duration_days} día${ph.duration_days > 1 ? "s" : ""} · ${ph.crew}</div>
            <div class="progress-bar"><div class="fill" style="width: ${(f * 100).toFixed(0)}%"></div></div>
          </div>
        </div>
      `;
    }).join("");
  }

  // Log
  const logEl = document.getElementById("log-list");
  const log = getProgressState().log;
  if (logEl) {
    if (log.length === 0) {
      logEl.innerHTML = '<div class="log-entry"><span class="ts">—</span><span>Aún no hay actividad. Marca pasos en la pestaña <strong>Construir</strong>.</span></div>';
    } else {
      logEl.innerHTML = log.slice(0, 30).map((entry) => {
        const date = new Date(entry.ts);
        const ts = date.toLocaleDateString("es-CO", { day: "2-digit", month: "short" }) + " " + date.toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" });
        const phaseLabel = entry.phase === "_meta" ? "" :
          (() => {
            const ph = phasesData.phases.find(p => p.id === entry.phase);
            return ph ? `F${ph.number} · ` : "";
          })();
        return `
          <div class="log-entry ${entry.kind}">
            <span class="ts">${ts}</span>
            <span>${phaseLabel}${entry.message}</span>
          </div>
        `;
      }).join("");
    }
  }

  // Assistant suggestion
  const nx = nextPhase();
  const nxEl = document.getElementById("assistant-next");
  const msgEl = document.getElementById("assistant-message");
  if (nx) {
    if (nxEl) nxEl.textContent = `Fase ${nx.number} · ${nx.name}`;
    if (msgEl) {
      msgEl.innerHTML = `Tu siguiente paso recomendado es <strong>${nx.name}</strong>. ${nx.intro.split(".")[0]}. Ve a la pestaña <strong>Construir</strong> para ver los ${nx.substeps.length} sub-pasos detallados.`;
    }
  } else {
    if (nxEl) nxEl.textContent = "🎉 Proyecto completado";
    if (msgEl) msgEl.innerHTML = "Todas las fases están marcadas como completadas. Exporta tu progreso como respaldo y celebra.";
  }
}

// ============================================================
// BOM tab
// ============================================================

function renderBomTable() {
  const t = document.getElementById("bom-table");
  if (!t) return;
  const k = computeKpis(liveParams, prices);
  const rows = [
    ["Sección", "Cantidad", "Unidad"],
    ["—— Estructura acero ——", "", ""],
    [`Columnas (${liveParams.columns.profile})`, k.steel_lengths.columns.toFixed(1), "m"],
    [`Vigas principales (${liveParams.platform_structure.main_beam_profile})`, k.steel_lengths.main_beams.toFixed(1), "m"],
    [`Viguetas (${liveParams.platform_structure.secondary_joist_profile})`, k.steel_lengths.secondary_joists.toFixed(1), "m"],
    [`Arriostramiento (${liveParams.platform_structure.bracing_profile})`, k.steel_lengths.bracing.toFixed(1), "m"],
    [`Pares A-frame (${liveParams.aframe.rafter_profile})`, k.steel_lengths.rafters.toFixed(1), "m"],
    [`Tirantes (${liveParams.aframe.tie_beam_profile})`, k.steel_lengths.tie_beams.toFixed(1), "m"],
    [`Cumbrera (${liveParams.aframe.ridge_profile})`, k.steel_lengths.ridge.toFixed(1), "m"],
    [`Correas (${liveParams.aframe.purlin_profile})`, k.steel_lengths.purlins.toFixed(1), "m"],
    [`Total acero crudo`, k.steel_lengths.total.toFixed(1), "m"],
    [`Acero fabricado (×1.125)`, k.steel_fabricated_kg.toFixed(0), "kg"],
    ["—— Anclajes ——", "", ""],
    [`Anclajes a roca`, k.anchors, "u"],
    ["—— Envolvente ——", "", ""],
    [`Cubierta`, k.areas.roof_m2.toFixed(1), "m²"],
    [`Piso cabaña`, k.areas.enclosed_m2.toFixed(1), "m²"],
    [`Deck terraza`, k.areas.terrace_m2.toFixed(1), "m²"],
    [`Ventanal frontal`, liveParams.envelope.front_glazing_m2, "m²"],
    [`Muro trasero`, liveParams.envelope.rear_gable_m2, "m²"],
  ];

  t.innerHTML = `
    <thead><tr><th>Concepto</th><th class="num">Cantidad</th><th>Unidad</th></tr></thead>
    <tbody>${rows.slice(1).map(r => `<tr><td>${r[0]}</td><td class="num">${r[1]}</td><td>${r[2]}</td></tr>`).join("")}</tbody>
  `;
}

// ============================================================
// Presupuesto tab
// ============================================================

function renderBudgetTab() {
  const k = computeKpis(liveParams, prices);
  const c = k.cost;
  const fmt = (v) => `$ ${new Intl.NumberFormat("es-CO", { maximumFractionDigits: 0 }).format(v)}`;
  const fmtCompact = (v) => `$${(v / 1_000_000).toFixed(0)} M`;

  document.getElementById("budget-direct").textContent  = fmtCompact(c.direct_cop);
  document.getElementById("budget-overhead").textContent = fmtCompact(c.indirect_cop + c.contingency_cop);
  document.getElementById("budget-iva").textContent     = fmtCompact(c.iva_cop);
  document.getElementById("budget-total").textContent   = fmtCompact(c.total_cop);
  document.getElementById("budget-usd").textContent     = `≈ USD ${(c.total_usd / 1000).toFixed(0)} K`;

  const t = document.getElementById("budget-table");
  if (t) {
    // Suma referencial por fase (anchored del PRESUPUESTO.md manual)
    const phaseTotals = [
      { name: "M1 — Levantamiento + estudios previos", total: 8_804_000 },
      { name: "M2 — Ingeniería estructural", total: 22_800_000 },
      { name: "M3 — Procura de materiales", total: 108_318_300 },
      { name: "M4 — Obra (mano de obra + equipos)", total: 78_400_000 },
    ];
    const subtotalDirect = phaseTotals.reduce((a, b) => a + b.total, 0);
    const indirect = subtotalDirect * prices.overhead.indirect_pct;
    const contingency = subtotalDirect * prices.overhead.contingency_pct;
    const preIva = subtotalDirect + indirect + contingency;
    const iva = preIva * prices.overhead.iva_pct;
    const total = preIva + iva;

    t.innerHTML = `
      <thead><tr><th>Concepto</th><th class="num">Valor</th><th class="num">% del total</th></tr></thead>
      <tbody>
        ${phaseTotals.map(p => `<tr><td>${p.name}</td><td class="num">${fmt(p.total)} COP</td><td class="num">${(p.total / total * 100).toFixed(1)}%</td></tr>`).join("")}
        <tr style="border-top: 2px solid var(--ai-blue-dim)"><td><strong>Subtotal directos</strong></td><td class="num"><strong>${fmt(subtotalDirect)} COP</strong></td><td class="num">${(subtotalDirect / total * 100).toFixed(1)}%</td></tr>
        <tr><td>Indirectos (15%)</td><td class="num">${fmt(indirect)} COP</td><td class="num">${(indirect / total * 100).toFixed(1)}%</td></tr>
        <tr><td>Contingencia (10%)</td><td class="num">${fmt(contingency)} COP</td><td class="num">${(contingency / total * 100).toFixed(1)}%</td></tr>
        <tr><td>Subtotal antes IVA</td><td class="num">${fmt(preIva)} COP</td><td class="num">${(preIva / total * 100).toFixed(1)}%</td></tr>
        <tr><td>IVA 19%</td><td class="num">${fmt(iva)} COP</td><td class="num">${(iva / total * 100).toFixed(1)}%</td></tr>
        <tr style="border-top: 2px solid var(--warm-orange)"><td><strong>TOTAL</strong></td><td class="num"><strong>${fmt(total)} COP</strong></td><td class="num"><strong>100%</strong></td></tr>
        <tr><td>USD referencial</td><td class="num">≈ USD ${(total / prices.exchange_rate_usd_cop).toLocaleString("en-US", { maximumFractionDigits: 0 })}</td><td class="num">—</td></tr>
      </tbody>
    `;
  }
}

// ============================================================
// 3D Full viewer — lazy mount
// ============================================================

let fullViewerMounted = false;
async function ensureFullViewerMounted() {
  if (fullViewerMounted) return;
  const el = document.getElementById("viewer-full");
  if (!el) return;
  await mountViewer(el, `${DATA_BASE}/cabin.glb`, null);
  fullViewerMounted = true;
}

// ============================================================
// Actions
// ============================================================

function bindActions() {
  document.getElementById("btn-reset")?.addEventListener("click", () => {
    liveParams = structuredClone(baseline);
    document.querySelectorAll("input[type=range]").forEach((input) => {
      const path = input.dataset.path;
      input.value = getByPath(baseline, path);
      input.dispatchEvent(new Event("input"));
    });
    updateAllKpis();
  });

  document.getElementById("btn-copy-url")?.addEventListener("click", copyExperimentUrl);

  document.getElementById("btn-download")?.addEventListener("click", () => {
    const k = computeKpis(liveParams, prices);
    downloadExperiment(liveParams, baseline, k);
  });

  document.getElementById("btn-export-progress")?.addEventListener("click", exportProgressJson);

  document.getElementById("btn-import-progress")?.addEventListener("click", () => {
    document.getElementById("import-file")?.click();
  });

  document.getElementById("import-file")?.addEventListener("change", async (ev) => {
    const file = ev.target.files?.[0];
    if (!file) return;
    try {
      await importProgressJson(file);
      alert("Progreso importado correctamente.");
    } catch (err) {
      alert("Error importando: " + err.message);
    }
  });

  document.getElementById("btn-reset-progress")?.addEventListener("click", () => {
    if (confirm("¿Borrar TODO el progreso? Esto no se puede deshacer.")) {
      resetProgress();
    }
  });
}

function getByPath(obj, path) {
  return path.split(".").reduce((o, k) => (o == null ? undefined : o[k]), obj);
}

window.addEventListener("DOMContentLoaded", () => {
  main().catch((err) => {
    console.error(err);
    const status = document.getElementById("viewer-status");
    if (status) status.textContent = `Error: ${err.message}`;
  });
});
