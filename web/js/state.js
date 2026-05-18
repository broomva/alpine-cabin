// state.js — Persistencia de estado: URL hash + JSON download.
// El estado mínimo guardado en URL es el delta vs baseline (solo lo que cambió).

const SLIDER_PATHS = [
  "platform.width_m",
  "platform.depth_m",
  "envelope.enclosed_depth_m",
  "envelope.terrace_depth_m",
  "aframe.apex_height_m",
  "aframe.portal_count",
  "aframe.purlin_rows_per_side",
  "columns.anchors_per_column",
];

function get(obj, path) {
  return path.split(".").reduce((o, k) => (o == null ? undefined : o[k]), obj);
}
function set(obj, path, value) {
  const parts = path.split(".");
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    if (cur[parts[i]] == null) cur[parts[i]] = {};
    cur = cur[parts[i]];
  }
  cur[parts[parts.length - 1]] = value;
}

function pathsToDelta(params, baseline) {
  const delta = {};
  for (const p of SLIDER_PATHS) {
    const a = get(params, p);
    const b = get(baseline, p);
    if (a !== b) delta[p] = a;
  }
  return delta;
}

function deltaToPartialParams(delta) {
  const obj = {};
  for (const [k, v] of Object.entries(delta || {})) set(obj, k, v);
  return obj;
}

export function saveExperimentToHash(params, baseline) {
  const delta = pathsToDelta(params, baseline);
  if (Object.keys(delta).length === 0) {
    if (location.hash) history.replaceState(null, "", location.pathname + location.search);
    return;
  }
  const compact = btoa(unescape(encodeURIComponent(JSON.stringify(delta))));
  history.replaceState(null, "", `#x=${compact}`);
}

export function loadExperimentFromHash() {
  if (!location.hash) return null;
  const m = location.hash.match(/x=([A-Za-z0-9+/=]+)/);
  if (!m) return null;
  try {
    const json = decodeURIComponent(escape(atob(m[1])));
    const delta = JSON.parse(json);
    return deltaToPartialParams(delta);
  } catch (err) {
    console.warn("hash inválido:", err);
    return null;
  }
}

export function copyExperimentUrl() {
  const url = location.href;
  navigator.clipboard.writeText(url).then(() => {
    flashStatus("URL copiada al portapapeles");
  }).catch(() => {
    flashStatus("No pude copiar — copia manualmente: " + url);
  });
}

export function downloadExperiment(params, baseline, kpisSnapshot) {
  const delta = pathsToDelta(params, baseline);
  const exp = {
    schema_version: "1.0",
    exported_at: new Date().toISOString(),
    exported_from: location.origin + location.pathname,
    base_commit: baseline?._meta?.base_commit ?? "unknown",
    delta_paths: delta,
    full_params: params,
    kpis_snapshot: kpisSnapshot,
    annotations: "",
  };
  const blob = new Blob([JSON.stringify(exp, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const stamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  a.download = `alpine-cabin-experimento-${stamp}.json`;
  a.click();
  URL.revokeObjectURL(url);
  flashStatus("Experimento descargado · aplicar con `python cad/apply_experiment.py`");
}

function flashStatus(msg) {
  const el = document.getElementById("viewer-status");
  if (!el) return;
  const old = el.textContent;
  el.textContent = msg;
  setTimeout(() => { el.textContent = old; }, 3500);
}
