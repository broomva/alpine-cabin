// progress.js — Persistencia + UI del avance del proyecto.

const STORAGE_KEY = "alpine-cabin-progress.v1";
const SCHEMA_VERSION = "1.0";

let phasesData = null;
let state = null;
const listeners = [];

function nowIso() {
  return new Date().toISOString();
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultState();
    const parsed = JSON.parse(raw);
    if (parsed?.schema_version !== SCHEMA_VERSION) return defaultState();
    return parsed;
  } catch {
    return defaultState();
  }
}

function defaultState() {
  return {
    schema_version: SCHEMA_VERSION,
    started_at: nowIso(),
    phases: {},
    log: [],
  };
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  for (const fn of listeners) fn(state);
}

function ensurePhase(phaseId) {
  if (!state.phases[phaseId]) {
    state.phases[phaseId] = {
      done: false,
      done_at: null,
      substeps: {},
      notes: "",
    };
  }
  return state.phases[phaseId];
}

export async function initProgress(phasesJson) {
  phasesData = phasesJson;
  state = loadState();
}

export function getState() {
  return state;
}

export function onChange(fn) {
  listeners.push(fn);
}

export function toggleSubstep(phaseId, idx) {
  const p = ensurePhase(phaseId);
  if (p.substeps[idx]) {
    delete p.substeps[idx];
    addLog("note", phaseId, `Desmarcado paso ${idx + 1}`);
  } else {
    p.substeps[idx] = { done_at: nowIso() };
    addLog("note", phaseId, `Marcado paso ${idx + 1}`);
  }
  recomputePhaseDone(phaseId);
  saveState();
}

export function markPhaseDone(phaseId) {
  const p = ensurePhase(phaseId);
  p.done = true;
  p.done_at = nowIso();
  // Marca todos los substeps
  const phase = phasesData.phases.find((x) => x.id === phaseId);
  for (let i = 0; i < phase.substeps.length; i++) {
    if (!p.substeps[i]) p.substeps[i] = { done_at: nowIso() };
  }
  addLog("complete", phaseId, `Fase ${phase.number} completada`);
  saveState();
}

export function reopenPhase(phaseId) {
  const p = ensurePhase(phaseId);
  p.done = false;
  p.done_at = null;
  addLog("note", phaseId, `Fase reabierta`);
  saveState();
}

function recomputePhaseDone(phaseId) {
  const phase = phasesData.phases.find((x) => x.id === phaseId);
  const p = ensurePhase(phaseId);
  const total = phase.substeps.length;
  const completed = Object.keys(p.substeps).length;
  if (completed === total && !p.done) {
    p.done = true;
    p.done_at = nowIso();
    addLog("complete", phaseId, `Fase ${phase.number} completada (todos los pasos marcados)`);
  } else if (completed < total && p.done) {
    p.done = false;
    p.done_at = null;
  }
}

export function setNote(phaseId, text) {
  const p = ensurePhase(phaseId);
  p.notes = text;
  saveState();
}

export function addLog(kind, phaseId, message) {
  state.log.unshift({
    ts: nowIso(),
    kind,
    phase: phaseId,
    message,
  });
  if (state.log.length > 200) state.log.length = 200;
}

export function phaseProgressFraction(phaseId) {
  if (!phasesData) return 0;
  const phase = phasesData.phases.find((x) => x.id === phaseId);
  if (!phase) return 0;
  const p = ensurePhase(phaseId);
  const total = phase.substeps.length;
  if (total === 0) return p.done ? 1 : 0;
  return Object.keys(p.substeps).length / total;
}

export function overallProgress() {
  if (!phasesData) return { fraction: 0, doneCount: 0, totalPhases: 0 };
  const phases = phasesData.phases;
  let sum = 0;
  let doneCount = 0;
  for (const ph of phases) {
    const f = phaseProgressFraction(ph.id);
    sum += f;
    if (state.phases[ph.id]?.done) doneCount++;
  }
  return {
    fraction: sum / phases.length,
    doneCount,
    totalPhases: phases.length,
  };
}

export function nextPhase() {
  if (!phasesData) return null;
  for (const ph of phasesData.phases) {
    if (!state.phases[ph.id]?.done) return ph;
  }
  return null;
}

export function exportJson() {
  const exp = {
    schema_version: SCHEMA_VERSION,
    exported_at: nowIso(),
    exported_from: location.origin + location.pathname,
    progress: state,
  };
  const blob = new Blob([JSON.stringify(exp, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const stamp = nowIso().replace(/[:.]/g, "-").slice(0, 19);
  a.download = `alpine-cabin-progreso-${stamp}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

export async function importJson(file) {
  const text = await file.text();
  const parsed = JSON.parse(text);
  const incoming = parsed.progress ?? parsed; // soporta envoltura o estado directo
  if (!incoming.phases) throw new Error("JSON sin sección 'phases' — formato inválido");
  state = incoming;
  addLog("note", "_meta", "Estado importado desde JSON");
  saveState();
}

export function resetAll() {
  state = defaultState();
  saveState();
}
