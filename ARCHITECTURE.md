# ARCHITECTURE — Digital Twin de la Cabaña Alpina

Estado: **M0.3 en construcción** (BRO-1175). Documento vivo.

Este archivo describe el sistema completo: cómo una sola fuente de verdad alimenta toda la documentación, los modelos CAD y la página interactiva, y cómo los experimentos del navegador se sincronizan de vuelta al repo.

---

## 1. Visión

El repo es un **gemelo digital** del proyecto físico:

```
┌──────────────────────────────────────────────────────────────────────┐
│  Realidad física            Gemelo digital (este repo)              │
│  ───────────────            ─────────────────────────               │
│  Sitio + rocas              docs/SITE.md + cad/params.toml          │
│  Diseño del ingeniero       cad/*.py (build123d) + STEP             │
│  Cantidades de obra         BOM.md (generado)                       │
│  Costo total                PRESUPUESTO.md (generado)               │
│  Construcción paso a paso   web/index.html (interactivo)            │
│  Variaciones / what-if      sliders en web/ + experimentos JSON     │
└──────────────────────────────────────────────────────────────────────┘
```

La regla de oro: **cambias un parámetro en una sola parte** (TOML, slider del HTML, o JSON de experimento) y todo lo demás se regenera. No hay drift entre BOM, presupuesto, CAD y HTML.

---

## 2. Fuente única de verdad

```
cad/params.toml         ← geometría + perfiles + alturas + posiciones de rocas
cad/prices.toml         ← precios unitarios Co/2026 (separados para que cambiar
                          precios no toque diseño y viceversa)
```

**Decisión**: TOML, no YAML ni JSON.
- TOML diffea mejor en git que YAML (sin ambigüedad de indentación) y es más legible que JSON.
- Python 3.11+ lee TOML nativamente (`tomllib`).
- Hay step de build que convierte TOML → JSON para que el HTML lo consuma sin librerías de parsing.

**Por qué dos archivos (params + prices)**:
- `params.toml` es el diseño. Lo modifica el diseñador/agente.
- `prices.toml` es el mercado. Lo modifica el presupuestador / contratista al cotizar.
- Separarlos permite versionar el diseño sin contaminarlo con cambios de precio, y al revés.

---

## 3. Pipeline

```
                 cad/params.toml ──┐
                                   │
                 cad/prices.toml ──┤
                                   │
              ┌────────────────────┼─────────────────────┐
              │                    │                     │
              ▼                    ▼                     ▼
   bom_generator.py     budget_generator.py     build123d (cad/cabin.py)
              │                    │                     │
              ▼                    ▼                     ▼
        BOM.md              PRESUPUESTO.md         cad/exports/
        (generado)          (generado)             ├── cabin.step  (ingeniero)
                                                   ├── cabin.stl   (fabricación)
                                                   ├── cabin.glb   (HTML)
                                                   └── renders/*.png
                                   │
                                   ▼
                          web/data/params.json (export TOML → JSON)
                                   │
                                   ▼
                          web/index.html (interactivo)
                                   │
                                   ▼
                          experimento.json (download)
                                   │
                                   ▼
                          apply_experiment.py
                                   │
                                   ▼
                          actualiza params.toml → loop completo
```

Cada flecha es **un script reproducible**. `make all` ejecuta el pipeline completo. CI puede correrlo para validar que no haya drift entre params y archivos generados.

---

## 4. Estructura de directorios

