# CLAUDE.md — alpine-cabin

This repo is governed by the [bstack](https://github.com/broomva/bstack) discipline when an agent edits it from `~/broomva/builds/alpine-cabin/`.

## Invariants

1. **Preliminary until engineer-stamped.** No claim of structural soundness, code compliance, or fitness for purpose. The `LICENSE` carries this disclaimer; do not weaken it.
2. **No fabricated quantities.** Every number in `BOM.md` traces to a calculation in `SPEC.md` or an explicit waste allowance. If you change a quantity, update the calculation.
3. **The reference photos in `assets/reference/` are the design's source of truth for aesthetic intent.** When prose and photo disagree, the photo wins for materials palette + form; the prose may add detail the photo cannot show.
4. **Open-source posture is non-negotiable.** All files in this repo are CC-BY-SA-4.0. Do not introduce content that conflicts (proprietary CAD, NDA-bound drawings, etc.) without splitting it to a separate private repo.
5. **Audience-correct formatting** ([P18](https://github.com/broomva/bstack#p18-format-follows-audience)). README, SPEC, BOM, build log → markdown (GitHub renders). Drawings → SVG inside HTML when introduced. PDFs only for engineer deliverables that must travel as stamped documents.

## File responsibilities

| File | Authoritative for | Updated by |
|---|---|---|
| `SPEC.md` | Geometry, profiles, member sizes, structural intent | Designer / engineer |
| `BOM.md` | Quantities, waste allowances, procurement targets | Designer, validated by quantity surveyor / contractor |
| `docs/SITE.md` | Terrain, geotech, GPS, environmental context | Site surveyor |
| `docs/REFERENCE.md` | Design intent, aesthetic decisions, interior program | Designer |
| `docs/NOTES.md` | Open questions, decision log, milestones, risks | Anyone — append, never rewrite history |
| `LICENSE` | Legal posture | Maintainer (rare changes) |
| `assets/reference/` | Reference photographs | Maintainer (immutable once committed) |

## Workflow

- Issues + PRs welcome. One topic per PR.
- Engineering corrections take priority over aesthetic ones.
- Decisions go into `docs/NOTES.md` decision-log table with a date.
- Open questions stay open until an explicit decision is logged.

## What this repo does NOT contain

- Private cadastre data (lot number, exact GPS, owner name).
- Proprietary CAD files.
- Permit-application documents.
- Contractor bids or pricing data.

If any of those become relevant, they live in a sibling private repo, not here.
