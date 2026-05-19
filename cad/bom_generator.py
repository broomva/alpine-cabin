"""bom_generator.py — Regenera BOM.md desde params.toml y la plantilla Jinja2.

Uso: `python cad/bom_generator.py` (desde la raíz del repo o desde cad/).
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from parameters import load_params, load_prices, PARAMS_PATH
from kpis import all_kpis

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
BOM_PATH = REPO_ROOT / "BOM.md"


def params_hash() -> str:
    """Hash determinístico del contenido de params.toml. Reemplaza
    git_commit que era no-determinístico entre commits (cada push cambia
    HEAD pero los archivos generados no deberían cambiar si los inputs
    no cambiaron)."""
    return hashlib.sha256(PARAMS_PATH.read_bytes()).hexdigest()[:12]


def render_bom() -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
        undefined=StrictUndefined,
        trim_blocks=False,
        lstrip_blocks=False,
    )
    tpl = env.get_template("BOM.md.j2")

    p = load_params()
    pr = load_prices()
    k = all_kpis(p, pr)

    return tpl.render(
        p=p,
        sl=k.steel_lengths,
        areas=k.areas,
        steel_raw_kg=k.steel_raw_kg,
        steel_fabricated_kg=k.steel_fabricated_kg,
        experiment=p.raw["experiment"],
        git_commit=params_hash(),
    )


def main() -> None:
    md = render_bom()
    BOM_PATH.write_text(md, encoding="utf-8")
    print(f"✅ BOM regenerado → {BOM_PATH.relative_to(REPO_ROOT)} ({len(md):,} bytes)")


if __name__ == "__main__":
    main()
