"""render_views.py — Genera screenshots PNG del modelo 3D desde 4 ángulos.

Estrategia: levanta un servidor HTTP local sobre web/, abre la página con
Playwright headless, lee el bounding box del modelo en Three.js, posiciona
la cámara para framear el bbox desde cada ángulo, captura.

Outputs: assets/renders/cabin-{iso,front,side,top}.png

Uso: `python cad/render_views.py` (después de `make cad` para tener cabin.glb).
"""
from __future__ import annotations

import contextlib
import http.server
import socketserver
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = REPO_ROOT / "web"
RENDERS_DIR = REPO_ROOT / "assets" / "renders"
RENDERS_DIR.mkdir(parents=True, exist_ok=True)

PORT = 8765
VIEWPORT_W = 1600
VIEWPORT_H = 1000


# Las posiciones se computan en función del bbox real del modelo:
#   iso   = posición (3D), mirando al centro
#   front = al frente del modelo, mirando hacia atrás
#   side  = al lado derecho, mirando hacia la izquierda
#   top   = directamente arriba, mirando hacia abajo
#
# `dist_factor` controla qué tan lejos del modelo queda la cámara (en unidades del bbox).

VIEWS = [
    {"name": "iso",   "azimuth": -45, "elevation": 25, "dist_factor": 1.35, "caption": "Vista isométrica"},
    {"name": "front", "azimuth":   0, "elevation":  3, "dist_factor": 1.30, "caption": "Vista frontal — gable de vidrio"},
    {"name": "side",  "azimuth":  90, "elevation":  5, "dist_factor": 1.45, "caption": "Vista lateral — pórticos A-frame"},
    {"name": "top",   "azimuth":   0, "elevation": 80, "dist_factor": 1.30, "caption": "Vista cenital — planta"},
]


@contextlib.contextmanager
def local_server(directory: Path, port: int):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args, **kwargs):
            pass
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

    httpd = socketserver.TCPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield httpd
    finally:
        httpd.shutdown()


CAM_JS = r"""
(args) => {
  const { azimuth, elevation, dist_factor } = args;
  if (!window.__cabinCamera || !window.__cabinControls || !window.__cabinScene) {
    return { ok: false, reason: 'viewer globals not available' };
  }
  const THREE = window.__cabinControls.object.constructor; // hack: get THREE.PerspectiveCamera ctor — better get THREE via import side
  // Compute bbox of the actual cabin model (skip ground plane and grid).
  const box = new (window.__cabinControls.object.parent?.constructor.Box3 || class {})();

  // Build a bbox by iterating top-level scene children that aren't the ground/grid.
  const scene = window.__cabinScene;
  let min = null, max = null;
  scene.traverse((obj) => {
    if (obj.isMesh && obj.geometry && obj.parent && obj.parent.type !== 'Scene') {
      // It's a mesh inside a Group/Compound (the cabin model). Use its world bbox.
      obj.geometry.computeBoundingBox();
      const bb = obj.geometry.boundingBox.clone();
      bb.applyMatrix4(obj.matrixWorld);
      if (!min) { min = bb.min.clone(); max = bb.max.clone(); }
      else {
        min.min(bb.min); max.max(bb.max);
      }
    }
  });

  if (!min) return { ok: false, reason: 'no model meshes' };

  const cx = (min.x + max.x) / 2;
  const cy = (min.y + max.y) / 2;
  const cz = (min.z + max.z) / 2;
  const dx = max.x - min.x, dy = max.y - min.y, dz = max.z - min.z;
  const diag = Math.sqrt(dx*dx + dy*dy + dz*dz);
  const dist = diag * dist_factor;

  const azRad = azimuth * Math.PI / 180;
  const elRad = elevation * Math.PI / 180;
  const px = cx + dist * Math.cos(elRad) * Math.sin(azRad);
  const py = cy - dist * Math.cos(elRad) * Math.cos(azRad);
  const pz = cz + dist * Math.sin(elRad);

  window.__cabinCamera.position.set(px, py, pz);
  window.__cabinControls.target.set(cx, cy, cz);
  window.__cabinControls.update();

  return {
    ok: true,
    bbox: { min: [min.x, min.y, min.z], max: [max.x, max.y, max.z] },
    center: [cx, cy, cz],
    camera_pos: [px, py, pz],
    diag: diag,
    dist: dist,
  };
}
"""


def render_all() -> list[Path]:
    out: list[Path] = []
    with local_server(WEB_DIR, PORT):
        time.sleep(0.5)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
                                       device_scale_factor=2)
            page = ctx.new_page()
            url = f"http://127.0.0.1:{PORT}/"
            print(f"→ Navegando a {url}")
            page.goto(url, wait_until="networkidle")

            page.wait_for_function(
                "() => document.getElementById('viewer-status')?.textContent?.includes('Modelo listo')",
                timeout=30000,
            )
            print("→ Modelo cargado")
            time.sleep(1)

            for view in VIEWS:
                info = page.evaluate(
                    CAM_JS,
                    {"azimuth": view["azimuth"],
                     "elevation": view["elevation"],
                     "dist_factor": view["dist_factor"]},
                )
                if not info.get("ok"):
                    print(f"  ⚠ {view['name']}: {info.get('reason')}")
                    continue
                # Pausa para que damping termine + render fresco
                time.sleep(0.6)

                out_path = RENDERS_DIR / f"cabin-{view['name']}.png"
                viewer = page.locator("#viewer")
                viewer.screenshot(path=str(out_path), animations="disabled")
                kb = out_path.stat().st_size / 1024
                bbmin = info["bbox"]["min"]
                bbmax = info["bbox"]["max"]
                print(f"  ✅ {view['name']:>5}  {out_path.relative_to(REPO_ROOT)}  ({kb:,.0f} KB)")
                print(f"         bbox=({bbmin[0]:.0f},{bbmin[1]:.0f},{bbmin[2]:.0f})→({bbmax[0]:.0f},{bbmax[1]:.0f},{bbmax[2]:.0f}) diag={info['diag']:.0f} dist={info['dist']:.0f}")
                out.append(out_path)

            browser.close()
    return out


if __name__ == "__main__":
    paths = render_all()
    print(f"\nRendered {len(paths)} views to {RENDERS_DIR.relative_to(REPO_ROOT)}")
