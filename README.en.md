# Alpine Cabin — Open-Source Build

A 6 × 7 m elevated A-frame cabin on a steel platform supported by existing rock outcroppings. Open-sourced from day one so anyone can fork the design, the bill of materials, and the build log.

**🌐 Interactive page**: **<https://broomva.github.io/alpine-cabin/>** · 📐 STEP/STL in [`cad/exports/`](cad/exports/) · 📄 [README en español](README.md) (primary)

![Reference cabin](assets/reference/01-reference-cabin.png)

## Parametric 3D Model

Generated with [build123d](https://github.com/gumyr/build123d) from [`cad/params.toml`](cad/params.toml). The 4 views regenerate automatically with `make render`.

| | |
|---|---|
| ![Iso](assets/renders/cabin-iso.png) | ![Front](assets/renders/cabin-front.png) |
| Isometric | Front — glass gable |
| ![Side](assets/renders/cabin-side.png) | ![Top](assets/renders/cabin-top.png) |
| Side — A-frame portals | Top |

## Status

**M0.4 — Parametric digital twin + OSS governance.** `cad/params.toml` is the single source of truth. The BOM, CAD model (STEP/STL/GLTF), and interactive page all derive automatically. Dimensions are **preliminary** — profiles, anchors, welds, and bracing must be validated by a licensed structural engineer after a geotechnical survey.

[![CI](https://github.com/broomva/alpine-cabin/actions/workflows/validate.yml/badge.svg)](https://github.com/broomva/alpine-cabin/actions/workflows/validate.yml)
[![Pages](https://github.com/broomva/alpine-cabin/actions/workflows/pages.yml/badge.svg)](https://broomva.github.io/alpine-cabin/)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-blue.svg)](LICENSE)

## What's in this repo

| File | Purpose |
|---|---|
| [`README.md`](README.md) | Primary README (Spanish — target audience is LATAM constructors) |
| [`SPEC.md`](SPEC.md) | Dimensional + system specification |
| [`BOM.md`](BOM.md) | Bill of materials — **auto-generated** from `cad/params.toml` |
| [`PRESUPUESTO.md`](PRESUPUESTO.md) | Reference budget (Colombian market 2026) — auto-generated |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Digital twin pipeline + 13 architectural decisions |
| [`cad/params.toml`](cad/params.toml) | **Single source of truth** — geometry, profiles, column heights |
| [`cad/prices.toml`](cad/prices.toml) | **Single source of truth** — unit prices Co/2026 |
| [`cad/cabin.py`](cad/cabin.py) | Parametric build123d model → STEP + STL + GLB |
| [`web/index.html`](web/index.html) | Interactive page — 3D viewer + parameters + KPIs + progress tracker |
| [`docs/real-world-plan.md`](docs/real-world-plan.md) | Step-by-step plan to actually build: surveyors, engineers, contractors |
| [`docs/SITE.md`](docs/SITE.md), [`docs/REFERENCE.md`](docs/REFERENCE.md), [`docs/NOTES.md`](docs/NOTES.md) | Site context, design intent, decision log |

## How to run the digital twin locally

```bash
make setup     # Creates venv + installs build123d + jinja2 (once)
make all       # Regenerates BOM + budget + CAD + web data from params.toml
make serve     # Serves the page at http://localhost:8765
make validate  # Asserts GLB matches params.toml (regression test)
make render    # Regenerates 4 PNG views in assets/renders/
make dogfood   # Playwright walks the 7 tabs + captures screenshots
```

To experiment with the design:

1. Move the sliders on https://broomva.github.io/alpine-cabin/ (Parameters tab).
2. Download the experiment JSON (button "Descargar experimento JSON").
3. Apply the JSON to the repo: `python cad/apply_experiment.py path/to/experiment.json` — this updates `cad/params.toml`, regenerates BOM / CAD / web data, and suggests a commit.
4. Push → the live page redeploys with your design.

Direct alternative: edit `cad/params.toml` and run `make all`.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the complete system design.

## License

- **Plans, drawings, BOM, documentation** — [Creative Commons Attribution-ShareAlike 4.0](LICENSE) (CC-BY-SA-4.0)
- **Future scripts / tooling** — Apache-2.0 (will be added under `tools/` with a separate `LICENSE-CODE` if introduced)

Free to use, fork, modify, and build from. If you publish derivatives, share-alike under the same license and credit `broomva/alpine-cabin`.

## Engineering disclaimer

Nothing in this repository replaces stamped engineering drawings, a geotechnical report, or a code-compliant building permit. Anyone building from these documents does so at their own risk and must engage licensed professionals (structural engineer, geotechnical engineer, local building authority) before procuring steel or drilling rock anchors. The author assumes no liability.

## Contributing

Issues and PRs welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md). For security or structural-risk reports, see [`SECURITY.md`](SECURITY.md).

This repo follows the [bstack](https://github.com/broomva/bstack) discipline — see [`AGENTS.md`](AGENTS.md) for the operational contract when AI agents edit it.
