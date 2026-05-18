"""dogfood.py — Recorre la página con Playwright y captura screenshots
de cada tab para validar visualmente el redesign.

Outputs: assets/dogfood/{overview,construir,parametros,bom,presupuesto,3d,progreso}.png

Uso: `python cad/dogfood.py` (con `make serve` ya corriendo OPCIONAL — el script
levanta su propio server temporal en puerto 8888 si está libre).
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
DOGFOOD_DIR = REPO_ROOT / "assets" / "dogfood"
DOGFOOD_DIR.mkdir(parents=True, exist_ok=True)

PORT = 8889
VIEWPORT_W = 1600
VIEWPORT_H = 1000

TABS = ["overview", "construir", "parametros", "bom", "presupuesto", "cad3d", "progreso"]


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


def main():
    errors: list[str] = []
    with local_server(WEB_DIR, PORT):
        time.sleep(0.5)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport={"width": VIEWPORT_W, "height": VIEWPORT_H}, device_scale_factor=2)
            page = ctx.new_page()
            page.on("pageerror", lambda exc: errors.append(f"pageerror: {exc}"))
            page.on("console", lambda msg: errors.append(f"console.{msg.type}: {msg.text}") if msg.type == "error" else None)

            url = f"http://127.0.0.1:{PORT}/"
            print(f"→ {url}")
            page.goto(url, wait_until="networkidle")
            page.wait_for_function(
                "() => document.getElementById('viewer-status')?.textContent?.includes('Modelo listo')",
                timeout=30000,
            )
            time.sleep(1)

            for tab in TABS:
                # Click on the tab button
                page.locator(f'.tab-btn[data-tab="{tab}"]').click()
                time.sleep(0.6)  # transition + render

                # For 3D tab, wait extra for viewer to mount lazily
                if tab == "cad3d":
                    time.sleep(2)

                out = DOGFOOD_DIR / f"{tab}.png"
                page.screenshot(path=str(out), full_page=False)
                kb = out.stat().st_size / 1024
                print(f"  ✅ {tab:<12}  {out.relative_to(REPO_ROOT)}  ({kb:,.0f} KB)")

            # Test interaction: move first slider and verify KPI updates
            page.locator('.tab-btn[data-tab="parametros"]').click()
            time.sleep(0.4)
            slider = page.locator('input[type=range]').first
            slider.evaluate("(el) => { el.value = '7.0'; el.dispatchEvent(new Event('input')); }")
            time.sleep(0.5)
            dirty_kpis = page.locator('.kpi-value.dirty').count()
            print(f"  ✓ Interaction test: {dirty_kpis} KPIs marked dirty after slider change")
            if dirty_kpis == 0:
                errors.append("interaction: no KPIs marked dirty after slider change")

            # Test progress: go to Construir tab, mark a substep
            page.locator('.tab-btn[data-tab="construir"]').click()
            time.sleep(0.4)
            first_step = page.locator('.checklist-item').first
            first_step.click()
            time.sleep(0.3)
            is_done = first_step.evaluate("(el) => el.classList.contains('done')")
            print(f"  ✓ Substep toggle: done={is_done}")
            if not is_done:
                errors.append("interaction: substep did not toggle to done")

            # Verify localStorage persistence
            ls = page.evaluate("() => localStorage.getItem('alpine-cabin-progress.v1')")
            if ls:
                print(f"  ✓ localStorage: {len(ls)} bytes saved")
            else:
                errors.append("persistence: nothing in localStorage")

            browser.close()

    print()
    if errors:
        print(f"⚠ {len(errors)} issues encontradas:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"✅ Dogfood passed — {len(TABS)} tabs capturadas, sin errores")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
