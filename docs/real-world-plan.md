# Plan de ejecución real-world — alpine-cabin

Este documento es el puente entre **lo que está en el repo** (digital twin, BOM preliminar, presupuesto referencial) y **construir la cabaña realmente**. Lista pasos concretos, contactos sugeridos en Cundinamarca, y plantillas de RFP.

> **Quién debería leer esto**: el propietario que va a construir, su director de obra, o cualquier persona que tome este diseño como base para una obra real.

---

## Resumen ejecutivo del flujo real-world

```
M0 — Lo que tenés en el repo (terminado)
  ↓
M1 — Levantamiento de sitio (2-3 semanas calendario)
      Top + Geotech + Permit query
  ↓
M2 — Ingeniería estructural (4-8 semanas)
      Planos firmados + cálculos + licencia
  ↓
M3 — Procura (4-6 semanas)
      Cotización + compra + fabricación
  ↓
M4 — Obra (5 meses)
      Anclaje + montaje + envolvente + acabados + entrega
```

Total realista: **9-13 meses** entre que decidís construir y entregás. Sin contar imprevistos de permisos.

---

## M1 — Levantamiento de sitio

### Qué necesitás contratar

| Servicio | Costo aprox. (ref `PRESUPUESTO.md`) | Quién |
|---|---|---|
| Levantamiento topográfico | $1.5 – 3.5 M COP | Topógrafo certificado |
| Estudio geotécnico | $2.5 – 6.5 M COP | Ingeniero geotécnico (mín. especialista en mecánica de rocas) |
| Consulta de licencia | $0.8 – 3 M COP | Curador urbano local |

### Cómo encontrar topógrafos en Cundinamarca

1. **Cámara Colombiana de la Construcción (CAMACOL Bogotá+Cundinamarca)** — directorio público de profesionales matriculados.
   - Sitio: https://camacolcyb.org
2. **Sociedad Colombiana de Topógrafos** — listado nacional.
3. **Universidad Distrital / Universidad Nacional — Facultad de Ingeniería Topográfica** — egresados recientes con tarifas competitivas, suelen aceptar trabajos pequeños.
4. **Pregunta a la JAC (Junta de Acción Comunal) de la vereda** — siempre conocen al topógrafo local que ha hecho levantamientos en la zona.

### Cómo encontrar geotécnicos con experiencia en roca

Este es el rol más crítico para este proyecto en particular. La mayoría de geotécnicos trabaja con suelos blandos, no con anclaje a roca. Filtrar específicamente:

1. **Sociedad Colombiana de Geotecnia (SCG)** — https://scg.org.co — directorio de profesionales.
2. **Buscar antecedentes en proyectos similares**: cabañas elevadas sobre roca, anclaje químico a peñas, construcciones en zonas rocosas (Boyacá, Cundinamarca rural, Santander, montañas del Eje Cafetero).
3. **Universidad Nacional, Universidad de los Andes — Departamento de Ingeniería Civil** — profesores con experiencia en mecánica de rocas a veces consultan en privado o conocen a sus egresados especialistas.
4. **Empresas consultoras conocidas**:
   - Suelos y Pavimentos (Bogotá)
   - INGETEC (proyectos grandes — pueden cotizar uno pequeño si tienen disponibilidad)
   - GeoTechCol

### RFP a topógrafos (plantilla)

```
Asunto: Cotización levantamiento topográfico — predio rural Cundinamarca

Estimado(a) [topógrafo],

Solicito cotización para levantamiento topográfico de una huella
de 6 × 7 metros + 12 metros perimetrales en predio rural ubicado
en [vereda], municipio [X], Cundinamarca.

Alcance:
  - Identificación y cota de 9 peñas de roca expuestas dentro de
    la huella (puntos candidatos para anclaje estructural).
  - Curvas de nivel cada 0.2 m en radio 12 m.
  - Marcación física (pintura) sobre cada peña.
  - Plano topográfico en PDF + CAD (DWG/DXF) + CSV con coordenadas.
  - Foto panorámica desde los 4 cardinales.

Referencia del proyecto:
https://github.com/broomva/alpine-cabin

Necesito el levantamiento en la quincena de [mes año].

Pido por favor:
  1. Cotización con desglose (visita, oficina, entrega).
  2. Plazo de entrega.
  3. Referencias de 2 trabajos similares (cabañas o construcciones
     en sitios rurales con vegetación parcial).

Gracias,
[nombre + teléfono]
```

