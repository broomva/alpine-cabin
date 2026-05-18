# NOTES — Decision log, open questions, milestones

## Milestones

| Milestone | Deliverables | Status |
|---|---|---|
| **M0 — Spec + BOM** | README, SPEC, BOM, SITE, REFERENCE, LICENSE, reference images | **In progress (this commit)** |
| M1 — Site survey | Topo survey, geotech report, GPS-marked rock positions, photo set | Backlog |
| M2 — Structural engineering | Stamped drawings, load calcs, splice details, anchor spec, MEP rough-in plan | Backlog (blocked by M1) |
| M3 — Procurement + fabrication | Final cut list, steel order, glass order, deck/roof order, fabrication QA | Backlog (blocked by M2) |
| M4 — Build | Anchor drilling, column erection, platform, A-frame, envelope, finishes | Backlog (blocked by M3) |
| M5 — Build log + retro | Daily photos, deviations from spec, retrospective | Concurrent with M4 |

## Open questions

1. **Site location** — GPS coordinates not yet recorded. Affects seismic zone, wind load, permit jurisdiction, prevailing wind, sun path.
2. **Rock survey** — visible rocks may not all be structurally sound. Need geotech assessment + sound test before finalizing column positions.
3. **Permit jurisdiction** — local building code lookup pending.
4. **Material delivery** — access road suitability for steel-truck. Steel members up to 12 m may be required (rafters) or accept splicing.
5. **Power + water** — off-grid or grid-connected? Affects floor + envelope penetrations.
6. **Wood stove model** — chimney diameter + clearance affects roof penetration sizing.
7. **Front gable orientation** — view vs. wind vs. solar gain; site visit needed to decide.
8. **Loft access** — ladder, alternating-tread stair, or stair? Affects building code compliance (egress).

## Decision log

| Date | Decision | Rationale |
|---|---|---|
| 2026-05-18 | Open-source from day 1 under CC-BY-SA-4.0 | Maximize learning + reuse; the design isn't proprietary, the rocks under it are |
| 2026-05-18 | 9 columns in 3 × 3 grid | Matches visible rock cluster; one column per peña; allows variable column heights |
| 2026-05-18 | A-frame portals every 1.0 m (6 portals) | Conservative spacing for a steep-slope roof in a windy alpine site; engineer may relax |
| 2026-05-18 | Rafter 6.89 m — accept splicing as an option | Standard 6 m stock + 1 m splice OR custom 12 m stock; final call deferred to engineer |
| 2026-05-18 | Floor-to-ceiling front glazing, slim wood trim base | Aesthetic non-negotiable; engineer designs around it |
| 2026-05-18 | Chimney exits rear slope, not ridge | Preserves clean front gable; pays for flashing complexity |
| 2026-05-18 | BOM is preliminary, not procurement-ready | All quantities subject to structural engineer + site survey |

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Rock fracture under load | **High** | Geotech survey at every column position; reject unsound rock; relocate columns if needed |
| Steel corrosion in humid alpine site | High | Galvanize OR epoxy primer + polyurethane finish; inspect annually |
| Wind uplift on steep glass gable | High | Engineer designs glazing + frame anchors for site-specific wind load |
| Water intrusion at roof / glazing junction | High | Continuous flashing; sealant; quality control at install |
| Splice failure at rafter midpoint | Medium | Engineered bolted/welded splice with NDT, OR avoid by ordering 12 m stock |
| Anchor pull-out from rock | Medium | Chemical anchors with pull-test verification; minimum embedment per geotech |
| Deck rot at terrace junction | Medium | Treated wood; drip edge; annual sealer |
| Construction crew unfamiliar with rock anchoring | Medium | Contract drilling specialist for anchor phase |
| Permit denial | Medium | Pre-application consult with local authority |
| Budget overrun on steel | Low-Medium | Lock steel price early; accept ±15% on quantities |

## Contributions welcome

Issues + PRs especially valued for:

- **Engineering review** of the BOM (anyone with structural credentials).
- **Build-log photos** from anyone replicating the design — we'll merge them into a `builds/` showcase.
- **Localized cost data** — what does 4 tons of fabricated steel cost in your country?
- **Alternative material substitutions** — what works in your climate that doesn't work in ours, and vice versa?
