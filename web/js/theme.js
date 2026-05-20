// theme.js — Toggle entre dark (default) y light.
//
// Estado: data-theme="dark"|"light" en <html>. Persistido en localStorage.
// Fallback inicial: prefers-color-scheme.
//
// Evento: dispatch "theme-change" en window cuando el USUARIO cambia el tema.
// El sync inicial NO dispara evento — viewer.js lee `currentTheme()` en mount.

const STORAGE_KEY = "alpine-cabin-theme.v1";
const THEMES = ["dark", "light"];

function preferredInitial() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && THEMES.includes(saved)) return saved;
  } catch (_) { /* localStorage may be unavailable */ }
  if (typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-color-scheme: light)").matches) {
    return "light";
  }
  return "dark";
}

function currentTheme() {
  return document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

function setTheme(theme, { dispatch = true } = {}) {
  document.documentElement.dataset.theme = theme;
  try { localStorage.setItem(STORAGE_KEY, theme); } catch (_) { /* ignore */ }
  if (dispatch) {
    window.dispatchEvent(new CustomEvent("theme-change", { detail: { theme } }));
  }
}

function bindToggle() {
  const btn = document.getElementById("theme-toggle");
  if (!btn) return;
  btn.addEventListener("click", () => {
    setTheme(currentTheme() === "light" ? "dark" : "light");
  });
  const updateLabel = () => {
    const next = currentTheme() === "light" ? "modo oscuro" : "modo claro";
    btn.setAttribute("aria-label", `Cambiar a ${next}`);
    btn.setAttribute("title", `Cambiar a ${next}`);
  };
  updateLabel();
  window.addEventListener("theme-change", updateLabel);
}

// Apply BEFORE DOMContentLoaded to avoid flash. No event dispatch on initial
// sync — listeners that mount later (viewer.js) read currentTheme() themselves.
setTheme(preferredInitial(), { dispatch: false });

window.addEventListener("DOMContentLoaded", bindToggle);
