# Villa — landscape and external works specification

Plot **24.0 × 29.0 m = 696 m²** (7,494 sq ft). House footprint **226.3 m² = 32.5 %
coverage**, measured off the wall polygons rather than typed in. Open ground
**≈ 470 m²**. Every dimension below is taken from
`villa_design.py`, which is the single source of truth; where this document states a
*range*, that is a researched target the design is checked against, and the design's
own figure is given beside it.

Levels: street **±0**, finished floor **+900**, pool top water **+700**, pool floor
**−700**, catch-basin invert **−1400**, plant-room floor **−2800**.

---

## 1. Three outdoor rooms

The plot is not a garden with a house in it. It is three outdoor rooms in a line,
north to south, each with a different job and a different floor level:

| | Extent (mm, y) | Size | Level | Job |
|---|---|---|---|---|
| **Arrival forecourt** | 23,400 → 28,600 | 5.2 × 7.2 m | ±0 → +900 | car, gate, compression |
| **The house** | 11,000 → 24,000 | 226.3 m² | +900 | — |
| **Pool garden** | 0 → 11,000 | ≈ 264 m² | +700 / +900 | release, water, sun |

The sequence is the point: **compress, release, compress, release.** Street → 2.2 m
gate reveal → open forecourt → 2.4 m entry loggia → 6.4 m double-height hall. The
researched threshold for compression to *register* is a ratio of at least **1 : 2.2**
between the compressed and released soffit; 2.4 m into a 6.4 m void gives **1 : 2.67**.

---

## 2. Arrival

**Vehicle gate** clear opening **5,600 mm** (x 4,200 → 9,800). Researched minimum
3.5 m, comfortable 4.0–4.5 m; this is generous because it doubles as the service
opening. Cantilever slider — run-back required is opening + 500 = **6,100 mm** along
the inside face of the north wall, which the forecourt provides.

**Pedestrian gate** 1,200 mm at x 15,400 → 16,600, on the majlis side, so a women's
majlis guest arrives without crossing the car court.

**Standing space** between gate line and street: the research asks **5.5–6.0 m**; the
plot gives **5,200 mm**. This is the one dimension in the scheme under its comfort
target, and it is a deliberate trade — the alternative was shortening the pool below
6.0 m, at which point the water stops reading as a pool and starts reading as a spa.
A car fits. A large SUV parks with roughly 200 mm to spare rather than 800.

**Turning.** A 13–15 m circle to exit forwards does not exist on a 29 m plot with a
house on it. Accept one straight reversing movement and shape the apron for it: no
planter, no step, no bollard inside the swept path x 3,400 → 10,600, y 23,400 →
28,600.

**Surface.** Sawn basalt setts 200 × 100 × 60 mm on a rigid bed, laid to a **1.5 %
fall** to a slot drain on the gate line. Setts, not slabs — the joint pattern absorbs
the settlement a driveway gets and a 600 × 600 porcelain slab does not.

---

## 3. The pool

**6,000 × 6,600 mm = 39.6 m² water**, constant depth **1,400 mm**, volume ≈ **55 m³**.

Two honest notes. First, the researched water surface for a plot this size is
**45–50 m²** (about 10 % of plot); at 39.6 m² this pool is ~15 % under that, because
the 1,200 mm terrace on the house side was treated as non-negotiable. Second, at
6.6 m in the swimming direction it is **not a lap pool** — the research line is ≥ 12 m.
This is a swimming-and-sitting pool and should be described that way rather than sold
as something it is not.

### Overflow edge

South edge is the vanishing edge; the other three are deck-level slot.

- Crest set **4 mm below top water level** (+700 → crest +696). Research band is
  **2–6 mm**; that differential, not the pump, sets sheet thickness. A 25 mm error
  destroys the effect.
- **Level tolerance ±0.8 mm over the whole perimeter.** Set with a rotating laser
  during the pour and *again* at tiling. This single number decides whether the pool
  works.
- Crest stone: dense machined granite **40 mm**, 6 mm radius on the leading arris,
  bedded falling away from the water.
- Weir wall RC **250 mm at the crest**, widening to 400 mm at base.
- Deck-level sides: slot **20 mm**, gutter **100 × 100 mm** minimum, fall **1:48**,
  drop pipes **90 mm at 1,500 mm centres**, vents 38 mm.

### Catch basin / balance tank

One chamber, not two — on a plot this size that is the right move. The basin runs the
full pool width + 800 mm, y 2,000 → 3,200, invert **−1,400**, i.e. **2,100 mm below
top water level**, which gives gravity fill and flooded suction.

Sized by building it up rather than by a rule of thumb:

| Component | Litres |
|---|---|
| Bather displacement, 8 people @ 70 L | 560 |
| Water in transit, ≈ 26 m of gutter | 650 |
| Backwash | 1,000 |
| Start/stop surge | 300 |
| **Subtotal** | **2,510** |
| Cross-check: 40.7 L/m² × 39.6 m² | 1,612 |

Take the larger: **working volume 2,600 L**, plus 200 mm freeboard and a 180 mm
low-level cut-out. Autofill solenoid and float switch go **on the tank, never on the
pool**. Evaporation in a hot-dry climate is **5–10 mm/day** = **200–400 L/day** at
this surface, so the autofill is not optional.