```
alpine-cabin/
├── cad/
│   ├── params.toml             # FUENTE DE VERDAD — geometría/perfiles/alturas
│   ├── prices.toml             # FUENTE DE VERDAD — precios Co/2026
│   ├── pyproject.toml          # Proyecto Python (build123d, tomllib, jinja2)
│   ├── parameters.py           # Loader + validación de params.toml
│   ├── platform.py             # build123d → columnas + plataforma
│   ├── aframe.py               # build123d → pórticos A-frame + correas
│   ├── envelope.py             # build123d → cubierta + glazing + deck
│   ├── cabin.py                # Assembly raíz
│   ├── export.py               # Exporta STEP, STL, GLTF, renders PNG
│   ├── bom_generator.py        # params + plantilla → BOM.md
│   ├── budget_generator.py     # params + prices + plantilla → PRESUPUESTO.md
│   ├── kpis.py                 # Cálculos centralizados (peso acero, costo, área)
│   ├── apply_experiment.py     # JSON experimento → actualiza params.toml
│   ├── onshape_sync.py         # (opcional) sube STEP a Onshape vía API
│   └── exports/                # (gitignored) STEP/STL/GLTF/PNG generados
├── web/
│   ├── index.html              # Página interactiva
│   ├── js/
│   │   ├── app.js              # Bootstrap UI
│   │   ├── viewer.js           # Three.js + GLTF loader
│   │   ├── state.js            # URL hash + localStorage + JSON I/O
│   │   ├── kpis.js             # KPI calc (mirror de cad/kpis.py)
│   │   └── ui.js               # Sliders, inputs, panels
│   ├── css/style.css
│   └── data/
│       ├── params.json         # GENERADO desde params.toml
│       ├── prices.json         # GENERADO desde prices.toml
│       └── cabin.glb           # GENERADO por build123d
├── templates/
│   ├── BOM.md.j2               # Plantilla Jinja2 → BOM.md
│   └── PRESUPUESTO.md.j2       # Plantilla Jinja2 → PRESUPUESTO.md
├── BOM.md                      # GENERADO (header dice "auto-generated, edit template")
├── PRESUPUESTO.md              # GENERADO
├── SPEC.md                     # MANUAL (descripción narrativa)
├── README.md                   # MANUAL
├── ARCHITECTURE.md             # MANUAL (este archivo)
├── docs/                       # MANUAL
└── Makefile                    # Orquestación
```

---

## 5. Contratos

### 5.1 Schema de `params.toml`

```toml
[platform]
width_m = 6.0
depth_m = 7.0
column_grid_cols = 3            # 3 columnas en el eje ancho
column_grid_rows = 3            # 3 filas en el eje profundidad

[columns]
profile = "HSS_100x100x4"       # ID en cad/profiles.toml
# alturas por columna [col][row] en metros
heights_m = [
    [1.8, 1.2, 0.6],            # fila 0 (back, mid, front)
    [1.8, 1.2, 0.6],
    [1.8, 1.2, 0.6],
]

[aframe]
apex_height_m = 6.2
portal_count = 6                # pórticos a lo largo de la profundidad cerrada
portal_spacing_m = 1.0
rafter_profile = "HSS_120x80x4"
tie_beam_profile = "HSS_100x50x3"
ridge_profile = "HSS_100x50x3"
purlin_profile = "C_80x40x2"
purlin_rows_per_side = 13

[envelope]
enclosed_depth_m = 5.0
terrace_depth_m = 2.0
front_glazing_m2 = 23
rear_gable_m2 = 20.5
roof_material = "metal_standing_seam_black"
deck_material = "treated_wood"

[experiment]
# Anotación libre. Sirve para identificar de dónde salió el params actual.
name = "M0 baseline"
source = "manual"               # manual | experiment | engineer | contractor
notes = ""
```

### 5.2 Formato del experimento (JSON export del HTML)

```json
{
  "schema_version": "1.0",
  "exported_at": "2026-05-18T22:00:00Z",
  "exported_from": "https://broomva.github.io/alpine-cabin/",
  "base_commit": "fe368e4",
  "params": { /* mismo schema que params.toml, en JSON */ },
  "kpis_snapshot": {
    "steel_weight_kg": 3404,
    "total_cost_cop_mid": 324754421,
    "anchor_count": 42
  },
  "annotations": "probar con apex 6.5m"
}
```

