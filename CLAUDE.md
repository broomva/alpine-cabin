# CLAUDE.md — alpine-cabin

Este repo se gobierna bajo la disciplina [bstack](https://github.com/broomva/bstack) cuando un agente lo edita desde `~/broomva/builds/alpine-cabin/`.

## Invariantes

1. **Preliminar hasta validación de ingeniero matriculado.** Ningún reclamo de solidez estructural, cumplimiento normativo, ni aptitud para un propósito determinado. El `LICENSE` lleva este aviso; no debilitarlo.
2. **Sin cantidades inventadas.** Todo número en `BOM.md` debe rastrearse hasta un cálculo en `SPEC.md` o hasta un margen de desperdicio explícito. Si cambias una cantidad, actualiza el cálculo.
3. **Las fotos de referencia en `assets/reference/` son la fuente de verdad del proyecto sobre intención estética.** Cuando el texto y la foto se contradicen, manda la foto para paleta de materiales + forma; el texto puede agregar detalle que la foto no muestra.
4. **La postura open source no es negociable.** Todos los archivos están bajo CC-BY-SA-4.0. No introducir contenido que entre en conflicto (CAD propietario, planos bajo NDA, etc.) sin separarlo a un repo privado.
5. **Formato según audiencia** ([P18](https://github.com/broomva/bstack#p18-format-follows-audience)). README, SPEC, BOM, bitácora de obra → markdown (GitHub renderiza). Planos → SVG dentro de HTML cuando se introduzcan. PDF solo para entregables del ingeniero que deben viajar como documentos firmados.

## Responsabilidad por archivo

| Archivo | Autoritativo para | Lo edita |
|---|---|---|
| `SPEC.md` | Geometría, perfiles, secciones, intención estructural | Diseñador / ingeniero |
| `BOM.md` | Cantidades, márgenes de desperdicio, metas de procura | Diseñador, validado por presupuestador / contratista |
| `docs/SITE.md` | Terreno, geotecnia, GPS, contexto ambiental | Topógrafo / responsable de sitio |
| `docs/REFERENCE.md` | Intención de diseño, decisiones estéticas, programa interior | Diseñador |
| `docs/NOTES.md` | Preguntas abiertas, bitácora de decisiones, hitos, riesgos | Cualquiera — agregar, nunca reescribir historia |
| `LICENSE` | Postura legal | Mantenedor (cambios raros) |
| `assets/reference/` | Fotografías de referencia | Mantenedor (inmutables una vez commiteadas) |

## Flujo de trabajo

- Issues y PRs bienvenidos. Un tema por PR.
- Correcciones de ingeniería tienen prioridad sobre las estéticas.
- Las decisiones van a la tabla de bitácora de decisiones en `docs/NOTES.md` con fecha.
- Las preguntas abiertas siguen abiertas hasta que se registre una decisión explícita.

## Lo que este repo NO contiene

- Datos catastrales privados (lote, GPS exacto, nombre del propietario).
- Archivos CAD propietarios.
- Documentos de licencia de construcción.
- Cotizaciones de contratistas ni datos de precio.

Si alguno de estos llega a ser relevante, vive en un repo privado hermano, no aquí.
