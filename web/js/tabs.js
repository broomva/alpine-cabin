// tabs.js — Sistema de pestañas con sincronización a URL hash.

const TAB_IDS = ["overview", "construir", "parametros", "bom", "presupuesto", "cad3d", "progreso"];
const DEFAULT_TAB = "overview";

const listeners = [];

export function initTabs() {
  // Bindings de click
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => activate(btn.dataset.tab));
  });

  // Hash inicial
  const initial = readTabFromHash() || DEFAULT_TAB;
  activate(initial, { silent: true });

  // Escuchar cambios externos al hash (atrás/adelante)
  window.addEventListener("hashchange", () => {
    const t = readTabFromHash() || DEFAULT_TAB;
    activate(t, { silent: true });
  });
}

function readTabFromHash() {
  const m = location.hash.match(/(?:^#|&)tab=([a-z0-9-]+)/);
  if (!m) return null;
  return TAB_IDS.includes(m[1]) ? m[1] : null;
}

function writeTabToHash(tab) {
  const params = new URLSearchParams();
  for (const part of location.hash.replace(/^#/, "").split("&")) {
    if (!part) continue;
    const [k, v] = part.split("=");
    if (k && k !== "tab") params.set(k, v);
  }
  params.set("tab", tab);
  const hash = "#" + params.toString().replace(/%3D/g, "=");
  if (location.hash !== hash) history.replaceState(null, "", hash);
}

export function activate(tab, { silent = false } = {}) {
  if (!TAB_IDS.includes(tab)) tab = DEFAULT_TAB;

  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === tab);
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    const want = `tab-${tab}`;
    panel.classList.toggle("active", panel.id === want);
  });

  if (!silent) writeTabToHash(tab);
  else writeTabToHash(tab); // siempre sincronizar al hash

  for (const fn of listeners) fn(tab);
}

export function onTabChange(fn) {
  listeners.push(fn);
}

export function currentTab() {
  const active = document.querySelector(".tab-btn.active");
  return active ? active.dataset.tab : DEFAULT_TAB;
}
