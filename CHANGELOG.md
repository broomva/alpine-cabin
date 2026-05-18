# Changelog

Todas las versiones notables de este proyecto se documentan aquí.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/), y este proyecto se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Added
- (próximos cambios irán aquí)

## [0.3.7] — 2026-05-18 — Pages live + renders + UI redesign

### Added
- **GitHub Pages live**: `https://broomva.github.io/alpine-cabin/` con deploy automático vía Actions.
- **Renders 3D**: `cad/render_views.py` captura 4 vistas (iso/front/side/top) en `assets/renders/`.
- **UI redesigned con tabs**: 7 tabs (Overview, Construir, Parámetros, BOM, Presupuesto, 3D, Progreso) en estética arcan-glass (dark + glass + AI blue).
- **Asistente de progreso**: checklists por fase guardadas en `localStorage`, export/import JSON.
- **Guía de construcción detallada**: 8 fases con paso-a-paso (140+ sub-pasos totales), riesgos, definición-de-done, herramientas, entregables.
- **Dogfood automatizado**: `cad/dogfood.py` con Playwright recorre todas las tabs y valida interacciones.
- **OSS best practices**: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`, `CITATION.cff`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`.
- **bstack governance**: `AGENTS.md`, `.control/policy.yaml`.

### Changed
- `web/js/viewer.js` migrado a convención Y-up (compatible con la salida default de build123d gltf).
- `BOM.md` ahora se considera generado — editar la plantilla `cad/templates/BOM.md.j2` no el archivo directamente.

### Tickets
- BRO-1175, BRO-1176

## [0.3.0] — 2026-05-18 — Digital Twin

### Added
- **Pipeline params → BOM → CAD → HTML**: `cad/params.toml` como fuente única de verdad de la cual derivan automáticamente la documentación y el modelo 3D.
- **`cad/cabin.py`**: modelo paramétrico build123d genera STEP/STL/GLB.
- **`web/index.html`**: viewer Three.js + sliders + KPIs en vivo + descarga de experimento.
- **`ARCHITECTURE.md`**: 13 decisiones arquitectónicas + diagramas.
- **`Makefile`**: `make setup`, `make all`, `make serve`, `make dogfood`.

### Tickets
- BRO-1175

## [0.2.0] — 2026-05-18 — Presupuesto

### Added
- **`PRESUPUESTO.md`**: presupuesto referencial Co/2026 con desglose por fase M1–M4, rangos low/mid/high, análisis de sensibilidad, flujo de caja sugerido. Total referencial ≈ $325 M COP (≈ USD 81 K).

### Tickets
- BRO-1173

## [0.1.1] — 2026-05-18 — i18n español

### Changed
- README, SPEC, BOM, docs/* traducidos al español. LICENSE mantiene texto canónico en inglés + traducción de cortesía.

## [0.1.0] — 2026-05-18 — M0 inicial

### Added
- Esqueleto del repo con `README.md`, `SPEC.md`, `BOM.md`, `docs/SITE.md`, `docs/REFERENCE.md`, `docs/NOTES.md`.
- 3 imágenes de referencia en `assets/reference/` (cabaña, terreno, infografía).
- Licencia CC-BY-SA-4.0 con disclaimer de ingeniería.
- `CLAUDE.md` con contrato bstack para edits de agentes.

### Tickets
- BRO-1172

[Unreleased]: https://github.com/broomva/alpine-cabin/compare/v0.3.7...HEAD
[0.3.7]: https://github.com/broomva/alpine-cabin/compare/v0.3.0...v0.3.7
[0.3.0]: https://github.com/broomva/alpine-cabin/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/broomva/alpine-cabin/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/broomva/alpine-cabin/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/broomva/alpine-cabin/releases/tag/v0.1.0
