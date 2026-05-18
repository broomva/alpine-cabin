# BOM — Preliminary Bill of Materials

Status: **M0 preliminary.** Quantities include 10–15% waste allowance unless noted. Profiles, anchors, welds, and bracing must be validated by a structural engineer.

## Assumptions

- Total elevated platform: 6.0 × 7.0 m = 42 m²
- Enclosed cabin: ~6.0 × 5.0 m = 30 m²
- Front terrace: ~6.0 × 2.0 m = 12 m²
- A-frame height: ~6.2 m
- Support: 9 steel columns on existing rocks in 3 × 3 grid
- Column heights vary 0.6 m – 1.8 m

## Rafter length

Roof slope length (each side):
```
rafter = √(3.0² + 6.2²) = √47.44 ≈ 6.89 m
```

---

## 1. Structural steel — platform + foundations

Column grid (3 × 3 = 9 supports):
- Width: 0 / 3 / 6 m
- Depth: 0 / 3.5 / 7 m

| Item | Profile | Calculation | Raw length | Waste | Order |
|---|---|---|---|---|---|
| Steel columns | HSS 100×100×4 mm | 3×1.8 + 3×1.2 + 3×0.6 | 10.8 m | 10% | **11.9 m** |
| Main platform beams | IPE160 or eq. | 3×7 m + 3×6 m | 39.0 m | 10% | **42.9 m** |
| Secondary floor joists | C100×50 / tube 80×40 | 19 joists × 6 m | 114.0 m | 10% | **125.4 m** |
| Diagonal bracing | L50×50×4 / flat | X-bracing between posts | 24.0 m | 15% | **27.6 m** |
| Base plates | 250×250×12 mm | 1 per column | 9 units | 10% | **10 units** |
| Top/cap plates | 200×200×10 mm | 1 per column | 9 units | 10% | **10 units** |
| Anchor bolts into rock | M16–M20 + epoxy | 4 per base plate | 36 units | 15% | **42 units** |
| Column stiffener plates | 8–10 mm triangular gussets | 4 per column | 36 units | 10% | **40 units** |

**Platform steel subtotal**

| Group | Total |
|---|---|
| Structural steel length | 207.8 m |
| Base/cap plates | 20 units |
| Rock anchors | 42 units |
| Gusset/stiffener plates | 40 units |

---

## 2. Structural steel — A-frame cabin

Portals every 1.0 m along the 5.0 m enclosed depth → **6 portals**.
Each portal = 2 rafters × 6.89 m = 13.78 m.

| Item | Profile | Calculation | Raw length | Waste | Order |
|---|---|---|---|---|---|
| Inclined A-frame rafters | HSS 120×80×4 mm | 6 × 2 × 6.89 m | 82.7 m | 10% | **90.9 m** |
| Lower tie beams | HSS 100×50×3 mm | 6 × 6 m | 36.0 m | 10% | **39.6 m** |
| Ridge beam | HSS 100×50×3 mm | 1 × 5.4 m | 5.4 m | 10% | **5.9 m** |
| Roof purlins/correas | C80×40×2 mm | 13 × 2 × 5.4 m | 140.4 m | 10% | **154.4 m** |
| Connection plates | 8–10 mm steel | apex / base / knee | — | — | **30–40 plates** |
| Structural bolts | M12–M16 galvanized | frame + purlin | — | — | **150–220 units** |

---

## 3. Total structural steel estimate

| Group | Order length |
|---|---|
| Steel columns | 11.9 m |
| Main platform beams | 42.9 m |
| Secondary joists | 125.4 m |
| Bracing | 27.6 m |
| A-frame rafters | 90.9 m |
| Lower tie beams | 39.6 m |
| Ridge beam | 5.9 m |
| Roof purlins | 154.4 m |
| **Total steel length** | **498.6 m** |

### Approximate steel weight

| Item | Length | kg/m | Weight |
|---|---|---|---|
| Columns 100×100×4 | 11.9 m | 12.1 | 144 kg |
| Main beams IPE160 | 42.9 m | 15.8 | 678 kg |
| Secondary joists | 125.4 m | 5.0 | 627 kg |
| Bracing | 27.6 m | 3.0 | 83 kg |
| A-frame rafters | 90.9 m | 12.1 | 1,100 kg |
| Lower tie beams | 39.6 m | 6.8 | 269 kg |
| Ridge beam | 5.9 m | 6.8 | 40 kg |
| Roof purlins | 154.4 m | 3.0 | 463 kg |
| **Subtotal** | | | **≈ 3,404 kg** |