### Plant

**The overflow pump is always separate from the filtration pump.** Flow for a thin
sheet is **40–60 L/min per linear metre** of crest; 6.0 m of crest → **240–360 L/min**
(confirm with the pool engineer). Catch-basin water level **150–300 mm below the
crest** so return water is neither seen nor heard.

Plant room at **−2,800**, minimum **12 m² clear at 2.4 m height**, pipe run under
15 m. It needs a floor gully — *the room will flood* — a 1.0 m clear door, mechanical
ventilation, and **acoustic separation from every bedroom and from the majlis**. Do
not share a wall.

### Structure

**The 45° load-spread rule governs.** The pool shell must not intrude into a plane
drawn at 45° up from the bottom outside edge of the adjacent footing. As drawn the
pool sits x 9,000 → 15,000 with boundaries at 0 and 24,000 — clear by 9 m either
side. The constraint that actually bites is the **south** boundary at y 0 against the
basin at y 2,000: **2,000 mm clear ground**, satisfied.

Shell RC **250 mm**, C32/40 with waterproofing admixture, **50 mm cover** to the
earth face, crack width **≤ 0.2 mm**. Never rely on tile adhesive as waterproofing.

### Finish

Interior in **dark grey-green glass mosaic, 25 × 25 mm**. Not blue. A dark tank
reflects the sky and the house; a blue one reflects nothing and reads as a hotel.

Reflecting geometry: for the house to read fully in the water, the pool must extend
toward the viewer by at least the apparent height of the house from that viewpoint.
From the south terrace, 6.6 m of water against a 7.8 m parapet returns roughly 85 %
of the elevation — enough that it reads, short enough that it is worth knowing.

---

## 4. Terrace and rill

**Pool terrace 1,200 mm** between the house face and the water on the north side. The
researched minimum is 1,200 for a back side and 1,500 where people walk — this is a
back side, and the lounging is on the east, where the garden opens to **3,800 mm**.
A 600 mm coping walk is a developer's pool; 1,200 is the floor of acceptable.

**Axial rill 600 mm wide** on the centre line at x 12,000, running from the entry
loggia through the house line to the pool head. Depth **75 mm over a black-finished
slab** — darkness and stillness make a mirror, not depth. Turnover every **2–4
hours**, submerged low-velocity inlets, **no visible jets, no audible splash**,
automatic float valve. A rill that drops 5 mm reads as broken.

---

## 5. Planting

Hot-dry, walled, no view. The planting has one job: make shade, and make the walls
disappear.

| Zone | Species | Size at planting | Note |
|---|---|---|---|
| Forecourt, 2 no. | *Prosopis cineraria* (ghaf) | 400–450 mm girth | Open canopy; keeps the gate sightline |
| Pool garden, 3 no. | *Phoenix dactylifera* | 4.0–4.5 m clear trunk | Set **off** the pool edge — leaf litter |
| East strip | *Bougainvillea glabra* on stainless cable | 3 L | Breaks 24 m of unrelieved stone |
| Courtyard | 1 no. *Ficus altissima* | 300 mm girth | Needs **4 × 4 m and 1.0–1.2 m soil depth** |
| Ground plane | *Zoysia matrella* / gravel mulch | — | Turf only where it is walked on |

Irrigation: sub-surface drip throughout, **a separate zone per planting type**,
pressure-compensating emitters, controller in the plant room. No spray heads anywhere
near the pool or the stone.

---

## 6. Boundary wall

**350 mm overall** — blockwork core with **40 mm stone both faces**. Height **2,400 mm**
to side and rear; the north run steps down to **2,000 mm** with the top 400 mm as a
bronze-finished screen, which is both the common planning requirement and the more
civil thing to do to a street.

- Piers at **3,500 mm** centres.
- Movement joint every **7,000 mm** — a 24 m run without one *will* crack.
- Coping **150 mm** with a **6 mm drip groove** set 20 mm back from the face.
- At every external corner, a **rebated return stone 150 mm deep** so no 40 mm arris
  is ever visible. This is the detail that separates a stone wall from a wall with
  stone stuck on it, and it costs almost nothing.

---

## 7. External lighting

One rule: **no light source visible from the house, and no fitting above eye level in
the garden.**

| Element | Fitting | Output |
|---|---|---|
| Boundary wall | Recessed linear grazer at base | 4 W/m, 3000 K |
| Trees, 5 no. | In-ground uplight, 20° spot | 9 W, 3000 K |
| Pool | Two niches on the **north** wall firing south | 30 W, 3000 K |
| Crest | Nothing. A lit vanishing edge looks like a swimming pool | — |
| Steps, terrace | Under-nosing LED in a 20 mm shadow gap | 3 W/m, 3000 K |
| Forecourt | Bollard-free; wall-recessed at 400 mm AFL | 3 W, 3000 K |

All on one DALI controller with four scenes — **arrival, evening, dining, away**.
Colour temperature is 3000 K everywhere and never varies. Mixed colour temperature
outdoors is the most common and most visible fault in a built villa.
