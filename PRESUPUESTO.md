<!--
  ⚠ Archivo auto-generado por cad/budget_generator.py — NO EDITAR A MANO.
  Fuente: cad/params.toml + cad/prices.toml + cad/templates/PRESUPUESTO.md.j2
  Regenerar: `make budget` o `python cad/budget_generator.py`
-->

# PRESUPUESTO — Cabaña Alpina (auto-generado)

Estado: **M0 baseline** — generado desde commit `725c5ee` · params.toml v1.0.

Este presupuesto es un **estimado referencial** basado en `cad/params.toml` (cantidades) y `cad/prices.toml` (precios). **No es una cotización vinculante**. Reemplazar los precios `mid` con cotizaciones reales antes de comprometer financiación.

## 0. Bases del presupuesto

| Variable | Valor |
|---|---|
| Moneda | COP |
| Año de referencia | 2026 |
| Región | Cundinamarca / altiplano cundiboyacense |
| Tasa USD ≈ COP | 4000 |
| IVA | 19% |
| Indirectos | 15% s/directos |
| Contingencia | 10% s/directos |
| Acero fabricado a procurar | 3647 kg ≈ 3.65 t |
| Anclajes a roca | 36 unidades |
| Área cubierta | 77.1 m² |

## 1. FASE M1 — Levantamiento + estudios previos

| Concepto | Cant. | Unid. | Precio mid | Subtotal |
|---|---|---|---|---|
| Levantamiento topográfico | 1 | servicio | $ 2.200.000 COP | **$ 2.200.000 COP** |
| Estudio geotécnico | 1 | servicio | $ 4.000.000 COP | **$ 4.000.000 COP** |
| Replanteo + marcación | 1 | servicio | $ 600.000 COP | **$ 600.000 COP** |
| Limpieza + desbroce | 42.0 | m² | $ 12.000 COP | **$ 504.000 COP** |
| Consulta de licencia | 1 | gestión | $ 1.500.000 COP | **$ 1.500.000 COP** |
| **Subtotal M1** | | | | **$ 8.804.000 COP** |

## 2. FASE M2 — Ingeniería estructural (honorarios)

| Concepto | Cant. | Unid. | Precio mid | Subtotal |
|---|---|---|---|---|
| Diseño estructural + memoria | 1 | servicio | $ 10.000.000 COP | **$ 10.000.000 COP** |
| Planos arquitectónicos | 1 | servicio | $ 5.000.000 COP | **$ 5.000.000 COP** |
| Diseño eléctrico | 1 | servicio | $ 2.000.000 COP | **$ 2.000.000 COP** |
| Diseño hidrosanitario | 1 | servicio | $ 1.800.000 COP | **$ 1.800.000 COP** |
| Trámite de licencia | 1 | gestión | $ 4.000.000 COP | **$ 4.000.000 COP** |
| **Subtotal M2** | | | | **$ 22.800.000 COP** |

## 3. FASE M3 — Procura de materiales

Calculado a partir de las cantidades del [BOM](BOM.md) × los precios mid de `cad/prices.toml`.