`apply_experiment.py experimento.json`:
1. Valida `schema_version`.
2. Hace dry-run mostrando diff contra params.toml actual.
3. Si el usuario confirma, escribe params.toml + corre `make all` (regenera BOM, presupuesto, CAD, HTML data).
4. Sugiere `git add -p && git commit` con mensaje pre-armado citando el experimento.

### 5.3 KPIs (calculados en dos lugares — debe ser consistente)

| KPI | Fórmula | Origen |
|---|---|---|
| `steel_length_m` | Σ longitudes de columnas + vigas + viguetas + arriostramiento + pares + tirantes + cumbrera + correas | params |
| `steel_weight_kg` | Σ longitudes × kg/m por perfil | params + profiles |
| `anchor_count` | columns_count × 4 + margen | params |
| `enclosed_area_m2` | width × enclosed_depth | params |
| `terrace_area_m2` | width × terrace_depth | params |
| `roof_area_m2` | 2 × rafter_length × enclosed_depth (con overhang) | derivado |
| `total_cost_cop_mid` | Σ (cantidad × precio_mid) por partida + indirectos + contingencia + IVA | params + prices |

`cad/kpis.py` y `web/js/kpis.js` implementan exactamente las mismas fórmulas. **Esto es duplicación intencional.** Para evitar drift hay un test (`tests/test_kpis_consistency.py`) que carga el modelo con params fijos, calcula KPIs en Python, y los compara con los que reporta el HTML (renderizado headless vía Playwright o similar).

---

## 6. Round-trip HTML ↔ repo

**Modo 1 — Visualización pura (default, sin escritura)**
- Usuario abre `web/index.html` (en GitHub Pages o localmente).
- HTML carga `web/data/params.json` y `web/data/cabin.glb`.
- Sliders permiten variar parámetros → KPIs se recalculan en vivo en JS.
- El modelo 3D NO se regenera en vivo (sería caro). Se muestran indicadores cualitativos (ej. "altura aumentó 20% → estructura más alta").
- Usuario puede:
  - Reset a baseline (revertir sliders)
  - Copy URL (sliders se serializan en URL hash → enlace compartible)
  - Save experiment (descarga JSON con params + KPIs snapshot)

**Modo 2 — Aplicar experimento (con commits al repo)**
- Usuario corre `python cad/apply_experiment.py experimento.json`.
- Script valida + muestra diff + pide confirmación.
- Si confirmado:
  1. Escribe `cad/params.toml` con los nuevos valores.
  2. Ejecuta `make all` (regenera BOM.md, PRESUPUESTO.md, cad/exports/, web/data/).
  3. Imprime sugerencia de commit con mensaje pre-armado.
- Usuario hace `git diff`, `git add`, `git commit` manualmente (revisión humana del cambio antes de persistir).

**Decisión**: nunca auto-commit. El humano sigue siendo el approver del cambio al diseño.

---

## 7. Decisiones arquitectónicas

| ID | Decisión | Por qué |
|---|---|---|
| AD-1 | TOML como fuente de verdad, no JSON ni YAML | Diff legible, tipos explícitos, Python nativo |
| AD-2 | Dos archivos separados (params + prices) | Diseño y precios cambian a ritmos distintos y por personas distintas |
| AD-3 | Markdown generado, no manuscrito | Evita drift entre cantidades y descripción |
| AD-4 | Plantillas Jinja2 para BOM / PRESUPUESTO | El estilo del documento es editable; los datos vienen del TOML |
| AD-5 | GLTF (.glb) para web, STEP para ingeniero, STL para fabricación | Cada audiencia recibe el formato correcto |
| AD-6 | HTML estático (GitHub Pages compatible) | Cero servidor, máxima accesibilidad |
| AD-7 | Regeneración local, nunca en el browser | El browser no corre build123d; el "save experiment" baja JSON, no STEP |
| AD-8 | KPIs duplicados Python + JS con test de consistencia | Necesario para que el HTML calcule en vivo y los generators usen los mismos números |
| AD-9 | URL hash + JSON download para preservar estado | Sin backend, sin login, sin DB |
| AD-10 | apply_experiment.py pide confirmación humana antes de escribir | El humano sigue siendo source-of-authority sobre el repo |
| AD-11 | Onshape sync es opcional, no parte del pipeline crítico | El repo es self-sufficient; Onshape es para colaborar con ingenieros que prefieren la nube |
| AD-12 | `build123d` sobre CadQuery | API moderna, mejor mantenida, encaja con Python 3.12 |
| AD-13 | Aplicar P18 (formato por audiencia) — markdown para repo, HTML para humanos | Coherente con bstack |