### RFP a geotécnicos (plantilla)

```
Asunto: Estudio geotécnico de anclaje a roca — cabaña 42 m² Cundinamarca

Estimado(a) [geotécnico],

Solicito cotización para estudio geotécnico orientado a anclaje
químico de columnas metálicas sobre peñas de roca existentes.

Contexto:
  - Cabaña elevada 6 × 7 m sobre 9 columnas, cada una anclada
    a una peña de roca diferente con 4 anclajes M16-M20.
  - Diseño open source disponible en
    https://github.com/broomva/alpine-cabin
  - Levantamiento topográfico ya completado por [topógrafo].

Alcance requerido:
  1. Visita al sitio (medio día).
  2. Inspección + clasificación de cada una de las 9 peñas:
     tipo de roca, grado de meteorización (1-5), discontinuidades,
     capacidad portante estimada (kPa).
  3. Prueba Schmidt hammer (si está disponible) en cada peña.
  4. Recomendación específica por peña: aceptar / reubicar / rechazar.
  5. Especificación de profundidad mínima de embebido y tipo de
     epoxi compatible con la litología.
  6. Recomendación de prueba de tracción in situ tras la instalación
     de anclajes (cuántos puntos, qué carga aplicar).
  7. Entregables: informe firmado PDF + tabla resumen por peña.

Plazo deseado: [fecha]

Pido:
  1. Cotización con desglose (visita, ensayos, informe).
  2. Plazo de entrega del informe firmado.
  3. Referencias en proyectos de anclaje a roca.
  4. CV breve con experiencia específica en mecánica de rocas.

Gracias,
[nombre + teléfono]
```

---

## M2 — Ingeniería estructural

### Qué necesitás contratar

| Servicio | Costo aprox. | Quién |
|---|---|---|
| Diseño estructural + memoria | $6 – 16 M COP | Ingeniero civil especialidad estructural, matriculado COPNIA |
| Planos arquitectónicos detallados | $3 – 8 M COP | Arquitecto matriculado |
| Diseño eléctrico + hidrosanitario | $2 – 5 M COP cada uno | Ingeniero eléctrico / sanitario |
| Trámite licencia construcción | $2.5 – 7 M COP | Curador urbano (gestión) |

### Filtros para el ingeniero estructural

1. **Matriculado en COPNIA** con tarjeta profesional vigente.
2. **NSR-10 fluído** — pregúntale qué requisitos NSR-10 aplican a este proyecto y cómo los va a verificar.
3. **Experiencia con acero estructural** (no solo concreto). Pídele 2 proyectos similares.
4. **Disposición a recibir un repo de GitHub como input** — la realidad es que mucho ingeniero trabaja solo con dibujos en PDF/DWG. Si rechaza el formato digital twin, podés exportarle:
   - STEP del CAD (`cad/exports/cabin.step` — abre en SolidWorks/Inventor/Tekla)
   - BOM en PDF (imprime `BOM.md`)
   - SPEC en PDF (imprime `SPEC.md`)
5. **Honorarios por hito**, no anticipo 100%. Sugerido: 50% al recibir planos firmados, 30% al obtener la licencia, 20% al cerrar supervisión.

### RFP al ingeniero estructural

```
Asunto: Diseño estructural cabaña 6×7 m sobre acero + anclaje a roca

Estimado(a) [ingeniero],

Solicito cotización para diseño estructural completo de una cabaña
A-frame de 6 × 7 m apoyada en 9 columnas metálicas ancladas a
peñas de roca existentes.

Anteproyecto:
  https://github.com/broomva/alpine-cabin
  - SPEC.md: dimensiones y perfiles preliminares
  - BOM.md: cantidades preliminares (~3.6 t acero fabricado)
  - cad/exports/cabin.step: modelo 3D paramétrico
  - Informe geotécnico ya disponible (entregado por [geotécnico])

Alcance:
  1. Cálculo estructural completo con NSR-10:
     - Carga viva, muerta, viento (sitio expuesto en altiplano),
       sismo (zona de Cundinamarca).
     - Verificación de columnas, plataforma, pórticos A-frame.
     - Diseño de empalmes de rafters (largos > stock 6m).
     - Verificación de anclaje a roca contra arrancamiento.
  2. Planos firmados:
     - Estructurales completos con detalles típicos
     - Detalles de anclaje a roca con espec. epoxi
     - Detalles de empalmes
  3. Memoria de cálculo en PDF.
  4. Acompañamiento durante M3 (procura) para resolver consultas
     sobre fabricación.
  5. Supervisión durante M4 obra (visitas + actas):
     - Visita al anclaje (mín. 1)
     - Visita al montaje de columnas (mín. 1)
     - Visita al cierre estructural (mín. 1)

Honorarios sugeridos: pagos por hito, no anticipo 100%.

Pido:
  1. Cotización con desglose por hito.
  2. CV con tarjeta COPNIA vigente.
  3. 2 referencias en proyectos similares.

Gracias,
[nombre + teléfono]
```

