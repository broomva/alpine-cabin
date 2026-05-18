# NOTAS — Bitácora de decisiones, preguntas abiertas, hitos

## Hitos

| Hito | Entregables | Estado |
|---|---|---|
| **M0 — Spec + BOM** | README, SPEC, BOM, SITIO, REFERENCIA, LICENSE, fotos de referencia | **En curso (este commit)** |
| M1 — Levantamiento de sitio | Topografía, geotecnia, posiciones GPS de rocas, set fotográfico | Backlog |
| M2 — Ingeniería estructural | Planos firmados, cálculo de cargas, detalle de empalmes, especificación de anclaje, plan de instalaciones gruesas | Backlog (bloqueado por M1) |
| M3 — Procura + fabricación | Lista de corte final, orden de acero, orden de vidrio, orden de deck/cubierta, QA de fabricación | Backlog (bloqueado por M2) |
| M4 — Obra | Perforación de anclajes, montaje de columnas, plataforma, A-frame, envolvente, acabados | Backlog (bloqueado por M3) |
| M5 — Bitácora + retro | Fotos diarias, desvíos respecto al spec, retrospectiva | Concurrente con M4 |

## Preguntas abiertas

1. **Ubicación del sitio** — coordenadas GPS aún sin registrar. Afecta zona sísmica, carga de viento, jurisdicción de licencia, viento predominante, recorrido solar.
2. **Estudio de rocas** — no todas las peñas visibles son necesariamente sanas. Se requiere evaluación geotécnica + prueba acústica antes de fijar posiciones de columna.
3. **Jurisdicción de licencia** — consulta normativa local pendiente.
4. **Entrega de material** — viabilidad de vía de acceso para camión con acero. Pueden requerirse miembros de hasta 12 m (pares) o aceptar empalmes.
5. **Energía + agua** — ¿off-grid o conectado a red? Afecta penetraciones de piso y envolvente.
6. **Modelo de estufa de leña** — el diámetro del ducto + el aislamiento de pase determina dimensión de la penetración de cubierta.
7. **Orientación del gable frontal** — vista vs. viento vs. ganancia solar; requiere visita de sitio.
8. **Acceso al altillo** — ¿escalerilla, escalera tipo alterna, o escalera completa? Afecta cumplimiento normativo (vía de evacuación).

## Bitácora de decisiones

| Fecha | Decisión | Razón |
|---|---|---|
| 2026-05-18 | Open source desde el día 1 bajo CC-BY-SA-4.0 | Maximizar aprendizaje + reuso; el diseño no es propietario, las rocas bajo él sí lo son |
| 2026-05-18 | 9 columnas en malla 3 × 3 | Coincide con el cúmulo visible de rocas; una columna por peña; permite alturas variables |
| 2026-05-18 | Pórticos A-frame cada 1.0 m (6 pórticos) | Espaciado conservador para una cubierta de fuerte pendiente en sitio alpino ventoso; el ingeniero puede relajarlo |
| 2026-05-18 | Par 6.89 m — aceptar empalme como opción | Stock estándar de 6 m + empalme de 1 m O stock custom de 12 m; decisión final al ingeniero |
| 2026-05-18 | Ventanal frontal piso-techo, banda delgada de trim de madera en la base | No negociable estéticamente; el ingeniero diseña alrededor |
| 2026-05-18 | Chimenea sale por agua trasera, no por cumbrera | Preserva el gable frontal limpio; paga la complejidad del flashing |
| 2026-05-18 | El BOM es preliminar, no listo para procura | Todas las cantidades sujetas al ingeniero estructural + levantamiento de sitio |
| 2026-05-18 | Repo en español como primario, inglés sigue accesible vía git history del commit M0 | Audiencia primaria son constructores/ingenieros colombianos y de LATAM |
| 2026-05-18 | Presupuesto referencial Co/2026 publicado en `PRESUPUESTO.md` (BRO-1173) | Necesario para llevar el proyecto a contratista; valor referencial total ≈ $325 M COP (≈ USD 81 K) con IVA — sujeto a cotización real |
| 2026-05-18 | Digital twin M0.3 shipped (BRO-1175) — params.toml como fuente única, build123d genera CAD, HTML interactivo con Three.js | Cambias parámetros en un solo lugar y todo (BOM, CAD, HTML) se regenera coherente. Ver `ARCHITECTURE.md` |

## Riesgos

| Riesgo | Severidad | Mitigación |
|---|---|---|
| Fractura de roca bajo carga | **Alta** | Estudio geotécnico en cada posición de columna; rechazar roca no sana; reubicar columnas si hace falta |
| Corrosión del acero en sitio alpino húmedo | Alta | Galvanizado O imprimante epóxico + acabado en poliuretano; inspección anual |
| Succión del viento sobre gable de vidrio | Alta | El ingeniero diseña el ventanal + anclajes de marco para la carga de viento del sitio |
| Infiltración de agua en uniones cubierta / ventanal | Alta | Flashing continuo; sellador; control de calidad en montaje |
| Falla de empalme en el ápice del par | Media | Empalme atornillado/soldado con END, O evitar pidiendo stock de 12 m |
| Arrancamiento de anclaje en roca | Media | Anclajes químicos con prueba de tracción; embebido mínimo según geotecnia |
| Pudrición del deck en unión con la terraza | Media | Madera tratada; vierteaguas; sellador anual |
| Cuadrilla sin experiencia en anclaje a roca | Media | Subcontratar especialista en perforación para la fase de anclaje |
| Negación de licencia | Media | Consulta preliminar con la autoridad local |
| Sobrecosto en acero | Baja-Media | Asegurar precio del acero temprano; aceptar ±15% en cantidades |

## Contribuciones bienvenidas

Issues y PRs especialmente valorados para:

- **Revisión de ingeniería** del BOM (cualquier persona con credenciales estructurales).
- **Bitácoras fotográficas** de quien replique el diseño — las incluimos en una galería `builds/`.
- **Datos de costo local** — ¿cuánto cuestan 4 toneladas de acero fabricado en tu país?
- **Sustituciones alternativas de materiales** — qué funciona en tu clima que no funcione en el nuestro y viceversa.