---

## 8. Estado de implementación

| Fase | Ticket | Estado |
|---|---|---|
| M0.3.1 — Arquitectura (este archivo) | BRO-1175 (padre) | **In progress** |
| M0.3.2 — Foundation | TBD | Pendiente |
| M0.3.3 — Generators | TBD | Pendiente |
| M0.3.4 — CAD MVP build123d | TBD | Pendiente |
| M0.3.5 — HTML interactivo | TBD | Pendiente |
| M0.3.6 — Sync + Onshape | TBD | Diferido |

---

## 9. Cómo extender

**Agregar un parámetro nuevo**:
1. Agregarlo a `cad/params.toml` con un valor default razonable.
2. Actualizar `parameters.py` para validarlo.
3. Si afecta el BOM: actualizar `templates/BOM.md.j2` o `bom_generator.py`.
4. Si afecta el costo: actualizar `prices.toml` o `budget_generator.py`.
5. Si afecta la geometría: actualizar los módulos build123d correspondientes.
6. Si debe ser controlable desde el HTML: agregar slider en `web/js/ui.js` y mapearlo en `web/js/state.js`.
7. Agregar test de regresión en `tests/`.
8. Regenerar todo (`make all`) y commit.

**Cambiar perfiles de acero**:
- Los perfiles están definidos en `cad/profiles.toml` (TODO: extraer de params.toml inicial).
- Cada perfil tiene `kg_per_m`, `width_mm`, `height_mm`, `thickness_mm`.
- Cambiar `profile = "HSS_120x80x4"` a `profile = "IPE_140"` en `aframe.rafter_profile` recalcula automáticamente peso, costo, y la geometría 3D si la sección está modelada.

---

## 10. Riesgos arquitectónicos conocidos

| Riesgo | Mitigación |
|---|---|
| KPIs en Python y JS pueden divergir | Test de consistencia headless en CI |
| build123d puede no soportar perfiles estructurales reales (IPE160, HSS) | Modelar como prisma rectangular con dimensiones del catálogo; suficiente para visualización |
| Cambiar params.toml requiere regenerar todo — fricción para el usuario | `make all` y `make watch` con file-watcher |
| HTML interactivo sin backend → no puede regenerar geometría | Documentado en AD-7; el HTML es exploratorio, no autoritativo |
| Drift entre BOM manual heredado y BOM generado | Renombrar BOM.md actual a BOM.md.legacy antes de regenerar; diff manual primero |
| Onshape API rate limits | Sync se hace explícito (no automático); script respeta límites |

---

## 11. Convenciones de archivos generados

Todo archivo auto-generado lleva header:

```markdown
<!--
  ⚠ Archivo auto-generado por scripts/bom_generator.py el 2026-05-18 desde:
    - cad/params.toml (commit fe368e4)
    - cad/prices.toml (commit fe368e4)
    - templates/BOM.md.j2

  No editar a mano — los cambios se sobrescriben en el siguiente `make all`.
  Para cambiar el contenido, edita el TOML o la plantilla y regenera.
-->
```

Esto cumple la regla P18 de bstack: el lector entiende inmediatamente si está mirando un artefacto editable o un producto del pipeline.
