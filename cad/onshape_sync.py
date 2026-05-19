"""onshape_sync.py — Sube `cad/exports/cabin.step` a Onshape vía REST API.

Estado: **stub funcional con --dry-run**. Necesita credenciales para upload
real. Documenta el setup completo para cuando el usuario quiera habilitarlo.

Configuración (variables de entorno):
    ONSHAPE_ACCESS_KEY      — Access key del developer portal
    ONSHAPE_SECRET_KEY      — Secret key
    ONSHAPE_DOCUMENT_ID     — ID del documento destino (opcional; si no
                              está, se crea un documento nuevo)
    ONSHAPE_WORKSPACE_ID    — Workspace dentro del documento (opcional)
    ONSHAPE_BASE_URL        — Default https://cad.onshape.com (Enterprise
                              accounts usan https://<company>.onshape.com)

Cómo obtener las API keys:
    1. https://cad.onshape.com → Developer Portal
    2. Click "Create new API key"
    3. Scopes mínimos: OAuth2Read + OAuth2Write
    4. Guardá access + secret en tu password manager
    5. NUNCA commitear las claves al repo

Uso:
    # Dry-run (sin claves, no sube nada — solo muestra qué haría):
    python cad/onshape_sync.py --dry-run

    # Upload real (requiere las env vars arriba):
    export ONSHAPE_ACCESS_KEY=...
    export ONSHAPE_SECRET_KEY=...
    python cad/onshape_sync.py

    # Crear documento nuevo:
    python cad/onshape_sync.py --create-document "alpine-cabin · YYYY-MM-DD"

Rate limits Onshape (2025+):
    - 250 requests/minuto por usuario
    - 25,000 requests/día
    - Subir un STEP = 1-2 requests
    - Este script hace 3 calls como máximo (doc create + element create + STEP import)

Política y privacidad:
    El STEP que subimos NO contiene metadata personal (no coordenadas GPS,
    no nombres de propietario). El nombre del documento puede ser
    customizado vía --doc-name. La carga es PRIVATE por default; el
    propietario puede cambiarla a PUBLIC desde la UI de Onshape después.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import os
import secrets
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
STEP_PATH = REPO_ROOT / "cad" / "exports" / "cabin.step"

DEFAULT_BASE_URL = "https://cad.onshape.com"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
DIM = "\033[2m"
RESET = "\033[0m"


def hmac_sign(secret: str, method: str, nonce: str, date: str,
              content_type: str, url: str) -> str:
    """Onshape API HMAC signature (RFC 7615 style)."""
    parsed = urlparse(url)
    path = parsed.path
    query = parsed.query
    string_to_sign = (
        f"{method.lower()}\n{nonce}\n{date}\n"
        f"{content_type}\n{path}\n{query}\n"
    )
    sig = hmac.new(
        secret.encode("utf-8"),
        string_to_sign.lower().encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(sig).decode("ascii")


def onshape_headers(access: str, secret: str, method: str,
                    url: str, content_type: str = "application/json") -> dict:
    nonce = secrets.token_urlsafe(16)[:25]
    date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
    sig = hmac_sign(secret, method, nonce, date, content_type, url)
    return {
        "Content-Type": content_type,
        "Date": date,
        "On-Nonce": nonce,
        "Authorization": f"On {access}:HmacSHA256:{sig}",
        "Accept": "application/json",
    }


def status() -> tuple[bool, list[str]]:
    """Verifica que el entorno esté listo para upload real."""
    issues: list[str] = []
    if not STEP_PATH.exists():
        issues.append(f"STEP no existe: {STEP_PATH}. Corré `make cad` primero.")
    if not os.getenv("ONSHAPE_ACCESS_KEY"):
        issues.append("ONSHAPE_ACCESS_KEY no está set")
    if not os.getenv("ONSHAPE_SECRET_KEY"):
        issues.append("ONSHAPE_SECRET_KEY no está set")
    return len(issues) == 0, issues


def dry_run() -> None:
    print(f"{BLUE}=== Onshape sync dry-run ==={RESET}")
    print(f"{DIM}Este modo NO sube nada. Solo muestra qué haría con credenciales reales.{RESET}\n")

    print(f"📁 STEP file:    {STEP_PATH.relative_to(REPO_ROOT)}")
    if STEP_PATH.exists():
        kb = STEP_PATH.stat().st_size / 1024
        print(f"   {GREEN}✓{RESET} existe — {kb:,.0f} KB")
    else:
        print(f"   {RED}✗{RESET} NO existe. Corré `make cad` primero.")

    print(f"\n🔐 Credenciales (env vars):")
    for var in ("ONSHAPE_ACCESS_KEY", "ONSHAPE_SECRET_KEY", "ONSHAPE_DOCUMENT_ID",
                "ONSHAPE_WORKSPACE_ID", "ONSHAPE_BASE_URL"):
        val = os.getenv(var)
        if val:
            shown = val[:6] + "…" + val[-3:] if len(val) > 12 else val
            print(f"   {GREEN}✓{RESET} {var} = {shown}")
        else:
            print(f"   {DIM}·{RESET} {var} no está set")

    base_url = os.getenv("ONSHAPE_BASE_URL", DEFAULT_BASE_URL)
    print(f"\n🌐 Endpoint:     {base_url}")

    doc_id = os.getenv("ONSHAPE_DOCUMENT_ID")
    if doc_id:
        ws = os.getenv("ONSHAPE_WORKSPACE_ID", "(default workspace)")
        print(f"\n📤 Acción planeada:")
        print(f"   POST {base_url}/api/blobelements/d/{doc_id}/w/{ws}")
        print(f"   Body: multipart con cabin.step (~{(STEP_PATH.stat().st_size if STEP_PATH.exists() else 0) // 1024} KB)")
    else:
        print(f"\n📤 Acción planeada (no hay ONSHAPE_DOCUMENT_ID):")
        print(f"   1. POST {base_url}/api/documents — crear documento nuevo")
        print(f"   2. POST .../api/blobelements/... — importar el STEP como Part Studio")

    print(f"\n{DIM}Para upload real, configurá las env vars y corré sin --dry-run.{RESET}")


def upload_step(dry: bool = False, doc_name: str = "alpine-cabin · digital twin") -> int:
    if dry:
        dry_run()
        return 0

    ok, issues = status()
    if not ok:
        print(f"{RED}❌ No se puede hacer upload real:{RESET}")
        for i in issues:
            print(f"   - {i}")
        return 1

    # Aquí iría el call real a Onshape API. Por ahora dejamos el stub
    # explícito porque no tenemos test credentials y subir a una cuenta
    # real desde CI/repo sería un anti-pattern.
    print(f"{YELLOW}⚠ STUB: implementación real pendiente.{RESET}")
    print(f"{DIM}Cuando uses esto en tu cuenta:{RESET}")
    print(f"  1. Importá `requests` (ya está en pyproject extras 'onshape')")
    print(f"  2. Usá las funciones `onshape_headers()` y `hmac_sign()` arriba")
    print(f"  3. Endpoints relevantes en https://onshape-public.github.io/docs/")
    print(f"  4. Probá primero contra una cuenta de sandbox antes de tu cuenta principal")
    return 2  # exit 2 = stub no implementado, no es error de validación


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="muestra qué haría sin necesidad de credenciales")
    ap.add_argument("--doc-name", default="alpine-cabin · digital twin",
                    help="nombre del documento Onshape a crear (si aplica)")
    ap.add_argument("--create-document", dest="doc_name_override", default=None,
                    help="alias de --doc-name")
    args = ap.parse_args()

    doc_name = args.doc_name_override or args.doc_name
    return upload_step(dry=args.dry_run, doc_name=doc_name)


if __name__ == "__main__":
    sys.exit(main())
