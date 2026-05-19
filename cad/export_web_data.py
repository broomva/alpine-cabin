"""export_web_data.py — Vuelca params.toml + prices.toml + KPIs a JSON
para que el HTML interactivo los consuma sin necesidad de parser TOML.

Output: web/data/params.json, web/data/prices.json, web/data/kpis.json
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from dataclasses import asdict, is_dataclass

from parameters import load_params, load_prices
from kpis import all_kpis

REPO_ROOT = Path(__file__).resolve().parent.parent
WEB_DATA_DIR = REPO_ROOT / "web" / "data"
WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _stringify(o):
    if is_dataclass(o):
        return {k: _stringify(v) for k, v in asdict(o).items()}
    if isinstance(o, dict):
        return {k: _stringify(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_stringify(v) for v in o]
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    return o


def main() -> None:
    p = load_params()
    pr = load_prices()
    k = all_kpis(p, pr)

    (WEB_DATA_DIR / "params.json").write_text(
        json.dumps(_stringify(p.raw), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (WEB_DATA_DIR / "prices.json").write_text(
        json.dumps(_stringify(pr.raw), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (WEB_DATA_DIR / "kpis.json").write_text(
        json.dumps({
            "schema_version": "1.0",
            "kpis": _stringify(k),
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    for name in ("params.json", "prices.json", "kpis.json"):
        path = WEB_DATA_DIR / name
        kb = path.stat().st_size / 1024
        print(f"  ✅ {name:>14}  ({kb:,.1f} KB)")


if __name__ == "__main__":
    main()