| Concepto | Cant. | Unid. | Precio mid | Subtotal |
|---|---|---|---|---|
| Acero estructural fabricado | 3646.9 | kg | $ 6.800 COP | **$ 24.798.926 COP** |
| Placas base 250×250×12 | 10.0 | u | $ 65.000 COP | **$ 650.000 COP** |
| Placas capitel 200×200×10 | 10.0 | u | $ 45.000 COP | **$ 450.000 COP** |
| Cartelas / rigidizadores | 40.0 | u | $ 25.000 COP | **$ 1.000.000 COP** |
| Pernos estructurales M12-M16 | 220.0 | u | $ 5.500 COP | **$ 1.210.000 COP** |
| Anclajes a roca M16-M20 | 42.0 | u | $ 28.000 COP | **$ 1.176.000 COP** |
| Epoxi de anclaje químico | 12.0 | u | $ 110.000 COP | **$ 1.320.000 COP** |
| Grout sin retracción | 2.0 | u | $ 120.000 COP | **$ 240.000 COP** |
| Tuercas + arandelas | 42.0 | juego | $ 6.500 COP | **$ 273.000 COP** |
| Brocas SDS-max | 4.0 | u | $ 280.000 COP | **$ 1.120.000 COP** |
| Lámina metálica negra | 84.9 | m² | $ 85.000 COP | **$ 7.212.768 COP** |
| Bajo-cubierta impermeable | 84.9 | m² | $ 14.000 COP | **$ 1.187.985 COP** |
| Aislamiento cubierta PIR | 84.9 | m² | $ 30.000 COP | **$ 2.545.683 COP** |
| Cielo raso machimbre | 84.9 | m² | $ 85.000 COP | **$ 7.212.768 COP** |
| Caballete (ridge) | 6.2 | m | $ 40.000 COP | **$ 248.000 COP** |
| Flashing de borde | 31.8 | m | $ 32.000 COP | **$ 1.017.600 COP** |
| Vierteaguas | 12.4 | m | $ 28.000 COP | **$ 347.200 COP** |
| Tornillos/clips cubierta | 700.0 | u | $ 1.300 COP | **$ 910.000 COP** |
| Tableros OSB estructural | 12.0 | u | $ 130.000 COP | **$ 1.560.000 COP** |
| Aislamiento piso | 33.0 | m² | $ 40.000 COP | **$ 1.320.000 COP** |
| Barrera de vapor | 33.0 | m² | $ 8.000 COP | **$ 264.000 COP** |
| Acabado piso interior | 33.0 | m² | $ 90.000 COP | **$ 2.970.000 COP** |
| Tablones deck exterior | 33.0 | u | $ 95.000 COP | **$ 3.135.000 COP** |
| Tornillos deck | 800.0 | u | $ 850 COP | **$ 680.000 COP** |
| Aceite/sellador deck | 2.0 | galón | $ 140.000 COP | **$ 280.000 COP** |
| Ventanal frontal templado | 23.0 | m² | $ 380.000 COP | **$ 8.740.000 COP** |
| Puerta corrediza vidrio | 2.0 | u | $ 2.200.000 COP | **$ 4.400.000 COP** |
| Trim madera frontal | 7.0 | m² | $ 110.000 COP | **$ 770.000 COP** |
| Sellos vidriería | 1.0 | lote | $ 400.000 COP | **$ 400.000 COP** |
| Estructura + siding muro trasero | 20.5 | m² | $ 130.000 COP | **$ 2.665.000 COP** |
| Aislamiento muro trasero | 20.5 | m² | $ 40.000 COP | **$ 820.000 COP** |
| Acabado interior muro | 20.5 | m² | $ 55.000 COP | **$ 1.127.500 COP** |
| Ventana/puerta trasera | 1.0 | u | $ 900.000 COP | **$ 900.000 COP** |
| Barandal terraza | 11.0 | m | $ 280.000 COP | **$ 3.080.000 COP** |
| Escalera lateral | 1.0 | u | $ 2.800.000 COP | **$ 2.800.000 COP** |
| Eléctrico rough-in | 30.0 | m² | $ 55.000 COP | **$ 1.650.000 COP** |
| Hidrosanitario rough-in | 30.0 | m² | $ 40.000 COP | **$ 1.200.000 COP** |
| Punto cocina | 1.0 | kit | $ 1.400.000 COP | **$ 1.400.000 COP** |
| Baño completo | 1.0 | set | $ 2.500.000 COP | **$ 2.500.000 COP** |
| Calentador agua | 1.0 | u | $ 1.300.000 COP | **$ 1.300.000 COP** |
| Estufa leña + ducto | 1.0 | u | $ 3.000.000 COP | **$ 3.000.000 COP** |
| Imprimante epóxico | 4.0 | galón | $ 140.000 COP | **$ 560.000 COP** |
| Acabado poliuretano | 4.0 | galón | $ 170.000 COP | **$ 680.000 COP** |
| Protector madera | 3.0 | galón | $ 130.000 COP | **$ 390.000 COP** |
| Sellador poliuretano | 20.0 | tubo | $ 38.000 COP | **$ 760.000 COP** |
| Cinta flashing | 50.0 | m | $ 7.000 COP | **$ 350.000 COP** |
| Drenaje perimetral 4" | 25.0 | m | $ 20.000 COP | **$ 500.000 COP** |
| Gravilla drenaje | 2.0 | m³ | $ 140.000 COP | **$ 280.000 COP** |
| Geotextil | 30.0 | m² | $ 8.000 COP | **$ 240.000 COP** |
| Hardware/tornillería lote | 1.0 | lote | $ 700.000 COP | **$ 700.000 COP** |
| Consumibles soldadura | 1.0 | lote | $ 850.000 COP | **$ 850.000 COP** |
| Discos corte/pulido | 40.0 | u | $ 13.000 COP | **$ 520.000 COP** |
| Adhesivo estructural | 15.0 | tubo | $ 32.000 COP | **$ 480.000 COP** |
| **Subtotal M3** | | | | **$ 106.191.431 COP** |