Add plates, welds, bolts, brackets, fabrication allowance (×1.10 – 1.15):

**Practical procurement target: 3.8 – 4.0 tons of fabricated steel.**

---

## 4. Procurement cut-list (commercial 6 m stock)

| Item | Order length | 6 m pieces |
|---|---|---|
| Columns 100×100×4 | 11.9 m | 2 |
| Main beams IPE160 | 42.9 m | 8 |
| Secondary joists | 125.4 m | 21 |
| Diagonal bracing | 27.6 m | 5 |
| A-frame rafters | 90.9 m | 16 |
| Lower tie beams | 39.6 m | 7 |
| Ridge beam | 5.9 m | 1 |
| Roof purlins | 154.4 m | 26 |
| **Total** | | **~86 pieces of 6 m stock** |

> ⚠ Rafters are 6.89 m. Order custom lengths, 12 m stock cut on site, or engineered bolted/welded splices. **Do not improvise splices at the peak without structural design.**

---

## 5. Floor, deck, platform

### Interior floor (30 m²)

| Item | Spec | Raw | Waste | Order |
|---|---|---|---|---|
| Structural OSB / plywood | 18–21 mm | 30 m² | 10% | 33 m² |
| Floor insulation | 80–100 mm | 30 m² | 10% | 33 m² |
| Vapor / humidity barrier | Membrane | 30 m² | 10% | 33 m² |
| Interior finish flooring | Wood / laminate / vinyl | 30 m² | 10% | 33 m² |

Boards 1.22 × 2.44 m (2.98 m² each): 33 / 2.98 ≈ 11.1 → **12 boards minimum**.

### Exterior terrace / deck (12 m²)

| Item | Spec | Raw | Waste | Order |
|---|---|---|---|---|
| Exterior deck boards | Treated wood / WPC | 12 m² | 15% | 13.8 m² |
| Deck screws | Stainless / galvanized | — | — | 600–800 units |
| Deck oil / sealer | Exterior-grade | 12–14 m² | — | 1–2 gallons |

Boards 140 mm × 3.0 m (0.42 m² each): 13.8 / 0.42 ≈ 33 → **33–36 deck boards**.

---

## 6. Roof + envelope (74.4 m² → 82 m² with waste)

| Item | Spec | Raw | Waste | Order |
|---|---|---|---|---|
| Metal roof sheets | Black standing-seam / trapezoidal | 74.4 m² | 10% | 82 m² |
| Waterproof underlayment | Roof membrane | 74.4 m² | 10% | 82 m² |
| Roof insulation | PIR / mineral wool | 74.4 m² | 10% | 82 m² |
| Interior wood ceiling | Machimbre panels | 74.4 m² | 10% | 82 m² |
| Ridge cap | Black metal flashing | 5.4 m | 15% | 6.2 m |
| Rake / edge flashing | Black metal | 27.6 m | 15% | 31.8 m |
| Eave / drip edge | Black metal | 10.8 m | 15% | 12.4 m |
| Roof screws / clips | For metal roof | — | — | 500–700 units |

Metal sheets 1.0 m effective width × 6.9 m length: 5.4 / 1.0 = 6 sheets per side × 2 = **12 sheets** (order 12–14).

---

## 7. Front façade, walls, glazing

Each gable triangle area = 0.5 × 6.0 × 6.2 = **18.6 m²**.

### Front (glass)

| Item | Spec | Raw | Waste | Order |
|---|---|---|---|---|
| Glass façade | Tempered / laminated + aluminum frame | 21 m² | 10% | 23 m² |
| Sliding / front doors | Glass + aluminum | 2 units | — | 2 units |
| Front wood trim / cladding | Treated wood | 4–6 m² | 15% | 6–7 m² |
| Sealants / gaskets | Exterior glazing | — | — | 1 lot |

### Rear gable

| Item | Spec | Raw | Waste | Order |
|---|---|---|---|---|
| Rear wall framing + cladding | Wood/steel subframe + siding | 18.6 m² | 10% | 20.5 m² |
| Rear wall insulation | 80–100 mm | 18.6 m² | 10% | 20.5 m² |
| Interior wall lining | Wood / gypsum / OSB | 18.6 m² | 10% | 20.5 m² |
| Rear window / door | Optional | 2–4 m² | — | optional |

---

## 8. Railings, stairs, access

Front railing perimeter: 6 + 2 + 2 = **10 m**.

