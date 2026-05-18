# Alpine Cabin — Open-Source Build

A 6 × 7 m elevated A-frame cabin on a steel platform, supported on existing rock outcroppings. Open-sourced from M0 so anyone can fork the design, the bill of materials, and the build log.

![Reference cabin](assets/reference/01-reference-cabin.png)

## Status

**M0 — Preliminary spec + BOM.** Dimensions and quantities are first-pass and explicitly marked preliminary. Final profiles, anchors, welds, and bracing must be validated by a licensed structural engineer after a geotechnical survey of the site (rock quality, slope, wind, seismic).

## What's here

| File | Purpose |
|---|---|
| [`SPEC.md`](SPEC.md) | Dimensional + system spec (platform, A-frame, envelope) |
| [`BOM.md`](BOM.md) | Preliminary bill of materials — structural steel, envelope, fasteners, finishes |
| [`docs/SITE.md`](docs/SITE.md) | Site context — terrain, rock outcroppings, vegetation, slope |
| [`docs/REFERENCE.md`](docs/REFERENCE.md) | Reference design notes + critical decisions for the engineer |
| [`docs/NOTES.md`](docs/NOTES.md) | Open questions, decision log, milestones |
| [`assets/reference/`](assets/reference/) | Reference cabin photo, site photo, system infographic |

## Concept

- **Footprint**: 6.0 × 7.0 m elevated platform (42 m²)
- **Enclosed cabin**: ~6.0 × 5.0 m (30 m²)
- **Front terrace**: 6.0 × 2.0 m (12 m²)
- **Roof**: A-frame, ~6.2 m apex, black metal standing seam
- **Support**: 9 steel columns (3 × 3 grid) anchored to existing rocks
- **Structure**: Steel platform + steel A-frame portals every ~1.0 m
- **Envelope**: Floor-to-ceiling front glazing, treated-wood gable, machimbre interior lining

The system reuses the site's existing rock outcroppings as foundations — minimal earthworks, minimal concrete. See the system infographic:

![System infographic](assets/reference/03-system-infographic.png)

## License

- **Plans, drawings, documentation, BOM** — [Creative Commons Attribution-ShareAlike 4.0](LICENSE) (CC-BY-SA-4.0)
- **Any future scripts/tooling** — Apache-2.0 (will be added under `tools/` with separate `LICENSE-CODE` when introduced)

You are free to use, fork, modify, and build from these plans. If you publish derivatives, share them under the same license and credit `broomva/alpine-cabin`.

## Engineering disclaimer

Nothing in this repository is a substitute for stamped engineering drawings, a geotechnical report, or a code-compliant building permit. Build at your own risk; consult licensed professionals before procuring steel or drilling rock anchors. The author assumes no liability for any structure built from these documents.

## Contributing

Issues + PRs welcome. Open an issue first if you want to propose a design change so the discussion is searchable.

## Project provenance

Bootstrapped under the [bstack](https://github.com/broomva/bstack) discipline at `~/broomva/builds/alpine-cabin/`. See [`CLAUDE.md`](CLAUDE.md) for the governance contract that applies to agent-driven edits in this repo.
