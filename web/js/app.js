// app.js — entry point. Carga params + KPIs, monta viewer, sliders, y state-sync.

import { mountViewer } from "./viewer.js";
import { mountSliders } from "./ui.js";
import { renderKpis, computeKpis } from "./kpis.js";
import { loadExperimentFromHash, saveExperimentToHash, downloadExperiment, copyExperimentUrl } from "./state.js";

const DATA_BASE = "data";

async function fetchJson(name) {
  const res = await fetch(`${DATA_BASE}/${name}`);
  if (!res.ok) throw new Error(`No pude cargar ${name}: ${res.status}`);
  return res.json();
}

async function main() {
  const status = document.getElementById("viewer-status");
  status.textContent = "Cargando parámetros…";

  // 1. Cargar fuente de verdad (paralelo).
  const [params, prices, baselineKpis] = await Promise.all([
    fetchJson("params.json"),
    fetchJson("prices.json"),
    fetchJson("kpis.json"),
  ]);

  // 2. Estado vivo: empieza en baseline, puede sobreescribirse desde URL hash.
  const baseline = structuredClone(params);
  let liveParams = structuredClone(params);

  const fromHash = loadExperimentFromHash();
  if (fromHash) {
    Object.assign(liveParams, fromHash);
    status.textContent = "Experimento cargado de URL.";
  } else {
    status.textContent = "Baseline cargado.";
  }

  // 3. Monta el 3D viewer (descarga cabin.glb).
  status.textContent = "Cargando modelo 3D…";
  await mountViewer(document.getElementById("viewer"), `${DATA_BASE}/cabin.glb`, () => {
    status.textContent = "Modelo listo · arrastra para rotar · scroll para zoom";
  });

  // 4. Calcula KPIs iniciales + render.
  const update = () => {
    const k = computeKpis(liveParams, prices);
    renderKpis(document.getElementById("kpi-list"), k, computeKpis(baseline, prices));
    saveExperimentToHash(liveParams, baseline);
  };
  update();

  // 5. Monta sliders.
  mountSliders(document.getElementById("sliders"), liveParams, baseline, (path, value) => {
    setByPath(liveParams, path, value);
    update();
  });

  // 6. Acciones de experimento.
  document.getElementById("btn-reset").addEventListener("click", () => {
    liveParams = structuredClone(baseline);
    document.querySelectorAll("input[type=range]").forEach((input) => {
      const path = input.dataset.path;
      input.value = getByPath(baseline, path);
      input.dispatchEvent(new Event("input"));
    });
    update();
  });

  document.getElementById("btn-copy-url").addEventListener("click", () => {
    copyExperimentUrl();
  });

  document.getElementById("btn-download").addEventListener("click", () => {
    const k = computeKpis(liveParams, prices);
    downloadExperiment(liveParams, baseline, k);
  });
}

function setByPath(obj, path, value) {
  const parts = path.split(".");
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) cur = cur[parts[i]];
  cur[parts[parts.length - 1]] = value;
}

function getByPath(obj, path) {
  return path.split(".").reduce((o, k) => (o == null ? undefined : o[k]), obj);
}

window.addEventListener("DOMContentLoaded", () => {
  main().catch((err) => {
    console.error(err);
    document.getElementById("viewer-status").textContent = `Error: ${err.message}`;
  });
});