---

## M3 — Procura

Una vez tengas los planos firmados de M2:

1. **Cotizar acero** a 3 proveedores. En Cundinamarca:
   - Aceros Sigma
   - Acerías Paz del Río (más bajo, pero verifica calidad)
   - DICOL / Ferrasa
2. **Cotizar vidrio templado** a 3 proveedores:
   - Tecnoglass (más alto, calidad alta)
   - Vidrios y Aluminio S.A.S.
   - Proveedores locales de aluminio
3. **Cotizar cubierta metálica negra** — buscar standing seam:
   - Acesco / Hunter Douglas
   - Acerco
4. **Cotizar mano de obra** — separa cuadrillas:
   - Cuadrilla anclaje a roca: pregunta por especialistas que hayan hecho perforación + anclaje químico antes (no constructores generales).
   - Cuadrilla estructural metalmecánica: soldador certificado + 2 ayudantes.

**Reemplazá la columna `Cotiz. real` en `PRESUPUESTO.md`** a medida que recibas cotizaciones reales.

---

## M4 — Obra

Sigue la guía paso-a-paso en la página interactiva (https://broomva.github.io/alpine-cabin/) tab "Construir". Cada fase tiene 10-25 sub-pasos detallados con cuadrilla, duración, herramientas y definición de done.

### Checkpoints críticos donde NO pasar a la siguiente fase sin firma del ingeniero estructural:

- ✋ Antes de inyectar epoxi en cualquier anclaje, el ingeniero debe haber visto y aprobado el geotécnico
- ✋ Antes de subir columnas, todos los anclajes deben haber pasado prueba de tracción
- ✋ Antes de cerrar la envolvente, el ingeniero debe firmar acta del esqueleto estructural

### Documentación durante la obra

Tomá fotos diarias. Las podés ir colgando como `build-log` issues en el repo. Si replicás el diseño, este build log queda como referencia para futuros constructores.

---

## Costos imprevistos típicos (no incluidos en presupuesto referencial)

| Item | Rango |
|---|---|
| Terreno | (no aplica si ya lo tenés) |
| Acceso vial | 0 si hay vía vehicular; +$5-30 M COP si necesitás abrir trocha |
| Energía eléctrica | 0 si la red está cerca; +$3-15 M COP por conexión |
| Agua | 0 si hay acueducto veredal; +$5-25 M COP por aljibe + bomba |
| Servidumbres / permisos vecinos | $0 – $5 M COP |
| Errores y retrabajos | 5-10% del presupuesto total |

---

## Contactos al autor del repo

Si tenés preguntas técnicas que NO sean de seguridad estructural (para esas usá `SECURITY.md`), podés:
- Abrir un issue en https://github.com/broomva/alpine-cabin/issues
- Contactar a Carlos Escobar-Valbuena: carlos@broomva.tech

---

## Disclaimer final

Este documento es **información de referencia**, no asesoría profesional. Quien decida construir es responsable de:
1. Contratar profesionales licenciados.
2. Obtener todos los permisos legales (curaduría urbana, licencias ambientales si aplican, servidumbres).
3. Cumplir normativa vigente (NSR-10, Ley 388 de 1997, decretos municipales).
4. Asegurar a la cuadrilla y el sitio durante la obra.
5. Cualquier pérdida o daño que ocurra durante o después de la construcción.

El autor del repo **no asume responsabilidad alguna** por las decisiones que tomes a partir de este material.