| Item | Spec | Raw | Waste | Order |
|---|---|---|---|---|
| Terrace railing | Wood/steel posts + cable/wood rails | 10.0 m | 10% | 11.0 m |
| Railing posts | every 1.2 m | 10 / 1.2 | — | 9–10 posts |
| Handrail | Wood or metal | 10.0 m | 10% | 11.0 m |
| Cable rails / horizontal | 4–5 rows × 10 m | 50 m | 10% | 55 m |
| Lateral stair | Steel + wood treads | — | 20% | 1 unit |
| Stair stringers | Steel | 2 × 3 m | 10% | 6.6 m |
| Stair handrails | Both sides | 2 × 3 m | 10% | 6.6 m |
| Stair treads | Wood / metal | 5–7 steps | — | 6–8 treads |

---

## 9. Anchoring + rock foundation

Per column base: 1 base plate + 4 rock anchors + epoxy/chemical anchor + grout + nuts/washers.

| Item | Spec | Quantity |
|---|---|---|
| Rock anchors | M16–M20 | 42 units |
| Chemical anchor epoxy | 500 ml cartridges | 10–12 cartridges |
| Non-shrink grout | leveling | 1–2 bags |
| Galvanized nuts / washers | matched | 42–50 sets |
| Base plate shims | steel / stainless | 1 lot |
| Rock drilling bits | SDS-max or core | 2–4 bits |

> ⚠ Anchors must land in **sound, continuous rock**. The best-looking rock is not always the best structural rock. Geotech assessment required.

---

## 10. Waterproofing + protection

| Item | Spec | Quantity |
|---|---|---|
| Steel primer | Epoxy anticorrosive | 60–70 m² coverage |
| Steel finish coat | Polyurethane / exterior enamel | 60–70 m² coverage |
| Wood protector | Lasur / oil / stain | 35–50 m² coverage |
| Roof sealant | Polyurethane / butyl | 12–20 tubes |
| Flashing tape | Openings + roof edges | 30–50 m |
| Perimeter drainage pipe | 4" perforated | 15–25 m |
| Gravel for drainage | Washed | 1–2 m³ |
| Geotextile | Drainage wrap | 20–30 m² |

---

## 11. Fasteners + consumables

| Item | Quantity |
|---|---|
| Structural bolts M12–M16 | 150–220 units |
| Self-drilling screws for steel | 300–500 units |
| Roof screws / clips | 500–700 units |
| Deck screws | 600–800 units |
| Wood screws | 800–1,200 units |
| Welding electrodes / wire | 1 lot |
| Grinding / cutting discs | 20–40 units |
| Silicone / polyurethane sealant | 20–30 tubes |
| Flashing tape | 30–50 m |
| Construction adhesive | 10–20 tubes |

---

## 12. Summary totals

| Category | Total |
|---|---|
| Total elevated platform area | 42 m² |
| Enclosed cabin area | 30 m² |
| Terrace area | 12 m² |
| Total steel length | ≈ 499 m |
| Estimated fabricated steel weight | ≈ 3.8 – 4.0 tons |
| Roof area to order | ≈ 82 m² |
| Floor system to order | ≈ 33 m² |
| Decking to order | ≈ 14 m² |
| Front glazing | ≈ 23 m² |
| Rear gable wall | ≈ 20.5 m² |
| Rock anchors | ≈ 42 units |
| Base/cap plates | ≈ 20 units |
| Railing length | ≈ 11 m |

---

## 13. Simplified procurement list (for contractor quotation)

| Package | Quantity |
|---|---|
| Fabricated steel structure | 3.8–4.0 tons |
| Steel base plates + connection plates | 1 lot |
| Rock drilling + chemical anchoring | 42 anchors |
| Elevated floor structure | 42 m² |
| Interior structural floor panels | 33 m² |
| Exterior deck boards | 14 m² |
| A-frame metal roof system | 82 m² |
| Roof insulation + membrane | 82 m² each |
| Interior wood ceiling lining | 82 m² |
| Front glass façade | 23 m² |
| Rear wall cladding + insulation | 20.5 m² |
| Terrace railing | 11 m |
| Access stair | 1 unit |
| Drainage + waterproofing | 1 lot |
| Electrical + plumbing rough-in | 1 lot |

---

## Next step

Convert this into a **structural cut plan**: exact column heights from a terrain survey, exact rock anchor positions, exact steel member sizes after load calculations (wind / seismic / live / dead).
