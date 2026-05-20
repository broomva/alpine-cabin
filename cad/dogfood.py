"""dogfood.py — Recorre la página con Playwright y captura screenshots
de cada tab en ambos temas (dark, light) para validar visualmente el redesign.

Outputs:
  assets/dogfood/<tab>-<theme>.png   para cada tab × {dark, light}
  tabs: overview, construir, bom, presupuesto, cad3d, progreso

Uso: `python cad/dogfood.py` (levanta su propio server temporal en puerto 8889).
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

TABS = ["overview", "construir", "bom", "presupuesto", "cad3d", "progreso"]
THEMES = ["dark", "light"]


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


def set_theme(page, theme: str):
    """Force theme + dispatch event so viewer.js updates scene."""
    page.evaluate(
        """(theme) => {
            document.documentElement.dataset.theme = theme;
            localStorage.setItem('alpine-cabin-theme.v1', theme);
            window.dispatchEvent(new CustomEvent('theme-change', { detail: { theme } }));
        }""",
        theme,
    )


def click_tab(page, tab: str):
    """Click a tab via direct DOM dispatch — bypasses Playwright actionability
    checks. The procedural viewer's lazy mount for cad3d does heavy synchronous
    geometry work that can stall the main thread; standard click waits time out."""
    page.evaluate(
        """(tab) => {
            const btn = document.querySelector(`.tab-btn[data-tab="${tab}"]`);
            if (!btn) throw new Error(`No tab button for data-tab=${tab}`);
            btn.click();
        }""",
        tab,
    )


def capture_tabs(page, theme: str):
    """Capture each tab for a given theme. Assumes page already loaded."""
    print(f"\n— Tema {theme} —")
    set_theme(page, theme)
    time.sleep(0.5)  # let CSS transitions settle
    for tab in TABS:
        click_tab(page, tab)
        time.sleep(0.6)
        if tab == "cad3d":
            time.sleep(3)  # 3D viewer lazy-mounts (heavy procedural build)
        out = DOGFOOD_DIR / f"{tab}-{theme}.png"
        page.screenshot(path=str(out), full_page=False)
        kb = out.stat().st_size / 1024
        print(f"  ✅ {tab:<12}  {out.relative_to(REPO_ROOT)}  ({kb:,.0f} KB)")


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

            for theme in THEMES:
                capture_tabs(page, theme)

            # ----- Interaction tests -----
            print("\n— Interacciones —")

            # Theme toggle button works + persists + viewer scene actually updates
            initial = page.evaluate("() => document.documentElement.dataset.theme")
            bg_before = page.evaluate("() => window.__cabinScene?.background?.getHex?.() ?? null")
            page.locator('#theme-toggle').click()
            time.sleep(0.4)
            after = page.evaluate("() => document.documentElement.dataset.theme")
            ls_theme = page.evaluate("() => localStorage.getItem('alpine-cabin-theme.v1')")
            bg_after = page.evaluate("() => window.__cabinScene?.background?.getHex?.() ?? null")
            if initial == after:
                errors.append(f"theme-toggle: no cambió de tema (sigue {after})")
            if ls_theme != after:
                errors.append(f"theme-toggle: localStorage ({ls_theme}) != dataset ({after})")
            if bg_before is None or bg_after is None:
                errors.append(f"theme-toggle: __cabinScene.background no expuesto (before={bg_before}, after={bg_after})")
            elif bg_before == bg_after:
                errors.append(f"theme-toggle: viewer scene.background NO cambió tras toggle (sigue 0x{bg_after:06x})")
            print(f"  ✓ Theme toggle: {initial} -> {after} (localStorage={ls_theme})")
            if bg_before is not None and bg_after is not None:
                print(f"  ✓ Viewer scene.background: 0x{bg_before:06x} -> 0x{bg_after:06x}")

            # Slider in Overview tab (params are inline there now)
            click_tab(page, "overview")
            time.sleep(0.5)
            slider = page.locator('input[type=range]').first
            if slider.count() > 0:
                slider.evaluate("(el) => { el.value = el.max || '7.0'; el.dispatchEvent(new Event('input')); }")
                time.sleep(0.5)
                dirty = page.locator('.kpi-value.dirty').count()
                print(f"  ✓ Slider -> KPIs dirty: {dirty}")
                if dirty == 0:
                    errors.append("interaction: no KPIs marked dirty after slider change")
            else:
                errors.append("interaction: no slider found in Overview")

            # Substep toggle in Construir tab
            click_tab(page, "construir")
            time.sleep(0.4)
            first_step = page.locator('.checklist-item').first
            first_step.click()
            time.sleep(0.3)
            is_done = first_step.evaluate("(el) => el.classList.contains('done')")
            print(f"  ✓ Substep toggle: done={is_done}")
            if not is_done:
                errors.append("interaction: substep did not toggle to done")

            # Progress localStorage persistence
            ls = page.evaluate("() => localStorage.getItem('alpine-cabin-progress.v1')")
            if ls:
                print(f"  ✓ localStorage progress: {len(ls)} bytes saved")
            else:
                errors.append("persistence: nothing in alpine-cabin-progress.v1")

            browser.close()

    total = len(TABS) * len(THEMES)
    print()
    if errors:
        print(f"⚠ {len(errors)} issues encontradas:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"✅ Dogfood passed — {total} screenshots ({len(TABS)} tabs x {len(THEMES)} temas), sin errores")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