## 4. FASE M4 — Obra (mano de obra + equipos)

### 4.1 Mano de obra (cuadrilla-día)

| Cuadrilla | Días | Tarifa día mid | Subtotal |
|---|---|---|---|
| Cuadrilla anclaje a roca | 5 | $ 600.000 COP | **$ 3.000.000 COP** |
| Cuadrilla montaje estructural | 25 | $ 650.000 COP | **$ 16.250.000 COP** |
| Cuadrilla envolvente | 20 | $ 550.000 COP | **$ 11.000.000 COP** |
| Cuadrilla acabados | 25 | $ 480.000 COP | **$ 12.000.000 COP** |
| Cuadrilla eléctrica | 8 | $ 500.000 COP | **$ 4.000.000 COP** |
| Cuadrilla hidrosanitaria | 6 | $ 500.000 COP | **$ 3.000.000 COP** |
| Dirección residente | 60 | $ 300.000 COP | **$ 18.000.000 COP** |
| **Subtotal mano de obra** | | | **$ 67.250.000 COP** |

### 4.2 Equipos + transporte

| Concepto | Cant. | Unid. | Precio mid | Subtotal |
|---|---|---|---|---|
| Andamio (alquiler 2 meses) | 1 | set | $ 2.500.000 COP | **$ 2.500.000 COP** |
| Pluma/grúa pequeña | 4 | día | $ 650.000 COP | **$ 2.600.000 COP** |
| Equipo soldadura (alquiler) | 1 | set | $ 1.100.000 COP | **$ 1.100.000 COP** |
| Taladro + compresor | 1 | set | $ 650.000 COP | **$ 650.000 COP** |
| Transporte acero | 2 | viaje | $ 700.000 COP | **$ 1.400.000 COP** |
| Transporte envolvente | 3 | viaje | $ 500.000 COP | **$ 1.500.000 COP** |
| Acarreo + retiro escombros | 1 | lote | $ 1.400.000 COP | **$ 1.400.000 COP** |
| **Subtotal equipos** | | | | **$ 11.150.000 COP** |

| **Subtotal M4** | **$ 78.400.000 COP** |
|---|---|

## 5. Resumen ejecutivo

| Fase | Subtotal |
|---|---|
| M1 — Levantamiento + estudios previos | $ 8.804.000 COP |
| M2 — Ingeniería estructural | $ 22.800.000 COP |
| M3 — Procura | $ 106.191.431 COP |
| M4 — Obra | $ 78.400.000 COP |
| **Total directos** | **$ 216.195.431 COP** |
| Indirectos (15%) | $ 32.429.315 COP |
| Contingencia (10%) | $ 21.619.543 COP |
| **Subtotal antes de IVA** | **$ 270.244.289 COP** |
| IVA (19%) | $ 51.346.415 COP |
| **TOTAL** | **$ 321.590.703 COP** |
| USD (referencial) | ≈ USD 80,398 |

### Distribución porcentual

| Categoría | % del total |
|---|---|
| Materiales (M3) | 33.0% |
| Mano de obra (M4 §4.1) | 20.9% |
| Honorarios profesionales (M2) | 7.1% |
| Equipos + transporte (M4 §4.2) | 3.5% |
| Estudios previos (M1) | 2.7% |
| Indirectos | 10.1% |
| Contingencia | 6.7% |
| IVA | 16.0% |

### Por m²

| Métrica | Valor |
|---|---|
| Área cabaña cerrada | 30 m² |
| Área plataforma total | 42 m² |
| Costo por m² cabaña cerrada | $ 10.719.690 COP / m² |
| Costo por m² plataforma total | $ 7.656.922 COP / m² |

## 6. Disclaimers

- Cantidades derivadas de `cad/params.toml`. Si los parámetros cambian, regenerá este archivo con `make budget`.
- Precios `mid` son referencias de mercado Co/2026, con alta varianza (±30–50%). Cotizá real antes de comprometerte.
- No incluye: terreno, financiamiento, escrituración, conexión a red eléctrica externa, conexión de acueducto veredal, mobiliario, decoración, jardinería, ni post-entrega.
- Para cifras vinculantes, contratá un presupuestador o director de obra licenciado.