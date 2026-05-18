# AGENTS.md — Contrato para agentes IA editando este repo

Este archivo declara las reglas operativas que aplican cuando un agente IA (Claude, Codex, GPT, Gemini, etc.) modifica este repositorio. Es el complemento operativo del `CLAUDE.md` (que declara las invariantes) y del `ARCHITECTURE.md` (que declara la estructura técnica).

Si sos humano editando este repo, no necesitás leerlo. Si sos un agente: léelo entero antes de tu primer write.

## Disciplina bstack aplicada

Este repo sigue las [primitivas bstack](https://github.com/broomva/bstack). Las relevantes para este repo son:

| Primitiva | Cómo aplica aquí |
|---|---|
| **P3 Tickets** | Work no trivial requiere un issue / Linear ticket BRO-XXXX antes de empezar. Para repos open source externos: GitHub issue. |
| **P4 PR Pipeline** | Cambios sustantivos van por PR, no commit directo a `main`. CI (Pages workflow) debe pasar. |
| **P10 Worktree Hygiene** | Trabajos paralelos en branches independientes. `git status` limpio antes de empezar nueva tarea. |
| **P11 Empirical** | Validación = correr `make all` + `python cad/dogfood.py` + abrir el HTML, no solo leer el código. |
| **P14 Dep-Chain** | Antes de escribir, enumerar upstream + downstream concreto (file paths + functions). PR body lleva la enumeración. |
| **P15 Snapshot** | Antes de planear, surfacer git status + branch + open PRs + Pages deploy state. |
| **P18 Audience** | Markdown para repo (`SPEC.md`, `BOM.md`). HTML para humanos consumidores (`web/index.html`). Renders PNG para README. |
| **P20 Cross-Review** | PRs sustantivos pasan revisión cruzada por otro modelo / fresh-context subagent antes de merge. |

## Fuente única de verdad

Antes de modificar **cualquier** cantidad numérica:

1. Pregúntate: ¿esto vive en `cad/params.toml`, `cad/prices.toml`, o `cad/profiles` (sección dentro de params.toml)?
2. Si **sí** → editá solo el TOML, luego corré `make all` para regenerar derivados.
3. Si **no** está en el TOML y debería estarlo → primero agregalo al TOML, luego actualizá el código consumidor, luego regenerá.

**NUNCA** editar directamente `BOM.md`, `web/data/params.json`, `web/data/kpis.json`, ni cualquier archivo con el header `⚠ Archivo auto-generado`. Editar la fuente, regenerar.

## Reglas de seguridad estructural

Esta sección es de máxima prioridad. Si dudás, no toques.

1. **Cantidades estructurales**: cambiar un perfil de acero, la altura del A-frame, el número de columnas, o las alturas individuales NO es una decisión de software. Requiere validación estructural. Si un usuario te pide cambiar, indícale que el cambio se aplique vía `apply_experiment.py` para que pase por revisión humana, y que para construir necesita validación de ingeniero matriculado.
2. **Anclajes**: el número (`anchors_per_column`), profundidad de embebido, y tipo de epoxi son críticos. Cambios requieren referencia a geotecnia o ingeniero estructural.
3. **Material**: cambiar de acero a aluminio, de HSS a IPE, de Open Web Steel Joist a otra cosa cambia la mecánica entera. No es un find-replace.

## Reglas para edits típicos

### Cambiar contenido didáctico (intros, descripciones)

Bienvenido. Editar `web/data/construction-phases.json`, `docs/REFERENCE.md`, etc. Mantener tono y estilo del repo (español Colombia neutral, primera persona del plural cuando aplica, técnico pero accesible).

### Agregar una fase de construcción nueva

1. Agregar entrada en `web/data/construction-phases.json` con todos los campos del schema.
2. Si introduce dependencias nuevas, declararlas en `deps`.
3. Actualizar el `CHANGELOG.md` bajo `[Unreleased]`.
4. Cross-check: ¿afecta el flujo del asistente en `web/js/progress.js`? Si sí, ajustar `nextPhase()`.

### Cambiar la paleta visual / glass aesthetic

1. Editar tokens en `web/css/style.css` `:root { ... }`.
2. Mantener accesibilidad (contraste mínimo 4.5:1 para texto small).
3. Probar en Chrome Y Firefox (Safari opcional).
4. Capturar screenshots actualizados de las 7 tabs vía `python cad/dogfood.py`.

### Agregar tests

Tests viven en `tests/` (Python) y se ejecutan con `pytest`. Para el HTML, usar `cad/dogfood.py` como integration test.

## Lo que NO está permitido sin discusión previa

- Cambiar la licencia (CC-BY-SA-4.0).
- Quitar el aviso de ingeniería de `LICENSE`, `README.md`, `SPEC.md`.
- Eliminar disclaimers de `SECURITY.md`.
- Subir contenido con licencia incompatible (proprietary CAD, NDA-bound material).
- Subir secretos (API keys, tokens, datos catastrales privados, GPS exacto del sitio).
- Auto-commitear cambios derivados de un "experiment.json" sin confirmación humana — `cad/apply_experiment.py` MUST mostrar diff y pedir confirmación.

## Lo que SÍ está bien hacer autónomamente

- Regenerar `BOM.md` con `make bom` cuando se cambia `params.toml`.
- Regenerar `cad/exports/cabin.{step,stl}` + `web/data/cabin.glb` con `make cad`.
- Regenerar renders `assets/renders/*.png` con `python cad/render_views.py`.
- Capturar screenshots dogfood con `python cad/dogfood.py`.
- Actualizar `CHANGELOG.md` con cada PR (bajo `[Unreleased]`).
- Commit + push de cambios derivados que NO involucren decisiones estructurales.

## Convenciones de commit

[Conventional Commits](https://www.conventionalcommits.org/):

| Prefijo | Cuándo |
|---|---|
| `feat:` | Nueva funcionalidad |
| `fix:` | Corrección de bug |
| `docs:` | Cambios solo a documentación |
| `refactor:` | Reorganización sin cambio de comportamiento |
| `chore:` | Mantenimiento, dependencias, configs |
| `ci:` | Workflows GitHub Actions |
| `i18n:` | Traducciones |
| `feat(M0.4):` | Para hitos del proyecto, usar `(M0.4)` o `(BRO-1234)` como scope |

Co-Author: Para edits hechos con Claude Code, incluir el trailer `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`.

## Triggers automáticos del workspace

Este repo está integrado al workspace `~/broomva` del usuario. Algunos hooks aplican:

- **Pre-commit hook** (futuro): valida que si tocaste `cad/params.toml`, también regeneraste `BOM.md` y `web/data/*.json`.
- **GitHub Actions**: cada push a `web/**` re-deploya GitHub Pages.
- **Bookkeeping (P6)**: los cambios sustantivos se reflejan en `research/entities/project/alpine-cabin.md` en el workspace madre (no aquí).

## Cuando estés en duda

- Si la duda es estructural → no toques, abre un issue tipo `engineering-review`.
- Si la duda es estética → propón en un PR y dejá que el humano decida.
- Si la duda es de proceso → consulta este archivo, `CLAUDE.md`, y `ARCHITECTURE.md`.

## Versión

Este AGENTS.md está alineado con bstack v0.3.x y CLAUDE Code v0.x. Última revisión: 2026-05-18.
