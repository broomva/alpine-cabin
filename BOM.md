<!--
  ⚠ Archivo auto-generado por cad/bom_generator.py — NO EDITAR A MANO.
  Fuente: cad/params.toml + cad/templates/BOM.md.j2
  Regenerar: `make bom` o `python cad/bom_generator.py`
-->

# BOM — Listado Preliminar de Materiales (auto-generado)

Estado: **M0 baseline** — params hash `e3bdadede54c` · schema v1.0.

> Este BOM es derivado de `cad/params.toml`. Las cantidades se recalculan automáticamente cuando cambian los parámetros. Margen de desperdicio aplicado: 10–15% según partida.

## Supuestos

- Plataforma: 6.0 × 7.0 m = 42.0 m²
- Cabaña cerrada: 6.0 × 5.0 m = 30.0 m²
- Terraza: 6.0 × 2.0 m = 12.0 m²
- A-frame: apex 6.2 m, 6 pórticos a 1.0 m
- Rafter (calculado): √(3.0² + 6.2²) = **6.888 m**

## 1. Acero estructural — plataforma + cimentación

| Elemento | Perfil | Longitud cruda | × waste | Pedir |
|---|---|---|---|---|
| Columnas | HSS_100x100x4 | 10.8 m | 10% | **11.9 m** |
| Vigas principales | IPE_160 | 39.0 m | 10% | **42.9 m** |
| Viguetas secundarias | C_100x50 | 144.0 m | 10% | **158.4 m** |
| Arriostramiento diagonal | L_50x50x4 | 24.0 m | 15% | **27.6 m** |
| Placas base 250×250×12 | acero | 9 u | 10% | **10 u** |
| Placas capitel 200×200×10 | acero | 9 u | 10% | **10 u** |
| Anclajes a roca | M16–M20 | 36 u | 15% | **42 u** |
| Cartelas / rigidizadores | 8–10 mm | 36 u | 10% | **40 u** |

## 2. Acero estructural — cabaña A-frame

| Elemento | Perfil | Cálculo | Longitud cruda | × waste | Pedir |
|---|---|---|---|---|---|
| Pares A-frame | HSS_120x80x4 | 6 × 2 × 6.888 m | 82.7 m | 10% | **90.9 m** |
| Tirantes | HSS_100x50x3 | 6 × 6.0 m | 36.0 m | 10% | **39.6 m** |
| Cumbrera | HSS_100x50x3 | 5.4 m | 5.4 m | 10% | **5.9 m** |
| Correas | C_80x40x2 | 13 × 2 × (5.0 + 0.4) | 140.4 m | 10% | **154.4 m** |

## 3. Resumen acero

| Categoría | Longitud cruda | Peso (kg/m × m) |
|---|---|---|
| Columnas (HSS_100x100x4) | 10.8 m | 131 kg |
| Vigas principales (IPE_160) | 39.0 m | 616 kg |
| Viguetas (C_100x50) | 144.0 m | 720 kg |
| Arriostramiento (L_50x50x4) | 24.0 m | 72 kg |
| Pares (HSS_120x80x4) | 82.7 m | 1000 kg |
| Tirantes (HSS_100x50x3) | 36.0 m | 245 kg |
| Cumbrera (HSS_100x50x3) | 5.4 m | 37 kg |
| Correas (C_80x40x2) | 140.4 m | 421 kg |
| **Total acero crudo** | **482.3 m** | **3242 kg** |
| Acero fabricado (×1.125) | | **3647 kg ≈ 3.6 t** |

## 4. Envolvente

| Elemento | Cantidad | Margen | Pedir |
|---|---|---|---|
| Cubierta metálica negra | 77.1 m² | 10% | 84.9 m² |
| Bajo-cubierta impermeable | 77.1 m² | 10% | 84.9 m² |
| Aislamiento cubierta | 77.1 m² | 10% | 84.9 m² |
| Cielo raso machimbre | 77.1 m² | 10% | 84.9 m² |
| Tablero estructural piso | 30.0 m² | 10% | 33.0 m² |
| Acabado piso interior | 30.0 m² | 10% | 33.0 m² |
| Deck exterior | 12.0 m² | 15% | 13.8 m² |
| Ventanal frontal vidrio | 23.0 m² | — | 23.0 m² |
| Muro trasero | 20.5 m² | — | 20.5 m² |

## 5. Acceso

| Elemento | Cantidad |
|---|---|
| Barandal terraza | 11.0 m |
| Cables horizontales | 55.0 m |
| Escalera lateral | 1 unidad (6 pasos) |

## Resumen ejecutivo

| Métrica | Valor |
|---|---|
| Plataforma total | 42 m² |
| Cabaña cerrada | 30 m² |
| Acero crudo | 3242 kg |
| **Acero fabricado a procurar** | **3647 kg ≈ 3.6 t** |
| Anclajes a roca (sin margen) | 36 u |
| Anclajes a procurar (15% margen) | 42 u |
| Cubierta | 77 m² |
| Ventanal | 23.0 m² |

Ver [`PRESUPUESTO.md`](PRESUPUESTO.md) para precios y total estimado.

Ver [`ARCHITECTURE.md`](ARCHITECTURE.md) para cómo regenerar este BOM cuando cambian los parámetros.