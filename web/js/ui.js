// ui.js — Construye sliders desde una whitelist de parámetros editables.

const SLIDERS = [
  {
    path: "platform.width_m",
    label: "Ancho plataforma",
    unit: "m",
    min: 4.0, max: 8.0, step: 0.1,
    meta: "Ancho frontal (eje X)",
  },
  {
    path: "platform.depth_m",
    label: "Profundidad plataforma",
    unit: "m",
    min: 5.0, max: 9.0, step: 0.1,
    meta: "Profundidad total (eje Y)",
  },
  {
    path: "envelope.enclosed_depth_m",
    label: "Profundidad cabaña cerrada",
    unit: "m",
    min: 3.0, max: 7.0, step: 0.1,
    meta: "Resto = terraza frontal",
  },
  {
    path: "envelope.terrace_depth_m",
    label: "Profundidad terraza",
    unit: "m",
    min: 1.0, max: 4.0, step: 0.1,
    meta: "Frente abierto sobre deck",
  },
  {
    path: "aframe.apex_height_m",
    label: "Altura A-frame",
    unit: "m",
    min: 4.5, max: 8.0, step: 0.1,
    meta: "Ápice sobre plataforma",
  },
  {
    path: "aframe.portal_count",
    label: "Pórticos A-frame",
    unit: "u",
    min: 4, max: 9, step: 1,
    meta: "Cuántos pórticos (más = más rígido + más caro)",
  },
  {
    path: "aframe.purlin_rows_per_side",
    label: "Correas por agua",
    unit: "u",
    min: 8, max: 18, step: 1,
    meta: "Filas de correa en cada lado del techo",
  },
  {
    path: "columns.anchors_per_column",
    label: "Anclajes por columna",
    unit: "u",
    min: 2, max: 6, step: 1,
    meta: "Más anclajes = más estabilidad ante viento/sismo",
  },
];

function getByPath(obj, path) {
  return path.split(".").reduce((o, k) => (o == null ? undefined : o[k]), obj);
}

export function mountSliders(container, params, baseline, onChange) {
  container.innerHTML = "";

  for (const cfg of SLIDERS) {
    const current = getByPath(params, cfg.path);
    const base = getByPath(baseline, cfg.path);

    const isInt = Number.isInteger(cfg.step);

    const div = document.createElement("div");
    div.className = "slider-item";
    div.innerHTML = `
      <label>${cfg.label}</label>
      <div class="slider-row">
        <input type="range" data-path="${cfg.path}"
               min="${cfg.min}" max="${cfg.max}" step="${cfg.step}"
               value="${current}" />
        <span class="slider-value" data-display="${cfg.path}" data-unit="${cfg.unit}">${formatValue(current, cfg.unit, isInt)}</span>
      </div>
      <div class="slider-meta">${cfg.meta} · baseline: ${formatValue(base, cfg.unit, isInt)}</div>
    `;
    container.appendChild(div);

    const input = div.querySelector("input[type=range]");
    const display = div.querySelector(".slider-value");

    input.addEventListener("input", () => {
      const value = isInt ? parseInt(input.value, 10) : parseFloat(input.value);
      display.textContent = formatValue(value, cfg.unit, isInt);
      onChange(cfg.path, value);
    });
  }
}

function formatValue(v, unit, isInt) {
  if (isInt) return `${v} ${unit}`;
  return `${(+v).toFixed(2)} ${unit}`;
}
