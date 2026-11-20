# Villa design critique - full agent findings

Extracted from the workflow journals of the six-lens adversarial
critique. Roughly **7.4M agent tokens** across two runs produced
this. Journals: wf_69b7b587-078, wf_bfc60f4e-52c

- distinct findings raised: **160**
- verdicts returned: **78** (60 upheld, 18 refuted)

> **Meta-lesson, worth more than the findings themselves:** nearly
> every item below is *mechanically detectable*. Room areas are
> arithmetic. Inner rooms and unreachable volumes are a reachability
> graph over door openings. Bathrooms-per-bedroom is counting. A
> validator finds these for free on every run, in milliseconds.
> Agents should be spent on judgement that cannot be computed --
> does the elevation read as architect-designed, is the concept
> actually delivered -- not on arithmetic.


---

## Findings by severity

### 1. The west brise-soleil shades a blank wall -- there is no window behind it

**Severity:** FATAL

**Numbers:** Fins: 9 no. @ 600 c/c, 180 x 450, z 900-8700. Wall behind: 5500 x 7800 = 42.9 m2, zero openings. East wing east wall: 42.9 m2, zero openings.

**Evidence:** Lines 186-189 place 9 fins at x 2300-2750, z 900-8700, in front of the west wing's west wall (x=3000, y 12500-18000). I traced every void in the V list: nothing cuts that wall. The clerestory at line 176-178 uses xx=HX0 but spans y 18800-23200, which is the NORTH BAR, not the wing. So the fins stand in front of 5.5 x 7.8 = 43 m2 of 100% solid wall. This is the first thing an experienced architect will spot and it invalidates the whole west facade as a considered move. Worse, both wing end-walls are blank: the east wing's east wall (x=21000, y 12500-18000) has no opening either -- the service door at line 183 is in the north bar. Two of your four elevations are dead, which is why all the compositional load has fallen onto the south and why the south is over-punched.

**Proposed fix:** Either delete the fins entirely and recess the west glazing plane 1800 mm behind the wall face (x=3000 face, glass at x=4800) to make a full-height loggia 1800 deep x 5500 long -- the 400 mm wall plus 1800 recess gives 2200 mm of self-shading, costs nothing and is the correct Gulf answer -- or keep fins and cut a real opening: 3600 w x 2400 h per storey in the west wall at z 1400-3800 and 5600-8000. Do the same on the east wing east wall. Non-negotiable: nothing gets a shading device unless there is glass behind it.

### 2. The south elevation is a mirrored A-B-A with four identical punched squares -- the developer signature

**Severity:** FATAL

**Numbers:** Current wing face 5000 x 9400 = 47.0 m2, openings 6.89 + 5.85 = 12.74 m2 = 27%; south WWR 38% GF / 37% FF against the ECBC <30% the research cites. Proposed: 4800 x 9400 = 45.1 m2, opening 7.9 m2 = 17.6%.

**Evidence:** Bay rhythm is 5000 : 1000 : 6000 : 1000 : 5000. The centre is only 1.2x the wings -- too close to read as dominant, too far to read as equal, so the eye reads 'symmetrical and slightly off'. Openings (lines 173-175): every wing gets 2600 x 2650 on the ground and 2600 x 2250 on the first, stacked in perfect vertical alignment, mirrored left-right. That is a 2x2 grid of near-squares (1:1.02 and 1:1.16) -- the exact elevation of a spec house. Nothing in the composition has hierarchy: no dominant void, no dominant solid, every part doing the same amount of work. The only asymmetry in the entire elevation is accidental: the fins project 450 mm west of the mass (line 189) so the south elevation has a 450 x 7800 sliver hanging off the left side and nothing on the right. That reads as a modelling error, not a move.

**Proposed fix:** Re-cut the bays asymmetrically on a 600 module: west wing 4800 | slot 1800 | centre 6000 | slot 1200 | east wing 4200 = 18000. Centre now 1.25x and 1.43x the wings -- legibly dominant, and the elevation is no longer a face. Then delete all four square windows and cut ONE opening per wing: 1200 w x 6600 h (z 1400-8000), a vertical incision through the floor line, glass in a single plane recessed 400. Ratio 1:5.5. Two strong verticals against the horizontal cantilever, in a large stone field. Wing face void drops from 27% to 18%.

### 3. The cantilever is deeper than it projects and is invisible in the south elevation

**Severity:** FATAL

**Numbers:** Current 3000 out : 4200 deep : 5800 tall front plane = 0.71:1. Proposed 4200 out : 3700 deep, 2400 mm step past a 1800 mm wing overhang. Required south overhang per research at 25N: 0.6-0.8 x 2650 opening = 1590-2120 mm; currently 0.

**Evidence:** CANT = 3000 (line 99), but the cantilevered element runs z 4500 to 8700 = 4200 mm deep, plus a flush 1100 parapet on top taking the front plane to 10300. So the projecting mass is 3000 out and 5800 tall -- it reads as a squat bay window or a lump, not a cantilever. A cantilever registers as a cantilever at roughly 3:1 length-to-depth; this is 0.71:1. Second failure: the wings do not project at all, so in orthographic south elevation the 3.0 m step is completely invisible (no shade, no hidden lines). The scheme's headline move does not appear in the scheme's primary elevation. Third: the cantilever front face at y=9500 runs flush and unbroken from soffit 4500 to parapet top 10300, 5800 mm of dead plane, which is precisely what kills the read. Fourth: the first-floor front (lines 148-149) is cut through to the front face, leaving a 5200 x 3700 open hole with no glazing and no 1100 guarding.

**Proposed fix:** Three planes stepping out, 1200 apart: extend the first-floor slab 1800 mm south over BOTH wings (new solid blk(WW_X0, WG_Y0-1800, GF+GF_CH, WW_X1, WG_Y0, FF) and the east equivalent) -- this also gives the south windows the 1600-2100 mm overhang the research demands at 25 degrees N and which currently does not exist at all; push CANT to 4200 (still RC, ~450-500 mm effective depth per the Eurocode note in the research); and hold the roof slab back at the wing line. Then thin the cantilever edge: 300 mm slab edge with a 20 mm drip and shadow gap, and set the parapet back 900 mm from the cantilever face as a recessed glass balustrade so the projecting plate reads thin. Result: 6000 wide x 4200 out x 3700 deep, wider than it is deep, 2400 mm proud of the wings.

### 4. The overflow does not exist: the basin void subtracts zero material

**Severity:** FATAL

**Numbers:** Basin void y-range 1600-2600 mm; pool shell south face y = POOL_Y0-400 = 2600 mm. Boolean overlap measured as (x, y, z) = (5800, 0.0, 1540) mm -- zero in y.

**Evidence:** villa_3d.py:195-196 cuts blk(POOL_X0-400, POOL_Y0-1400, -900, POOL_X1+400, POOL_Y0-400, POOL_TW-60), commented "spill + basin". Its north face lands at y=2600, which is exactly the outer face of the shell built at line 192-193 (blk spans y 2600-12900). The two solids abut on a plane of zero thickness, so the subtraction removes nothing. Nothing else in the file is a ground solid, so the cut also carves no basin out of the earth. Result: the built model is a closed box, shell y 2600-12900, x 9100-14900, z -1100 to +700, with a continuous flat 400 mm rim at +700 on all four sides. There is no weir, no crest, no lip, no gutter, no basin, no spill face anywhere in the geometry. Every drawing the script derives -- plans, section AA on the water axis, POOL_EYE perspective -- will show a plain raised tank. The single conceptual move the docstring builds the whole water design on (lines 17-22) is absent from the thing that gets drawn.

**Proposed fix:** Model the weir explicitly, not as a near-miss cut. Extend the basin void north to y = 2900 so it overlaps the 400 mm south wall by 300 mm, and set its top to POOL_TW - 5 (695) so the crest sits 5 mm below the water line (research: crest 2-6 mm below required water level). Then add the basin as a separate cut into a modelled ground solid: x 9100-14900, y 1400-2600, invert -900, with a 200 mm upstand back to grade. Re-cut the pool water void so its south face stops at the crest, and add the 400 mm-wide spill wall as its own block so section AA shows the sheet path.

### 5. No crest differential: all four rims at +700, so the pool overflows toward the house

**Severity:** FATAL

**Numbers:** Rim level +700 mm on all four sides. Ground-floor FFL +900 (GF), glazing sill +1000 (GF+100, line 169). Freeboard from pool water to interior floor = 200 mm; to glazing sill = 300 mm. Research tolerance ±0.8 mm over the whole perimeter; typical achieved ±3-5 mm.

**Evidence:** The shell solid (line 192-193) tops out at POOL_TW = 700 uniformly, and the water void (line 194) is cut to POOL_TW+100, so the shell's top face is a flat 400 mm band at exactly +700 on all four sides. Nothing tells the water which side to leave by. Research §3 requires the vanishing-edge crest to sit 2-6 mm below the required water level and states "a 25 mm error destroys the effect" and "LEVEL TOLERANCE ±0.8 mm OVER THE WHOLE PERIMETER... This number decides whether the pool works." With no designed differential, the pool spills on whichever of its 29 m of perimeter construction tolerance leaves lowest. The worst case is the north rim: it abuts the living-volume face at y 12500 with no surround, no gutter and no drainage, and discharges 700 mm above the garden straight down the building face onto the ground-floor slab edge, 200 mm below the finished floor inside.

**Proposed fix:** Hold three sides 15-20 mm above the design water line as a true coping with a 10-15 mm shadow gap to the deck, and drop only the spill crest to +695. Independently, raise the whole pool or drop the water: a 200 mm differential between pool water and interior FFL is not a defensible flood margin for a tank holding 66.5 m³. Either lower POOL_TW to +450 (which also buys the seat-height edge the research names) or set the north rim as a 150 mm-high solid upstand with a drained channel between the pool and the building line.

### 6. Pool shell is fused into the house ground-floor slab -- a tanked structure with no isolation joint

**Severity:** FATAL

**Numbers:** Measured interpenetration of the pool shell solid and the living-volume ground slab: 5800 × 400 × 300 mm (x, y, z), at y 12500-12900, z +400 to +700.

**Evidence:** Shell spans y 2600-12900 (line 192-193, POOL_Y1+400). The living volume ground slab is blk(LV_X0, WG_Y0, GF-SLAB, LV_X1, WG_Y1, GF) = y 12500-18000, z 400-900 (line 134). The union at line 213 silently welds them. As built that means the pool's north wall -- a water-retaining element the research requires at crack width ≤ 0.2 mm, fully tanked, with a drained cavity and leak detection -- is cast monolithically into the slab and foundation zone of a two-storey wing that also carries the 3.0 m cantilever. There is no movement or isolation detail at the perimeter, which research §3 lists as mandatory. Consequences: the pool's shrinkage and thermal movement crack the building slab, the building's differential settlement cracks the pool, and any leak in the north wall reports into the house foundation rather than into a detectable cavity. It also leaves the pool with zero surround on its north side against the research minimum of 1.2 m on back sides.

**Proposed fix:** Pull POOL_Y1 back to 11800 so the shell's north face lands at 12200 and leaves 300 mm of clear gap to the building line at 12500, then detail that gap as a compressible isolation joint with a drained cavity and leak-detection channel discharging to the balance tank. That loses 700 mm of pool length, which the pool cannot afford -- so take it back at the south end by moving POOL_Y0 to 2300 (still 1.95 m clear of the boundary wall footing zone).

### 7. The single water axis does not exist: two unrelated water bodies at two different levels with 11.5 m of solid house between them

**Severity:** FATAL

**Numbers:** Rill 3.9 m at +150; pool 9.5 m at +700; level difference 550 mm; solid house on the axis 11.5 m. Axial water 13.4 m of 25.65 m available = 52%. Court of the Myrtles = 93%.

**Evidence:** villa_3d.py:199-202 builds the rill only from y=24400 to y=28300 -- 3.9 m, entirely in the forecourt, north of the house -- with its top at STREET+150. The pool (lines 93-94, 192-194) runs y=3000 to 12500 with POOL_TW=+700. Between them the house is continuous solid from y=12500 to y=24000. No rill geometry exists anywhere inside the house, and no rill geometry exists between the house and the pool. The two water surfaces are 550 mm apart in level. So the docstring claim (lines 29-32) 'the axis is carried the LONG way by a 500 mm rill... terminating in the swimming pool' is a caption over geometry that does the opposite: the model contains a short trough in a driveway and, 11.5 m away and 550 mm higher, a swimming pool.

**Proposed fix:** Make it one water plane at one datum. (1) Set the rill top water to POOL_TW (+700), not +150 -- that single number is why the two can never read as one body; the pool sits 200 mm below the GF floor at +900, so a rill at +700 holds the identical relationship all the way to the gate. (2) Run the rill as one uninterrupted S/V pair from y=28300 to y=12500 at x=AXIS±250, i.e. through the forecourt, through the north bar, through the living volume, and over the pool head as a chadar. (3) That requires the north bar to be cut open on the axis -- cut V blk(10500, 17600, GF, 13500, 24400, FF) so the axis passes through an open-air entry court between two masses (garage 3000-10500, service/stair 13500-21000) and the first floor bridges over it (F.LOT's glazed bridge). Cost 19 m2 of ground floor; recover it by extending the wings or the roof enclosure. Result: 15.8 m of rill + 9.5 m of pool = 25.3 m of continuous water on 25.65 m of available axis = 99%, against the Alhambra's 93%.

### 8. The perspective from the gate dies 10.2 m in, at an 800 mm wall with no opening in it

**Severity:** FATAL

**Numbers:** 800 mm of solid wall on the axis, 0 openings. Uninterrupted perspective delivered 10.25 m of 25.65 m available.

**Evidence:** The living volume's north wall (y 17600-18000, line 137) and the north bar's south wall (y 18000-18400, line 137) stack to 800 mm of solid concrete across the entire width of the house. I searched every V entry in build(): there is not one opening cut anywhere in that plane. The entrance hall and the living room are sealed from each other. The sightline from the gate face (y=28650) therefore terminates at y=18400, 10.25 m in, with 14.5 m of plot still to go. Casa Merida's move -- the thing being quoted -- is an 80 m uninterrupted perspective from the entrance door to the pool. Here it is 10.25 m, and only if you are standing on the axis, which the gate does not let you do (see the arrival finding).

**Proposed fix:** Cut the axis open, at a width that reads as a room not a door: V blk(AXIS-1500, 17600, GF, AXIS+1500, 18400, GF+GF_CH) at minimum, and preferably the full-height version described above so the axis is a void through the mass rather than a hole in a wall. Then verify with a real ray, not a caption: put an eye at (12000, 28300, 1600) and confirm it reaches (12000, 8000, 700) through air only. That test -- gate to water, one straight line, nothing in it -- is the whole scheme; run it as an assertion in build() so it cannot silently break again.

### 9. Every garden-facing opening stops 100 mm short of breaking through; the entire pool facade is solid

**Severity:** FATAL

**Numbers:** Cut ends y=12800; inside wall face y=12900; residual skin 100 mm on 3 of 3 south openings. Real openings in the completed model: front door, 2 garage doors, 1 service door, 2 clerestories. Zero on the south.

**Evidence:** The south walls of the living volume and both wings span y=12500 to 12900 (WG_Y0 to WG_Y0+WALL). The 'structural glazing' cut (lines 169-170) ends at WG_Y0+300 = 12800. The two wing window cuts (line 174) also end at 12800. All three therefore leave a continuous 100 mm skin of solid material across the full width of every opening. The first-floor cut (line 171-172) uses WG_Y0+WALL+300 = 13200 and does penetrate -- proving the pattern is a slip, not a convention. Consequence: in the model the whole garden and pool elevation of this house -- the money shot, the one facade the $5M is being spent on -- has no opening in it at all. VILLA_SECTION_AA.dxf on the water axis will show the living volume as a closed box facing the pool, and VILLA_ELEV_S.dxf will show a blank wall. The double-height space is simultaneously wide open above 4.5 m (see separate finding), so the drawings read as a sealed room under an open shaft: the exact inverse of the intent.

**Proposed fix:** Change the three south cuts to terminate at WG_Y0 + WALL + 300 (13200), matching line 172. While there, the glazing head at GF+3400 sits 200 mm below the 3600 soffit -- take it to GF+GF_CH so the glass meets the slab and the corner reads as structural glass with no head trim, which is the detail the research calls the single most legible architect signal.

### 10. The sunken courtyard is roofed over -- the basement gets zero daylight

**Severity:** FATAL

**Numbers:** Court 5.0 x 4.0 m, void -2800 to +1100 = 3.90 m. Aperture to sky: 0 m2. Roof slab 8700-9200 continuous over the full 5.0 x 4.0 m footprint. Basement net internal 121 m2 (17.2 x 8.2 less the court), all of it unlit.

**Evidence:** villa_3d.py:127 cuts the court void only from BASE_FL (-2800) up to GF+200 (+1100). Line 154 then lays a continuous roof slab over x 3000-21000, y 9500-24000 at z 8700-9200, and nothing cuts it except the two light slots (x 8000-9000 / 15000-16000). The court at x 9500-14500, y 15400-19400 sits under solid ground-floor structure, under the double-height void, and under an unbroken roof slab. It is a hole in the ground floor, not a light court. The single research move that 'makes a basement a served space, not a cellar' (VILLA_RESEARCH.md, F.LOT) is absent from the model.

**Proposed fix:** Carry the court void up through every level to the sky: extend the CT void to RF+SLAB+PARAPET (as the light slots already do at lines 163-166), and pull the roof slab and the roof pavilion (PV = 9000,19000,15000,24000, which overlaps the court at y 19000-19400) clear of x 9500-14500, y 15400-19400. If the court must stay covered at ground level, replace it with a 5.0 x 4.0 m structural rooflight and accept that it is a lightwell, not a courtyard.

### 11. The courtyard hole guts the living volume and severs the entry axis, with no bridge and no guarding

**Severity:** FATAL

**Numbers:** Living-volume floor: 5.2 x 4.7 = 24.4 m2 gross interior, minus 5.0 x 2.2 = 11.0 m2 of court = 13.4 m2 remaining, in a strip only 2.5 m deep (y 12900-15400). Against a 7.80 m clear height that is 7.80 : 2.50 = 3.1 : 1 -- a shaft by the research's own test, not a room. Axis gap 4.0 m; unguarded drop 3.70 m; guarding required 1100 mm (VILLA_RESEARCH.md s.6).

**Evidence:** The court (x 9500-14500, y 15400-19400) is punched straight through the ground-floor slab on the axis. The living volume's interior is x 9400-14600, y 12900-17600; the court removes y 15400-17600 across 5.0 of its 6.0 m width. The north bar's interior runs y 18400-23600; the court removes y 18400-19400. Walking south from the guest entrance at y 24000 you get 4.2 m of hall floor and then a 4.0 m gap with a 3.7 m drop, and no bridge is modelled. The court also occupies 5.0 m of the 6.0 m wide junction between the north bar and the living volume, so there is no floor to put a door onto. Section AA is cut at x 12000 -- dead through the middle of this -- so the drawing that is meant to sell the scheme is the drawing that shows it.

**Proposed fix:** Either (a) move the court off the axis and out of the living volume -- put it at x 4000-9000 or 15000-20000 under the north bar, where it lights the basement without eating the piano nobile -- or (b) keep it on the axis and bridge it, F.LOT's 'bridge encased in sliding glass': a 6.0 m wide slab from y 17600 to 19400 with a 1.0-1.2 m glass balustrade to the void each side. Option (b) is the better drawing but it costs the living volume 11 m2 of floor unless the LV band is deepened.

### 12. No opening in the model penetrates its wall -- every door and window leaves a 100 mm leaf

**Severity:** FATAL

**Numbers:** Wall 400 mm; opening overshoot 300 mm; residual leaf 100 mm on 9 of 11 openings. Glazed area actually cut through the envelope: 5.72 m2 of clerestory on a 407 m2 GFA = 1.4%. Research target WWR <30% is a ceiling, not a floor.

**Evidence:** WALL = 400 mm (line 79) but every opening void is cut with only a 300 mm overshoot past the outer face. Line 169-170, the 'structural glazing' to the garden: y 9200 to 12800, against a south wall occupying y 12500-12900 -- 100 mm of wall survives across the whole opening. Same at lines 173-175 (both wing ground windows and both wing first-floor windows, y 12200-12800), line 179-180 (guest entrance, y 23700-24300 against a wall at 23600-24000), lines 181-182 (both garage doors), lines 183-184 (service door, x 20700-21300 against a wall at 20600-21000). Nine of the eleven opening cuts leave a 100 mm skin; only the two clerestories (lines 176-178, correctly cut 2900-3600 and 20400-21100) and the internal window onto the void (line 171-172) actually go through. The house as modelled is a sealed box: every elevation, the long section and all three perspectives will render a blank facade, and the 'structural glass corner' the research calls the single most legible architect signal is not there.

**Proposed fix:** One-line fix: change every +/-300 overshoot to +/-500 (or define OVER = WALL + 100 and use it), so each void clears the 400 mm wall at both faces. Then re-cut and re-check the south elevation and section AA -- they are currently passing only because the wall was never opened.

### 13. The fourth bedroom cannot be reached -- the cantilever is a marooned platform, open at both ends

**Severity:** FATAL

**Numbers:** Cantilever internal 5.2 x 3.0 = 15.6 m2 net / 18 m2 counted GFA. Gap to nearest first floor: 5.1 m (y 12900 to 18000). Drop to living-room floor 4.100 m; to pool water 4.300 m. Honest GFA without it: 407 - 18 = 389 m2 = 4,187 sq ft, 7% under the 418 m2 / 4,500 sq ft brief.

**Evidence:** villa_3d.py lines 140-151. The first-floor loop builds solids only over the north bar and the two wings. The cantilever is a separate block at x 9000-15000, y 9500-12900 (line 147-148). North of it, the living volume is void through both storeys (line 151), a 5.5 m gap to the north bar's first floor at y 18000. East and west of it, the 1.0 m light slots (lines 163-166) are cut full height from GF-SLAB to the top of the parapet, so it never touches the wings. Worse, its north wall (y 12500-12900) is entirely removed by the FF glazing void (line 171-172, y 12200-13200) and it has no south wall at all (the void at line 149 starts at y 9500, the outer face). So it is a 5.2 x 3.0 m slab with two side walls, open at the north over a 4.1 m drop into the living room and open at the south over a 4.3 m drop into the pool, with no stair, bridge, corridor or guarding. It is counted as 18 m2 of GFA (line 219, `ct`). Delete it and the villa has three reachable bedrooms against a four-bedroom brief.

**Proposed fix:** Either bridge it (a 1.4 x 5.1 m glazed bridge from the north bar, the F.LOT move -- but that costs 7 m2 and cuts the double-height volume into two 2.5 m strips), or stop counting it as GFA and re-declare it as an external shade canopy over the pool. If it is to be the fourth bedroom it needs the first floor over the living volume reinstated, which kills the double-height.

### 14. Ground floor is 48 m2 short of the minimum brief programme, and no room in the villa can be 35 m2

**Severity:** FATAL

**Numbers:** 137.4 m2 available vs 185.0 m2 required = 47.6 m2 short (35% over capacity). Largest contiguous room after the north bar's fixed content: 19.74 m2. Family living minimum 35 m2 -- 44% short. Site coverage is only 28% of a plot where 18 x 21 = 378 m2 is buildable; the scheme uses 52% of its own envelope while running 48 m2 short.

**Evidence:** Net internal after 400 mm walls (WALL, line 79) and after the sunken-court hole: north bar 17.2 x 5.2 = 89.44 less 5.0 = 84.44; west wing 4.2 x 4.7 = 19.74; east wing 19.74; living volume 5.2 x 4.7 = 24.44 less 11.0 = 13.44. Total 137.4 m2 net from 196 m2 gross (70% efficiency -- the cost of four separate boxes with 400 mm walls). The brief programme at the RESEARCH MINIMUM of every line, with no formal dining and no store: garage 30 + hall 18 + guest WC 3.5 + women's majlis 25 + family living 35 + show kitchen 20 + dirty kitchen 12 + pantry 4 + stair 14 + lift 3.5 + spine corridor 20 = 185.0 m2. The four pieces are 84.4 / 19.7 / 19.7 / 13.4, so the largest single room available anywhere on the ground floor is the 5.2 m deep north bar, which already has to hold the garage, both entrances, both kitchens, stair and lift. Family living (research 35-45) and formal dining (28-35) have nowhere to go at all.

**Proposed fix:** Delete the two 1.0 m light slots (lines 163-166) and make the south band one continuous 18.0 x 5.5 m bar. That recovers 11 m2 of footprint and, far more importantly, produces one 17.2 x 4.7 m = 80.8 m2 contiguous net space in which a 35-45 m2 family living and a 25-35 m2 majlis can actually be drawn. Then grow the ground footprint from 196 to ~240 m2 (34% coverage, still inside the 35-45% band the research quotes) by deepening the north bar.

### 15. The sunken courtyard cuts a hole through the ground floor on the entry axis and severs the living volume from the house

**Severity:** FATAL

**Numbers:** Court 5.0 x 4.0 = 20 m2 but split by 800 mm of party wall into 5.0 x 2.2 and 5.0 x 1.0 light wells; the second is 1.0 m wide x 3.7 m deep, H/W 3.7. Research minimum useful court: 4 x 4 m. Living volume floor 24.44 -> 13.44 m2 against a family-living requirement of 35-45 m2 (62-70% short). Remaining floor connection to the axis: 2 x 100 mm.

**Evidence:** CT = x 9500-14500, y 15400-19400 (lines 103-104), and the void (line 127) runs from BASE_FL up to GF+200 = +1100 -- i.e. it removes the ground-floor slab (z 400-900) and the bottom 200 mm of the walls, but leaves every wall above +1100 hanging in mid-air over the void. The court straddles the party wall between the living volume (y ...-18000) and the north bar (y 18000-...). It therefore (a) takes 11.0 m2 out of the living volume's 24.44 m2 floor, leaving a 5.2 x 2.5 m strip of 13.4 m2 as the 'family living'; (b) takes 5.0 m2 out of the entrance hall floor immediately behind the front door; (c) reduces the only floor connection between the north bar and the living volume, on the axis, to two 100 mm slivers at x 9400-9500 and 14500-14600. Note also that the plan cuts in derive() are taken at z = GF+1200 = 2100 (line 278), which is 1000 mm ABOVE the top of the court void -- so the courtyard does not appear on the ground-floor plan at all and this defect is invisible in the drawings the script produces.

**Proposed fix:** Move the court clear of the party wall and clear of the axis -- put it against the north bar's north face under the front terrace, or in the east side strip. If it must stay under the living volume, make the void top GF+SLAB and add an explicit bridge/landing solid on the axis, and cut the plans at BASE_FL+1200 as well as GF+1200 so the hole is visible.

### 16. First floor is 48 m2 short; guest bedrooms are 30% under the suite minimum and the master cannot reach 55 m2

**Severity:** FATAL

**Numbers:** 128.9 m2 reachable vs 176.5 m2 required = 47.6 m2 short (37%). Guest suite delivered 19.74 m2 vs 28 m2 minimum = 29.5% short. Third and fourth guest suites: 10.8 m2 each in the best case. Corridor tax on the bar alone: 1.2 x 17.2 = 20.6 m2 (23% of the floor).

**Evidence:** Reachable first-floor net (excluding the marooned cantilever): north bar 89.44 + two wings at 19.74 = 128.92 m2, from 181 m2 gross. Required at research minimums: master 55 + three guest suites at 28 = 84 + stair 14 + lift 3.5 + landing/corridor 20 = 176.5 m2. Dimensionally it is worse than the total suggests. Both wings hang off the two ENDS of the north bar (x 3000-8000 and 16000-21000), so a 1.2 m corridor must run essentially the full 17.2 m of the bar to reach both, and the stair is pinned to the centre by the roof pavilion (PV = x 9000-15000, line 106). Best-case allocation: master = west wing 19.74 + 6.8 m of the bar (35.3) = 55.0; that leaves 89.44 - 35.3 - 14 - 3.5 - 15 = 21.6 m2 for TWO more guest suites. A wing on its own is 4.2 x 4.7 = 19.74 m2: bed 13.7 + shower 6.0 and no wardrobe at all, against the researched suite of bed 18-22 + wardrobe 4-6 + en-suite 6-8.

**Proposed fix:** Widen the north bar from 6.0 to 8.0-8.5 m so it can be double-loaded (bedrooms both sides of a central corridor) instead of a single-loaded 5.2 m strip, and reinstate first-floor area over the living volume's flanks so the two wings become 5.0 x 8.0 m suites of ~30 m2 net.

### 17. Forecourt is 4.65 m deep -- no car can stand between a closed gate and a closed garage door, and there is no turning space of any kind

**Severity:** FATAL

**Numbers:** 4.65 m available vs 5.5-6.0 standing / 6.0 aisle; shortfall 0.85-1.35 m. LC300 tail 85 mm past property line.

**Evidence:** villa_3d.py: PLOT_D 29000, BW 350 -> inside face of front wall y=28650. Garage doors are voids at NB_Y1=24000 (blk(x0, NB_Y1-300, GF, x0+2700, NB_Y1+300, GF+2400)). Clear depth = 28650 - 24000 = 4,650 mm; 5,000 mm to the property line. VILLA_RESEARCH.md sec.4 asks 5.5-6.0 m standing space between gate line and street, and 'Aisle in front 6.0 m min'. A Land Cruiser 300 (4,985 mm) stopped 100 mm off a closed door has its tail at y=29,085 -- 85 mm over the property line and 435 mm inside the 4.5 m gate opening, so the gate cannot close behind it. A Range Rover LWB (5,252) sits 350 mm out into the street; a GLS (5,207) 300 mm. Even a 4.5 m saloon leaves 50 mm. Turning: the research offers three options -- hammerhead 6.0 x 3.0 m bay off a 5.5 m aisle, a 6.0 x 12.0 m forecourt, or a 13-15 m circle. The court is 4.65 x 23.3 m, so none of the three fits; it fails the shallowest of them by 1.35 m. Every departure is therefore a reverse out through a 4.5 m gate. No driveway, apron, ramp, steps or gate leaves are modelled at all, so none of this has been tested in the geometry.

**Proposed fix:** The 6.0 m aisle has to be bought from the rear, which is 9.5 m over-set-back (see the depth-budget finding). Move the whole house 2.15 m south: forecourt becomes 6.80 m, garage bar y 15850-21850, rear band 10.0 m. Then the vehicle gate must also widen to 6.0 m clear (x 3800-9800) so it spans both doors and each bay gets a straight run -- with no run-back available for a slider once the pedestrian gate moves onto the axis, specify a 4-leaf bi-fold/speed gate, which needs none.

### 18. Garage bay 2 is physically unreachable -- the two-car brief delivers one car

**Severity:** FATAL

**Numbers:** required R = 3.01 m vs 5.8-6.4 m (car) / 6.9-7.5 m (SUV); bay 2 overhangs the gate by 1.30 m

**Evidence:** Doors are at x 3800-6500 (bay 1) and x 6900-9600 (bay 2); centres 5150 and 8250. The vehicle gate void is x 3800-8300, centre 6050 -- so 1,300 mm of bay 2's door sits behind solid boundary wall. Bay 1 works only by luck: its west edge is coincident with the gate's west jamb, so a car hugging the west side has a straight run. Bay 2 requires a 2,200 mm lateral shift completed within the 4,650 mm of court. For a symmetric two-arc S-path, tan(theta/2) = 2200/4650 = 0.473 -> theta = 50.6 deg, and L = 2R sin(theta) gives a required centreline turning radius of R = 3.01 m. Passenger cars manage ~5.8-6.4 m, large SUVs 6.9-7.5 m (research gives kerb radius 5.5-6.0 car / 6.5-7.0 SUV). The manoeuvre needs less than half the achievable radius. The alternatives fail too: driving east along the court then turning 90 deg into bay 2 needs ~6.0 m of depth for the turn alone against 4.65 m available; entering the gate at 20 deg off-square then straightening over 4.65 m yields only 0.80 m of lateral shift against the 2.20 m needed.

**Proposed fix:** Centre a 6.0 m clear gate on the pair of doors (x 3800-9800) so both bays are straight-in, and take the aisle to 6.0 m. If the gate must stay 4.5 m, the bays cannot be side-by-side behind it -- go tandem, which needs 11.0-11.5 m of depth and is not available, so the gate widening is the only route.

### 19. The terrace between the living-room glass and 1.4 m of water is 300 mm wide -- and it is the only outdoor floor on the plot

**Severity:** FATAL

**Numbers:** 0.30 m vs 1.5 m min (walking) and 3.5-4.5 m (lounging); south 2.25 / east 8.75 / west 8.75 all pass

**Evidence:** POOL_Y1 = 12500 is identical to WG_Y0 = 12500, so the pool water edge is coincident with the building line. The 400 mm north coping band of the shell (y 12500-12900) is buried under the living-volume slab. Evaluating the booleans at (x=12000, y=12650): solid to z=1000, void 1000-4300 (the structural glazing). At y=12400 you are already in the pool. So stepping out of the double-height volume you cross a 100 mm upstand onto a 300 mm ledge at +1000, then drop 300 mm to water at +700 and 1,400 mm of water beyond. Research sec.4: pool surround 1.2 m min on back sides, 1.5 m where people walk, 3.5-4.5 m on the lounging side, and 'A 600 mm coping walk is a developer's pool.' The other three surrounds pass (south 2.25 m to the rear wall, east and west 8.75 m each) -- the failure is on the one side that matters. The consequence compounds: the 3.0 m cantilever (y 9500-12500, soffit 3.8 m over water) shades nothing but water, so the villa's signature covered outdoor room contains no floor; and the wings' only south openings have 450 mm sills (GF+450), i.e. windows, so this 300 mm ledge is the sole physical connection between the house and its garden.

**Proposed fix:** Slide the pool 4.0-4.5 m south of the glass line so the 3.0 m cantilever covers a terrace instead of water. That gives a 4.0 m lounging deck at the double-height glazing -- dead on the research's 3.5-4.5 -- with the pool beyond it. This move and the 2.15 m southward shift of the house are the same operation and must be resolved together.

### 20. The overflow and the catch basin do not exist in the model -- the boolean is a no-op

**Severity:** FATAL

**Numbers:** basin void ∩ pool shell = 0.000 m³; y-overlap 0 mm. Rim +700 = water level on all 4 faces. Section AA and aerial SW both show a closed level-rim box.

**Evidence:** villa_3d.py:269-270 cuts the "spill + basin" void over y = 1600→2600. The pool shell (line 266-267) spans y = 2600→12900. The two ranges touch at y=2600 and nowhere overlap: I computed the intersection as 0.000 m³ (y-overlap 0 mm) against the pool shell, against the interior void, and against the south boundary wall -- the void removes nothing from anything. So the pool is modelled as a sealed 400 mm-walled tank whose rim sits at exactly POOL_TW = +700 on all four sides, i.e. dead level with the water: no weir crest, no notch, no basin, no gutter. VILLA_SECTION_AA.png shows it plainly -- a symmetric U with both walls to the same height and no spill; VILLA_VIEW_AERIAL_SW.png shows a flat-rimmed tray. Meanwhile villa_sheets.py:72-73 and :84-85 draw a rectangle and the words "OVERFLOW EDGE + CATCH BASIN" onto A-201. That geometry is on the sheet only. This is precisely the failure villa_3d.py's own docstring claims to have eliminated: "Modelling once and deriving every drawing means plan, section and elevation cannot disagree." On the single element the whole scheme is sold on, they disagree.

**Proposed fix:** Give the void a real y-range that bites into the shell (e.g. POOL_Y0-1400 → POOL_Y0+400) and model the crest as a separate lowered block: south wall top at +694, i.e. 6 mm below POOL_TW, per the research's 2-6 mm differential. Model the basin as a solid chamber (walls + floor) and subtract its interior, so it survives into the section. Then re-cut Section AA and check the notch appears before anything else is drawn.

### 21. The waterwall faces the boundary wall 2.25 m away -- no occupant ever sees it

**Severity:** FATAL

**Numbers:** Spill face y=2600; boundary wall inner face y=350 → 2,250 mm slot. Nearest viewer (living-room glazing) at y=12800, i.e. 10.2 m on the wrong side of the weir. Unused strip between pool shell (12900) and basement wall (15000) = 2,100 × 18,000 mm = 37 m².

**Evidence:** The spill face is the south end at y = 2600. The south boundary wall's inner face is at y = 350: the waterwall discharges into a 2,250 mm slot, of which 1,000 mm is the basin, leaving a 1,250 mm walkway. Every occupied viewpoint is north of the pool -- living-room structural glazing (y 12800), the 3.0 m cantilever soffit, the first-floor bedrooms, the roof pavilion -- so all of them see the *back* of the weir: a blank 700 mm rim. The research's entire case for the raised one-sided overflow (VILLA_RESEARCH.md §THE THREE FINDINGS, option (b)) is that "the spill face becomes a waterwall into a visible basin". Oriented this way, the +20-40% cost of an overflow edge buys a feature that "reads as nothing" -- the exact failure the research diagnosed for the classic infinity edge on this plot. The 700 mm raise is within the researched 600-900 mm band and does earn its 45° clearance, but visually it earns nothing.

**Proposed fix:** Move the weir to the NORTH end (y=12500, facing the house) and put the basin in the 2,100 mm gap between the pool and the basement. The sheet then falls toward the double-height glazing, is seen from the living room and heard from under the cantilever, and the basin lands within a few metres of where the plant room should be. Second-best: spill the east long face into a garden rill. Either beats spilling at a wall.

### 22. There is no plant room anywhere, no basement access, and every possible basement location breaks the 15 m pipe rule

**Severity:** FATAL

**Numbers:** Basement 141 m², zero partitions, zero access. Pipe run: 15.7 m to the nearest wall face; 24.2 m to a corner plant room; research limit 15 m. Same run drops to 12.9 m from a room in the 12900-15000 strip, and to 3-5 m if the weir also moves north.

**Evidence:** villa_3d.py:128-132 builds the basement as one undivided shell -- outer 3000-21000 × 15000-24000, interior inset 400 → 17.2 × 8.2 m = 141 m² less the 20 m² court. There are no partitions (PARTS_GF/PARTS_FF only touch ground and first), no plant room, no door, no ramp, and the stair loop at :232-234 runs GF→FF only, so the basement is a sealed box you cannot enter. The research requires 12-18 m² clear at 2.4 m for pool plant alone, plus 4-6 electrical / 6-10 AHU / 6-10 water tank, and an acoustically separated room with a 1.0 m clear door. On the pipe run: measuring orthogonally from the basin centre (12000, 2100, -450), the shortest possible route to the basement -- straight up the axis to the wall face at (12000, 15400, -2800) -- is already 15.7 m before you enter the room. A real 12-18 m² room at either basement corner (5000 or 19000, 17000, -2800) is 24.2 m one way, so ~48 m of suction+return plus a separate overflow-pump circuit, all buried under the garden and under the pool shell.

**Proposed fix:** Take the 2.1 × 18 m strip between the pool shell (y 12900) and the basement south wall (y 15000): 37 m² is more than enough for a 12-18 m² pool plant room plus the balance tank, entered from the basement, with the heat pump venting to the garden. Add a basement stair -- the obvious place is alongside the GF→FF flight at x 13000-14600 -- and partition the basement into plant / maid / laundry / store as the research schedule assumes.

### 23. The sunken courtyard is a 20 m² hole in the ground floor that receives no daylight and has no sump

**Severity:** FATAL

**Numbers:** Slab removed 5.0 × 4.0 × 0.5 = 10.0 m³ → 20.0 m² of floor. Living room 28.6 → 15.6 m² usable. Guest WC 3.6 → 2.7 m² with a 0.9 m² hole in it. Court invert -2800; garden 0; pool water +700. No guarding (research min 1,100 mm).

**Evidence:** The court void (villa_3d.py:132, x 9500-14500 × y 15400-19400 × z -2800→+1100) is subtracted after the ground slab is built (z 400-900), so it removes 10.0 m³ of slab = 20.0 m² of ground floor: 13.0 m² out of the family living room's 28.6 m² (leaving 15.6 m² usable), 7.0 m² out of the entrance hall, and 0.45 m³ = 0.9 m² out of the 3.6 m² guest WC -- a 900 × 1000 mm hole in the WC floor dropping 3.7 m to the basement. None of this appears on A-201 because the plan is cut at z=2100, above the void, and the code deliberately omits the "beyond" projection (villa_3d.py:349-350). And it is roofed: the first-floor slab covers y 18000-19400 at z 3600-4100 and the roof slab covers x 3000-21000 × y 9500-24000 at z 8700, so the court sees no sky at all. The one move that was supposed to make the semi-basement a served space rather than a cellar (F.LOT's pebble court, research §1 and §THE SECTION WORTH STEALING) delivers zero daylight. On water: this is the site's lowest open point at invert -2800, 3.7 m below the garden and 12 m downhill of 54.4 m³ of pool water, with no sump modelled -- the research explicitly calls for a "pumped sump for a 1-in-100-year storm".

**Proposed fix:** Move the court outside the ground-floor footprint -- the obvious place is the same 12900-15000 strip, or east/west of the living volume where the 1.0 m light slots already cut through every level -- so it is a true external light well against the basement wall with full-height glazing, open to sky. If it stays internal, it is an atrium, not a court: it needs an opening in the roof above, 1,100 mm guarding at the ground-floor edge, and it must stop clipping the guest WC. Add a pumped sump either way.

### 24. The west brise-soleil shades a solid wall -- there is no opening anywhere behind it

**Severity:** FATAL

**Numbers:** 9 fins at x 2300-2750, y 12800-17780, z 900-8700 (villa_3d.py:260-263). West wing west face = x 3000, y 12500-18000 = 5.5 x 7.8 = 43 m2, zero openings.

**Evidence:** The complete list of wall voids is villa_3d.py lines 238-249 and 257. Every one is on the south face (y=WG_Y0), the north-bar clerestory band (line 246: y 18800-23200 only), the north entrance, or the east service door. Nothing is cut in the west wall of the west wing. The fin array at lines 260-263 sits at y 12800-17780 -- precisely in front of 43 m2 of blank blockwork. This is the first thing an experienced architect sees in the aerial and it is unanswerable: a sunshade with nothing to shade is applied decoration, which is the exact definition of developer-built. It also means the villa has a solar-control device on the one facade where the research says horizontals cannot work, and no device at all where glass actually is.

**Proposed fix:** Put glass behind them or delete them. Cut a 4,200 wide x 2,900 high opening (sill +400, head +3,300 above each floor) in the west wall at x=3000, y 13400-17600, at both levels -- formal dining below, bedroom 1 above. Then re-proportion the fins (next finding). If the west glass is unacceptable for privacy or heat, delete the fins entirely and let the west read as a deliberate blind stone flank -- a blank wall is defensible, a blank wall wearing a sunscreen is not.

### 25. The first-floor cantilever and the roof edge are coplanar -- the scheme's subject is depth and its two deepest elements have no reveal between them

**Severity:** FATAL

**Numbers:** Roof front edge y = WG_Y0 − CANT = 9500 across the full 18.0 m (line 165). Cantilever box front y = WG_Y0 − CANT = 9500 (line 142). Offset: 0 mm.

**Evidence:** Line 165 projects the roof slab 3.0 m over the pool across the entire 18,000 mm width HX0-HX1, and line 142 projects the first-floor box 3.0 m to exactly the same plane. The strongest line in the south elevation is therefore a single unbroken 18.0 m straight edge at 10.3 m, with the 6.0 m box face flush behind it. No shadow, no layering, no hierarchy -- the cantilever cannot read as deliberate because it never separates from the roof. Confirmed in the aerial: the overhang reads as one flat lid, not as a projecting element.

**Proposed fix:** Step the roof edge and hold the box back. Roof: wings (x 3000-8000, 16000-21000) project 1.5 m to y 11000; centre (x 9000-15000) projects 3.5 m to y 9000. First-floor box front to y 10500 (2.0 m projection), so the roof oversails it by 1.5 m and throws a shadow line across its head. South elevation then reads four planes at y = 9000 / 10500 / 11000 / 12500 instead of two. Detail the soffit with a 20 mm shadow gap and a drip at the wall junction, as the research specifies.

### 26. The cantilevered box is a blank 22 m2 wall over an unnamed room

**Severity:** FATAL

**Numbers:** Box south face 6.0 x 3.7 = 22.2 m2, zero openings. Only glazing (lines 240-241) is at y 12200-12900 -- the box's NORTH wall, facing the internal void.

**Evidence:** The most exposed plane in the whole villa -- the thing that hangs over the pool and terminates the entry axis -- is solid. Lines 240-241 put the first-floor glazing at y 12200-12900, which is the back wall of the box facing into the double-height shaft, not the garden. Worse, villa_sheets.py FIRST (lines 36-44) schedules bedrooms 1/2/3, master, dressing, en-suite and landing -- all of them north of y 12500. Nothing occupies the box. A 3.0 m cantilever containing no room and showing no window is a gesture, and it will be read as one in five seconds.

**Proposed fix:** Give it a programme and a face. Put the master bed head there (or an upper family room), and glaze the south face 5,200 wide x 2,400 high, sill +750 / head +3,150 above the box floor (z 5750-8150), glass set back 600 mm from the outer face so the 400 mm wall plus 200 mm reveal reads as real thickness. A 600 mm reveal on a 2.4 m opening also gives a VSA of 76° -- genuine shading on the south face, which the current punched holes do not have.

### 27. Three of four elevations are effectively blank, and the two largest ground-floor rooms have no window at all

**Severity:** FATAL

**Numbers:** North 3.6 / 185 m2 = 1.9% void. West 2.86 / 118 = 2.4%. East 5.5 / 118 = 4.7%. South 44.0 / 185 = 23.8%. Women's majlis 26.1 m2 and show kitchen 26.1 m2: zero external openings.

**Evidence:** North face is 18.0 x 10.3 m with a single 1,500 x 2,400 door (line 248). West is 11.5 x 10.3 with one 4,400 x 650 clerestory. The villa is a bunker with a glass face -- that is a diagram, not a building, and the blankness is a direct symptom of the plan: the majlis and the kitchen both sit in the north bar (y 18400-23600) with no wall reaching an exterior face that has been opened. A 26 m2 women's majlis -- a principal reception room -- lit only by borrowed light through one 1.2 m door from the hall is the single most damaging plan fact behind the elevation.

**Proposed fix:** Manufacture two walled courts inside the setbacks, per Casa Merida / Wall House. Majlis: 5.0 x 2.5 m court at x 15600-20600, y 24000-26500, screened by the 2.4 m stone wall, with a 4,000 x 2,700 glazed opening in the majlis north wall. Kitchen: 4.0 x 2.5 m service court at x 0-3000 (side setback), y 19000-23000, with a 2,400 x 2,100 window. That lifts north to ~9% and west to ~10% void, gives both facades a deep shadow instead of a flat plane, and costs nothing in GFA because both courts are in setback land you cannot build on anyway.

### 28. Six elements on one centreline -- the elevation is a literal projection of the plan with no counterpoint

**Severity:** FATAL

**Numbers:** Building 18.0 m centred in 24.0 m (3.0 m each side). South bays 5.0 / 1.0 / 6.0 / 1.0 / 5.0. Windows mirrored at x 4200-6800 and 17200-19800. Pool centre 12000. Rill on AXIS 12000. Entrance AXIS ±750. Pavilion x 9000-15000, centre 12000.

**Evidence:** Perfect mirror symmetry with nothing to hold the other side of it. Both wings are the same width, the same depth (y 12500-18000), the same height, with the same two windows in the same positions. Symmetry is a legitimate strategy, but it has to be paid for with hierarchy -- a differentiated centre, a change of material, a change of aperture. Here the centre bay's only distinction is that it is 1.0 m wider and its cantilever is flush with everything else (see above). The result is the massing signature of a spreadsheet layout, and it is the reason the aerial reads as one squarish block.

**Proposed fix:** Keep the water axis dead centre -- that is the Alhambra idea and it is right -- and break everything else. (1) Push the east wing 1.5 m further south: y 11000-18000 instead of 12500-18000, so the south facade steps. (2) Make the wings different widths: west 5.6 m (x 3000-8600), east 4.4 m (x 16600-21000), centre unchanged at 6.0 m -- an A-B-A' rhythm, and formal dining gains 3.3 m2. (3) Move the roof pavilion off-axis to the south-west (see below). Three moves, no change to the parti, and the elevation stops being a mirror.

### 29. The four-bedroom programme is 43 m² (31%) short of the researched minimum on the modelled first floor

**Severity:** FATAL

**Numbers:** provided 96.0 m² net habitable · required 139 m² min · deficit 43.0 m² = 31% · usable gross 163 m² vs 190-200 m² needed

**Evidence:** villa_sheets.py:36-44 schedules the whole first floor. Habitable net (all rooms less the landing) = 96.0 m² -- the figure the A-202 title block itself prints. VILLA_RESEARCH.md:317-318 sets the bottom of the luxury range at master suite 55 + 3 guest suites @28 = 139 m² net. The floor is 43.0 m² short before any landing, stair or wall thickness is counted. It cannot be replanned out of the deficit either: first floor gross is 181 m², of which 18 m² is the orphaned cantilever, leaving 163 m² gross; at a realistic 0.82 net/gross for a cellular bedroom floor that is 134 m² net with zero circulation. A compliant four-suite floor needs ~190-200 m² gross.

**Proposed fix:** Two bedrooms must leave this plate. Either (a) take the master up into the roof level -- the 30 m² pavilion at villa_3d.py:107 is already built and already counted in GFA, extend it to ~60 m² as a master pavilion with roof terrace, or (b) deepen the north bar from 6.0 m (NB_Y0=18000) to 7.5 m and lengthen the wings south from 5.5 m to 7.0 m, which forces the pool to rotate east-west across the south boundary. Do not attempt four en-suited bedrooms on 163 m².

### 30. The master bedroom is 2.85 × 3.20 m = 9.1 m², windowless, and the whole suite is 26.1 m² against 55-75

**Severity:** FATAL

**Numbers:** master bedroom 9.12 m² vs 28-35 · suite 24.9 m² vs 55-75 (45% of minimum) · en-suite 9.30 m² × 1.85 m deep vs 14-20 · clerestory sill 2800 mm above FFL · even the entire east limb (master box 26.1 + Bedroom 2 22.5 = 48.6 m²) is 6.4 m² short of a minimum master suite

**Evidence:** villa_sheets.py:39-41 -- MASTER BEDROOM 17750,18400→20600,21600 = 9.12 m²; DRESSING 6.48 m²; MASTER ENSUITE 5.025 × 1.85 = 9.30 m². Suite net 24.9 m², gross box 26.1 m². VILLA_RESEARCH.md:317 requires 55-75 (bed 28-35, dressing 14-20, en-suite 14-20). The master bedroom is smaller than the guest WC standard for a majlis-served villa is large, and it is 2.85 m wide -- a 1.8 m king bed leaves 1.05 m total circulation. The en-suite is 1.85 m deep, which cannot take a 1.7 m bath plus a walkway. Worse, checked against every opening in villa_3d.py:237-258, the master bedroom's only daylight is the east clerestory band at z 7800-8450, i.e. a 650 mm slot with its sill 2.80 m above the bedroom floor. No window, no view, no openable light at eye level. BEDROOM 3 (26.1 m²) is in the same condition; the 35.6 m² LANDING has no opening of any kind.

**Proposed fix:** Give the master the whole east limb plus the east half of the north bar, or move it to the roof level. Whatever happens, it needs a window: the east wall at x=20600 faces the boundary 3.0 m away, so put a full-height opening onto a private screened terrace rather than relying on a 2.8 m clerestory.

### 31. Two of the four bedrooms are inner rooms entered only through another bedroom

**Severity:** FATAL

**Numbers:** 4 bedrooms briefed · 2 with independent access · 2 landlocked · 1 stair, unprotected, discharging into an open double-height volume

**Evidence:** villa_3d.py:213-220 DOORS_FF. Bedroom 1 has exactly one door, (5000,18250)-(6200,18400), which opens into Bedroom 3. Bedroom 2 has exactly one door, (17800,18250)-(19000,18400), which opens into the MASTER BEDROOM. Neither reaches the landing. The brief asks for 4 bedrooms; this plan delivers 2 bedrooms and 2 tandem inner rooms. Under any residential code these are not habitable bedrooms -- no independent access, no protected escape, and the escape route from Bedroom 2 runs through the principal bedroom. The single stair (villa_3d.py:232-235) discharges into a double-height volume open to the entrance hall, so there is no protected escape route from the first floor at all.

**Proposed fix:** The 35.6 m² landing has the area to become a proper corridor spine reaching all four rooms -- run a 1.4 m circulation loop off it into both wings, which costs ~9 m² and buys four independent doors. That still leaves the area deficit in finding 1 unresolved.

### 32. One bathroom above ground serves four bedrooms -- and it is inside the master suite

**Severity:** FATAL

**Numbers:** 4 bedrooms · 1 bathroom (9.30 m²) · 0 en-suites for 3 of 4 bedrooms · 18-24 m² of en-suite provision missing · nearest WC for Bedrooms 1/2/3 is one floor down

**Evidence:** villa_sheets.py:36-44 lists exactly one wet room on the first floor: MASTER ENSUITE, 9.30 m², reached through the master dressing (door villa_3d.py:217). Bedrooms 1, 2 and 3 have no en-suite, no wardrobe and no bathroom of any kind on their floor. There is no family bathroom and no first-floor WC. The nearest facility is the 3.65 m² guest WC off the ground-floor entrance hall. VILLA_RESEARCH.md:317-318 puts each guest suite at 28-35 m² comprising bed 18-22, wardrobe 4-6, en-suite 6-8.

**Proposed fix:** Budget 3 × 7 m² of en-suite plus 3 × 5 m² of wardrobe = 36 m² and add it to the deficit in finding 1 -- which is the arithmetic that proves the bedroom floor has to grow or lose a room.

### 33. The formal dining room is entered only through the working kitchen; the study only through the women's majlis

**Severity:** FATAL

**Numbers:** formal dining: 1 door, into the kitchen · study: 1 door, into the women's majlis · 0 doors from either to the hall

**Evidence:** villa_3d.py:187-201. Partition (3400,18250)-(7600,18400) closes the whole west neck with one door at (5000,18250)-(6200,18400); north of it is the SHOW KITCHEN. Partition (16400,18250)-(20600,18400) closes the east neck with one door at (17800,18250)-(19000,18400); north of it is the WOMEN'S MAJLIS. So guests going to dinner walk through the kitchen, and anyone using the study walks through the majlis -- which means the study is unusable whenever the majlis is occupied, and the majlis loses its privacy whenever the study is used. The formal dining room has no connection at all to the entrance hall or the living volume.

**Proposed fix:** Extend the hall south past the guest WC into the gap at y 18400-20550 (currently 10.4 m² of unassigned floor) and take doors off it into both wings, leaving the kitchen and majlis doors as secondary. The kitchen-to-dining door should survive as a serving door only.

### 34. Gulf service discipline fails completely: no dirty kitchen, no pantry, and the service route to the majlis crosses the entrance hall

**Severity:** FATAL

**Numbers:** dirty kitchen 0 m² vs 12-18 · pantry 0 m² vs 4-6 · service traverse 7.07 m across the entrance hall · service door lands in the majlis · study 22.5 m² unbriefed, on the service boundary

**Evidence:** The brief and villa_3d.py:46-48 both claim "service on the east boundary reaching the dirty kitchen without crossing guest or family space." No dirty kitchen exists -- villa_sheets.py:27-35 has no such room, and the basement is undivided. VILLA_RESEARCH.md:323 requires dirty/wet kitchen 12-18 m² with its own external door plus a 4-6 m² pantry; VILLA_RESEARCH.md:348-354 requires "a short service corridor behind the show kitchen with a discreet door into the majlis." Instead the show kitchen sits at the far west (x 3400-8425) and the majlis at the far east (x 15575-20600). The only route is kitchen door (8500,22100) → entrance hall → majlis door (15500,21100): a 7.07 m diagonal traverse of the guest arrival space, in full view of the front door and of the double-height family living volume. The one "service entrance" (villa_3d.py:257-258) punches the east boundary wall directly into the WOMEN'S MAJLIS at y 18700-19800 -- the most privacy-sensitive room in the house -- and is 12 m from the kitchen it is supposed to serve. A 22.5 m² STUDY that the brief never asked for occupies the east service frontage where the dirty kitchen and service corridor belong.

**Proposed fix:** Swap the kitchen and the majlis: put the show kitchen in the east half of the north bar against the east boundary, delete the study, and use the east wing for the dirty kitchen (13 m²) + pantry (5 m²) + service lobby off a boundary door. The majlis then sits west, one door off the hall, with a service door from the pantry -- the researched arrangement exactly.

### 35. The house has one external door in the entire envelope, and no opening in the model actually penetrates its wall

**Severity:** FATAL

**Numbers:** 3 entrances claimed · 1 modelled · 0 that open · 100 mm of wall left at every opening · 0 doors from porch to house · 0 external doors from majlis, kitchen, dining or study

**Evidence:** Openings are cut at ±300 about grid lines that are the OUTER face of a 400 mm wall, so every one of them leaves a 100 mm skin standing. Guest entrance (villa_3d.py:248-249): wall y 23600-24000, void y 23700-24300 → 100 mm left. Service entrance (:257-258): wall x 20600-21000, void x 20700-21300 → 100 mm left. Living-room garden glazing (:238-239): wall y 12500-12900, void y 9200-12800 → 100 mm left. All four wing windows (:242-244): same, 100 mm left. Only the two clerestory bands (:245-247) cut through. This is visible in A-201: the north, south and east walls draw as unbroken lines. Beyond the modelling bug, the programme is wrong even by intent: there is no family entrance at all (the car porch at x 3500-10500, y 24400-28400 has no door into the house -- villa_3d.py:44-48 claims "family via the garage", but there is no garage and no link), and the only garden threshold is the living-room glazing. The kitchen, formal dining, majlis and study have no external door: nobody can step out to the pool or garden from any of them.

**Proposed fix:** Change every opening to be cut about the wall centreline (or ±(WALL/2 + tolerance)), then add: a family door from the porch into a boot/service lobby at the west end of the north bar, a majlis door onto its own screened forecourt, and full-height sliding doors from the dining and living rooms onto the pool terrace.

### 36. The 142 m² semi-basement -- the whole reason the programme was said to fit -- has no stair, no door and no rooms

**Severity:** FATAL

**Numbers:** 142 m² basement · 0 stairs, 0 doors, 0 partitions · staff 0 m² vs 15 · laundry 0 vs 10 · plant 0 vs 16 · pool plant 0 vs 12-18 · store 0 vs 24-33 (6-8% of 407 GFA) · lift 0 vs 1.6 × 1.7 m shaft

**Evidence:** villa_3d.py:127-132 builds the basement as a single hollow box, x 3400-20600, y 15400-23600, and nothing else. VILLA_PLAN_BASEMENT.png renders as one empty rectangle. The stair at villa_3d.py:232-235 runs only from GF to FF; no stair, ramp, lift or hatch reaches BASE_FL = -2800. No opening is cut below ground level anywhere. VILLA_RESEARCH.md:24-27 and :341-342 make this level carry maid's room + bath 15, laundry 10, store 8, plant 16, pool plant 14 -- the brief asks for "staff and plant" here. None is drawn: 0 m² of staff accommodation, 0 staff WC, 0 laundry, 0 plant room, 0 pool plant room in a scheme with an overflow pool that needs 12-18 m² of plant with a floor gully and acoustic separation. There is also no lift anywhere in a four-level house (basement, ground, first, roof).

**Proposed fix:** Put a service stair plus a 1.6 × 1.7 m lift shaft in the west end of the north bar where it can serve the porch lobby, the dirty kitchen and the basement in one core, and draw the basement partitions. That core, not the ceremonial stair, is what makes the semi-basement a served floor.

### 37. The sunken courtyard is cut under the roofed living volume: it removes 52% of the family living room floor and the bottom of the only stair

**Severity:** FATAL

**Numbers:** 15.0 m² of 28.6 m² living-room floor removed = 52% · +5.0 m² in the hall · stair treads 1-2 removed · 0 daylight (roof slab is solid over it) · plan cut z=2100 vs hole top z=1100, so the drawing cannot see the defect

**Evidence:** villa_3d.py:104-105 and :132 -- CT is x 9500-14500, y 15400-19400, voided from BASE_FL up to GF+200 = z 1100. That footprint sits directly under the FAMILY LIVING room (villa_sheets.py:33 -- x 9400-14600, y 12900-18400). The overlap is 5.0 × 3.0 = 15.0 m², i.e. 52% of the 28.6 m² labelled living-room floor is a hole down to -2800, unguarded. A further 5.0 m² of hole falls in the hall zone and takes out the first two treads of the stair (x 13000-14600, y from 18700, first riser top at z 1144 vs the hole rising to 1100). The court is also not a courtyard: the roof slab (villa_3d.py:165) spans x 3000-21000, y 9500-24000 solid over it, so it receives no daylight and cannot do the F.LOT job VILLA_RESEARCH.md:24-27 assigned it. The plans do not show any of this because they cut at z = GF+1200 = 2100 while the hole tops out at 1100 -- A-201 draws FAMILY LIVING 28.6 m² over a floor that is half missing.

**Proposed fix:** Move the sunken court south and out from under the building -- the strip between the wings at y 15000-18000, x 3400-8000 and 16000-20600, is already excavated basement with no slab over it (2 × 12 m² of open hole in the garden today). Formalise one of those as the 5 × 4 m white-pebble court with full-height glazing to the basement, and slab over the other.

### 38. The stair is a 55° ladder that stops 196 mm below the first floor, and a compliant flight does not fit the space allowed

**Severity:** FATAL

**Numbers:** riser 244 (max 180-190) · going 170 (min 280) · pitch 55.1° (max 30°) · 16 × 244 = 3904 vs 4100, short 196 mm · compliant run 6440 mm vs 5200 available · stair area 4.35 m² vs 14-18

**Evidence:** villa_3d.py:232-234: 16 steps, riser 244 mm, going 170 mm. The research values (VILLA_RESEARCH.md:156-158) are going ≥280 (luxury 300-320) and riser 100-180 (luxury 170) -- the two numbers have been swapped. Pitch = atan(244/170) = 55.1°, against a 30° maximum in the research and ~42° in any code. The rise also does not close: 16 × 244 = 3904 mm against a ground-to-first floor-to-floor of 5000 - 900 = 4100 mm, leaving a 196 mm step at the top. A compliant flight at 175/280 needs 24 risers and 6440 mm of run; the stair zone (y 18400-23600) is 5200 mm. It has to become a dog-leg with a half-landing, which needs ~3.4 m width against the 1.6 m allowed, and 11-12 m² per floor against the 4.35 m² currently occupied -- VILLA_RESEARCH.md:327 budgets 14-18 m² per floor.

**Proposed fix:** Redraw as 24 risers at 171 mm / 280 mm going in two flights around a half-landing, 1300 mm wide, and reserve 12-14 m² per floor for it. That area has to come out of the 35.6 m² landing, which can afford it.

### 39. The axis is not built: no opening in the external envelope is actually cut through -- every one leaves a 100 mm skin

**Severity:** FATAL

**Numbers:** wall 400 mm; voids remove 300 mm; residual skin 100 mm × 1.5 m (front door), × 5.6 m (garden glazing), × 2.6 m (each wing window), × 1.1 m (service door). 6 sites, 0 openings currently through.

**Evidence:** Systematic off-by-100 in villa_3d.py. Walls are WALL=400 (shell() offsets the union by −400, lines 144-151) but every envelope void is dimensioned ±300 about the wall's OUTER face, so only 300 of the 400 is removed. Confirmed in the derived geometry, not inferred: VILLA_PLAN_GF.dxf at the front door shows the outer face stepping 24000 → 23700 across x 11250-12750 while the inner face runs y=23600 unbroken from x=8575 to 15425. The same three-line signature appears at the garden glass wall (outer 12500 → 12800 across x 9200-14800, inner face 12900 continuous 9400-14600), at both wing window bands (4200-6800, 17200-19800), and at the service door (outer 21000 → 20700, inner 20600 continuous 18400-23600). Culprits: line 248 (AXIS±750, NB_Y1−300), line 238 (WG_Y0+300), line 243, line 244, line 257. Only the two clerestories (line 245-247, ±100/+600 against a 400 wall) are genuinely cut. So the front door on the axis is a 300 mm niche, and the house that is supposed to frame an uninterrupted perspective from gate to pool is a hermetically sealed box. This is why VILLA_ELEV_S.png reads as four shallow punched squares.

**Proposed fix:** Every envelope void must straddle the full wall, not sit inside it. Replace ±300 with −300/+(WALL+100) measured outward-to-inward: line 248 NB_Y1−300 → NB_Y1−WALL−100 (23500); line 238 WG_Y0+300 → WG_Y0+WALL+100 (13000); lines 243-244 same; line 257 HX1−300 → HX1−WALL−100. Six sites, one line each. Then re-cut and re-read the plans before believing any elevation.

### 40. The destination of the axis is a sealed 7.8 m shaft with 15 m² of its floor missing

**Severity:** FATAL

**Numbers:** room 5.2 × 5.5 = 28.6 m² scheduled; court overlap 5.0 × 3.0 = 15.0 m²; real floor 13.6 m². Ceiling 8700 − 900 = 7.8 m clear. Brief/research target family living 35-45 m². Openings: 0.

**Evidence:** The double-height FAMILY LIVING volume (LV 9000-15000 × 12500-18000) has no opening of any kind. Its south wall is the 100 mm skin above; its two side walls face the 1.0 m light slots but no void is cut into them; the roof slab (line 165) runs unbroken across the top with no rooflight. Meanwhile the sunken-court void (line 132, CT 9500-14500 × 15400-19400, cut from BASE_FL to GF+200) punches a 5.0 × 4.0 m hole clean through the ground-floor slab, and 15.0 m² of that hole lands inside this room. The room the whole scheme points at is therefore a windowless 5.2 × 2.5 m ledge, 13.6 m² of walkable floor under a 7.8 m ceiling, with an unguarded 3.7 m drop across the rest of it. The hole does not appear on A-201 at all: the plan cuts at z=2100 and the court tops out at z=1100, so VILLA_PLAN_GF.dxf contains no 15400/19400 line and the sheet prints 'FAMILY LIVING 28.6 m2' over a floor that is not there. The header claim that plan, section and elevation 'cannot disagree' fails here -- a void below cut height is invisible to section().

**Proposed fix:** Move the sunken court off the axis (put it against the north bar's east end, x 16400-20600 × 19000-23000, where it lights the basement without eating the living room) and open the south wall: a single 6.0 m × 7.8 m glazed opening, LV_X0+400 to LV_X1−400, GF to RF. Add a floor-plate cut-check to build(): section the model at GF+50 as well as GF+1200 and print any hole area that falls inside a scheduled room rectangle, so the schedule can never overstate a floor again.

### 41. The 3.0 m cantilever is modelled as a closed room floating over the pool, disconnected from the building

**Severity:** FATAL

**Numbers:** box 6.0 × 3.4 m external, 5.2 × 2.3 m internal = 12 m²; soffit 4.1 m above pool water; 0 connections to the first floor; 1.0 m light slot on each side, 12.5 m void to the north.

**Evidence:** FF_FOOT (line 140-142) passes the cantilever rectangle (9000, 9500, 15000, 12900) through shell(), so it gets its own 400 mm wall ring instead of being a slab. That rectangle touches nothing: the first-floor wings are x 3000-8000 and 16000-21000, the north bar starts at y=18000. VILLA_PLAN_FF.dxf confirms a closed independent loop -- outer 9000/15000 × 9500/12900, inner 9400/14600 × 9900/12200 -- with no segment linking it to the rest of the floor, and A-202 draws it as a separate box sitting in the pool. It is a 12 m² room hovering 4.1 m above the water, reachable only by ladder, and its solid mass is what seals the top of the double-height wall in VILLA_VIEW_POOL_EYE.png. The one move that was supposed to shade the water's edge instead blocks the view it was shading.

**Proposed fix:** Take the cantilever out of FF_FOOT entirely and add it as bare geometry: extrude the rectangle (9000, 9500, 15000, 12900) at FF..FF+SLAB only -- a 500 mm slab with a drip and a 20 mm shadow gap -- so the double-height glazing runs full height under a 3.0 m soffit. If a first-floor room over the pool is wanted, it has to connect: extend the east or west wing south to y=9500 and cantilever from there.

### 42. Service entrance opens directly into the women's majlis

**Severity:** FATAL

**Numbers:** service door in majlis east wall (x 20600-21000, y 18700-19800); kitchen 12,175 mm away; dirty kitchen 0 m² against a 12-18 m² requirement.

**Evidence:** Line 257: the service door void sits at x 20700-21300, y 18700-19800 -- in the east wall of the north bar. The north bar's east room, x 15575-20600, is WOMEN'S MAJLIS (villa_sheets.py line 31). The show kitchen is at the opposite end, x 3400-8425, 12.2 m away across the entrance hall. The docstring (line 46-48) claims 'service on the east boundary reaching the dirty kitchen without crossing guest or family space'; the model does the reverse. There is no dirty kitchen and no pantry in the model at all. The coffee route the research calls out -- kitchen to majlis without crossing family living -- runs kitchen → entrance hall → majlis, straight across the front door on the axis.

**Proposed fix:** Swap the ground-floor north bar end-for-end: majlis to the west (adjacent to the guest entry, off the hall), kitchen to the east where the service door is. Then add a 1.2 m service corridor along the east boundary from the service door to a discreet 900 mm leaf into the majlis, and a dirty kitchen 12-18 m² between them. That also fixes the dining adjacency below.

### 43. The only stair is a 55° ladder that stops 196 mm below the landing; basement and roof have no access at all

**Severity:** FATAL

**Numbers:** 244 mm rise / 170 mm going / 55.1°; 3904 vs 4100 mm (−196); basement 142 m² and roof pavilion 30 m² with 0 means of access; reachable GFA 407 − 30 − 18 = 359 m².

**Evidence:** Lines 232-235: 16 treads at 170 mm going and 244 mm rise. Pitch 55.1°. 16 × 244 = 3904 mm against a floor-to-floor of FF − GF = 4100 mm, so the top tread lands 196 mm short. Research (VILLA_RESEARCH.md §2) gives going ≥280 (luxury 300-320), riser 100-180 (luxury 170), max 30°. There is no second stair anywhere in the model: the 142 m² semi-basement (BS 3000-21000 × 15000-24000, floor −2800) has no stair, no ramp and no vehicle access, and the 30 m² roof pavilion (PV, line 169) has no stair either. No lift, on a four-level house.

**Proposed fix:** Rebuild the stair as 24 risers × 171 mm with 300 mm going, two flights of 12 about a half-landing -- footprint 1.4 m wide × 3.6 m per flight, which fits the 13000-14600 × 18700-21900 zone if it is widened to x 12600-15400 and turned. Add a second stair in the north bar's west end running basement → roof, and a 1.6 × 1.7 m lift shaft beside it. Assert in build(): risers × rise == floor-to-floor, and rise ≤ 180, going ≥ 280.

### 44. Three of four bedrooms have no bathroom; two are entered through other bedrooms; the master bedroom is the smallest room on the floor

**Severity:** FATAL

**Numbers:** bathrooms: 1 for 4 bedrooms. Master suite 24.9 m² vs 55-75. Master bedroom 9.12 m² vs 28-35. Landing 35.6 m². 4 rooms with a single door off another habitable room.

**Evidence:** PARTS_FF (lines 205-212) creates only one wet partition set, the master en-suite. BEDROOM 1, 2 and 3 have no en-suite, no wardrobe and there is no family WC on the floor. A-202 prints the areas straight off the model rectangles: MASTER BEDROOM 9.1 m² (2.85 × 3.2), DRESSING 6.5, MASTER ENSUITE 9.3 -- a 24.9 m² master suite against the research target of 55-75 -- while BEDROOM 3 is 26.1 m², BEDROOM 1 and 2 are 22.5 m² each, and the LANDING is 35.6 m², the largest room on the floor. Circulation is worse than the areas: DOORS_FF gives BEDROOM 1 one door, from BEDROOM 3, and BEDROOM 2 one door, from the MASTER BEDROOM. Both are walk-through rooms off another bedroom. The same defect runs on the ground floor: FORMAL DINING is reachable only through the SHOW KITCHEN, STUDY only through the WOMEN'S MAJLIS.

**Proposed fix:** The cause is the 1.0 m light slots (lines 174-177), which sever both wings from the centre at every level, leaving each wing hanging off the single north-bar room beside it. Bridge the slots at first floor with a 1.2 m glazed link at each side (cut the slot void only from GF−SLAB to GF+GF_CH, not to RF+SLAB+PARAPET), giving the landing direct doors to bedrooms 1 and 2. Then re-cut the master zone: bed 30 / dressing 16 / en-suite 19 needs 65 m², which means the master takes the whole east wing plus the east end of the north bar, and the landing drops to 12-14 m².

### 45. Every ground-floor opening, including both entrance doors, is sealed by a 100 mm membrane of wall

**Severity:** FATAL

**Numbers:** 8 of 11 external openings blocked; 60.1 m2 of glazing and doors that does not exist; residual wall 100 mm in every case; walls are 400 mm, voids are cut at 300 mm

**Evidence:** villa_3d.py sets WALL = 400.0 (line 80) but every opening void is written against a hard-coded 300. The shell wall ring at the wings' south face occupies y 12500-12900; the glazing voids run to WG_Y0 + 300 = 12800 (lines 238-244). 100 mm of wall is left standing across the full width and height of each. I ran a shapely adjacency test on all seven ground rooms against all five modelled openings with a 1 mm tolerance: every room returned NO OPENING. Blocked: GF living-volume glazing 5.6 x 3.3 m (18.5 m2), GF west and east wing windows 2.6 x 2.65 m (6.9 m2 each), FF west and east wing windows, the 1.5 x 2.4 m GUEST ENTRANCE DOOR (void y 23700-24300 against a wall band 23600-24000, line 248), and the 1.1 x 2.4 m SERVICE ENTRANCE DOOR (void x 20700-21300 against a wall band 20600-21000, line 257). The only external openings that actually penetrate are the two first-floor clerestory bands and the cantilever-island window -- and that one works precisely because it is the single opening written as WG_Y0 + WALL + 300 (line 241) instead of WG_Y0 + 300. As modelled the villa is a sealed concrete box that cannot be entered or seen out of. The S elevation confirms it: what reads as a window is a 300 mm deep blind recess with a wall behind it.

**Proposed fix:** One symbol, six call sites. Replace the inner-side literal 300 with WALL + 100 in lines 239, 243, 244, 249 and 258, exactly as line 241 already does. Better, add a helper `def pierce(...)` that takes the wall band as an argument so an opening can never again be specified independently of the wall thickness it must cross -- this is the same class of bug as the reset-after-set shape already in the project notes: a constant standing in for a parameter.

### 46. The sunken courtyard is punched through the middle of the family living room floor, and the plan cut hides it

**Severity:** FATAL

**Numbers:** Court 5.0 x 4.0 m at x 9500-14500, y 15400-19400. Removes 15.0 m2 of the 28.6 m2 family living room (52%), 4.0 m2 of the only route from hall to living room, 1.1 m2 of the stair footprint, 0.9 m2 of the guest WC. Unguarded drop 3.7 m. Real living-room floor 13.6 m2, not 28.6 m2.

**Evidence:** CT_X0..CT_Y1 (villa_3d.py lines 104-105) place the court at x 9500-14500, y 15400-19400, and line 132 cuts it from BASE_FL up to GF + 200 = 1100 -- through the ground slab. Family living is x 9400-14600, y 12900-18400; the intersection is 5.0 x 3.0 m = 15.0 m2. The court was intended to sit beside the house lighting a basement; it is in fact a 20 m2 hole in the middle of the piano nobile, straddling the living room, the hall-to-living threshold and the guest WC. It never appears on A-201 because derive() cuts the GF plan at z = GF + 1200 = 2100 (line 352) while the court rim is at 1100, and the code deliberately disables 'beyond' projection (comment at line 349). villa_sheets.py line 33 then bills FAMILY LIVING at 28.6 m2 from the schedule rectangle. The one drawing that would expose this -- section A-A on the axis at x=12000 -- passes through the court but is rendered at a scale and lineweight where it does not read.

**Proposed fix:** Move the court south out of the occupied floor, or north into the front setback. The clean move is to slide it to y 19000-23000 under the entrance hall and glaze the basement's north wall to it, keeping the living room floor whole. Whatever you choose, cut the GF plan at 1100+ or re-enable a dashed below-cut projection so a 20 m2 hole in the floor cannot be invisible, and derive the room schedule by subtracting void polygons from the room rectangles instead of using the rectangle area directly.

### 47. The first-floor cantilever mass is a disconnected island with no way to reach it

**Severity:** FATAL

**Numbers:** 20.4 m2 of enclosed first floor, 400 mm walls, 3.7 m tall, a 5.6 x 2.6 m window -- 1.00 m from the wings across the light slot, 5.1 m from the north bar across the void. 18 m2 of it is counted in the 407 m2 GFA.

**Evidence:** FF_FOOT (villa_3d.py lines 140-142) unions the north bar, two wings and the cantilever piece (LV_X0, WG_Y0 - CANT, LV_X1, WG_Y0 + WALL) = x 9000-15000, y 9500-12900. A shapely unary_union of those four rectangles returns a MultiPolygon with two components: the 163.0 m2 north-bar-plus-wings body and a separate 20.4 m2 island, minimum separation 1.00 m -- the light slot, which is itself voided out from z 400 to 10300. There is no first floor over the living volume, so the island's nearest floor to the north is the north bar at y 18000, 5.1 m away across the double-height void. No bridge, stair or landing is modelled. Its only opening (line 240) is a 5.6 m wide, 2.6 m tall hole in its north wall with a 4.40 m drop to the living-room floor and no balustrade. build() then adds ct = 18 m2 into the first-floor and GFA figures (lines 293-296), so the headline 407 m2 / 4,381 sq ft includes a room nobody can enter.

**Proposed fix:** Decide what the cantilever is. If it is habitable (a study or master terrace room), the first-floor slab has to return across the void -- which is also the 60/40 fix below. If it is a shading canopy over the pool, model it as a slab and parapet, not a walled and glazed shell, and take its 18 m2 back out of the GFA. Add an assertion in build(): the first-floor footprint must be a single connected Polygon, and every enclosed first-floor area must be reachable from the stair landing.

### 48. The main stair is a 55-degree ladder and does not reach the first floor

**Severity:** FATAL

**Numbers:** 244 mm riser / 170 mm going, pitch 55.1 degrees. 16 risers x 244 = 3904 mm against a floor-to-floor of 4100 mm -- 196 mm short. Stair well 1.6 x 3.2 m = 5.1 m2 against a researched 14-18 m2.

**Evidence:** villa_3d.py lines 232-234: each tread is blk(13000, 18700 + i*170, GF + i*244, 14600, 18870 + i*170, GF + (i+1)*244) -- the y extent advances 170 mm per step and the z extent 244 mm. VILLA_RESEARCH.md section 2 specifies going >= 280 mm (luxury 300-320), riser 100-180 (luxury 170), max 30 degrees. This is 170/244 at 55.1 degrees, steeper than most domestic code maxima of roughly 42 degrees, and it stops at z 4804 with the landing at 5000. The geometry problem underneath is that the well is too small: at a compliant 171/300 the 4100 mm rise needs 24 risers and 6.90 m of run -- a half-turn in roughly 2.3 x 4.5 m = 10.3 m2, double the 5.1 m2 provided. The stair is also the one element that should dramatise a 7.80 m volume and it is instead buried against the hall's east wall with no daylight on it.

**Proposed fix:** Rebuild as a half-turn or dog-leg at 171 riser / 300 going, 24 risers, landing at riser 12. Take the space from the entrance hall (20.9 m2, currently doing nothing but circulation) and put the flight against the double-height volume's east wall so it climbs through the tall space under a rooflight -- the Interlude House move the design basis cites but does not execute. Add a check in build(): n_risers * rise must equal FF - GF exactly, and 2R + G must fall in 550-700 with R and G each inside the researched band.

### 49. No car fits between the gate and the house -- the porch is 4.0 m deep and 4.65 m gross; the second bay is unreachable

**Severity:** FATAL

**Numbers:** porch 7.0 x 4.0 = 28.0 m2 | gross depth 4,650 mm | max car behind a closed gate 4,050 mm | bay 2 needs 7,307 mm of run, has 4,250 mm | research min 5.5 x 5.5 = 30.3 m2

**Evidence:** villa_3d.py:110-111 sets PORCH_Y0..Y1 = 24400..28400 = 4.0 m deep, not the 5.2 m its own comment on line 109 claims (a 1,200 mm comment/model mismatch). The absolute parking depth is fixed by the villa's north face (NB_Y1 = 24000) and the inner face of the boundary wall (28650): 4,650 mm. A 5.0 m Range Rover nosed to the villa render leaves its tail 350 mm past the property line, so the gate cannot close; a 5.21 m GLS, 560 mm. With 300 mm clearance at each end the longest car that can stand behind a closed gate is 4,050 mm -- a Golf. Research (VILLA_RESEARCH.md:295-298) puts the 2-car minimum at 5.5 x 5.5 m / 30 m2; the porch is 28.0 m2 and 27% short on the governing dimension.

The second bay is worse. The blade wall at x 10250..10500 and the beams at 3600 and 6900 imply two bays: 3850..6900 and 7150..10250. The vehicle gate is x 3800..8300, so bay 2 overlaps the gate by only 1,150 mm and its centreline sits 2,650 mm east of the gate centreline. A reverse-curve at a 5.7 m kerb radius needs 7,307 mm of straight-line travel to shift 2,650 mm laterally; the gate face to the porch's south edge gives 4,250 mm -- 3,057 mm short before you add any car length. Bay 2 cannot be entered by any vehicle. Capacity is one car, not the two labelled in villa_sheets.py:88-90.

**Proposed fix:** The cars have to come back inside the building line; a 5.0 m front setback cannot hold them. Take the north bar's west end -- currently SHOW KITCHEN, 26.1 m2 -- for a garage x 3400..9400, y 18000..23600 = 6.0 x 5.6 m = 33.6 m2 internal (delete the partition at y 18250-18400, villa_3d.py:192). Two 2.7 m doors in the north wall at y = 24000, per the research's "two single 2.7 m doors beat one 5.0-5.5 m double". Shift the vehicle gate 350 mm east to x 4150..8650 so it is on the garage centreline (x 6400): straight in, straight out, one movement, using the 4.65 m front court as the apron. The kitchen drops into the west wing (22.5 m2, inside the 20-28 luxury band); the entrance hall's west wall moves 975 mm east, taking the hall from 20.9 to 17.8 m2.

### 50. Zero standing space at the gate, and every car must reverse ~11 m blind onto the street past a 2.4 m solid wall

**Severity:** FATAL

**Numbers:** standing space 0 mm provided vs 5,500-6,000 required | turning circle available 4,650 mm vs 11,000-12,000 needed | aisle 4.65 m vs 5.5 m min | blind reverse ~11,250 mm | visibility splay 0 x 0 m

**Evidence:** The gate leaves sit in the boundary wall at y 28650..29000 -- i.e. on the property line (villa_3d.py:284). Standing space inside the plot is 0 mm; the porch canopy edge is 250 mm behind the gate. Research (VILLA_RESEARCH.md:288) requires 5.5-6.0 m between gate line and street, so a car waiting for the gate to open stands entirely in the public carriageway. Deficit 5,500-6,000 mm.

Exit is worse. The front court is 4.65 m deep; the largest turning circle it can contain is 4,650 mm against the 11-12 m a car needs. The research hammerhead (6.0 x 3.0 bay off a 5.5 m aisle) needs 850 mm more aisle than exists, and a 6.0 x 12.0 forecourt is 7.35 m too deep. Reversing is therefore mandatory: roughly 4.65 m to the plot line + ~2 m of footpath + a 5 m car = ~11.25 m of blind reverse into traffic. The 2,400 mm solid boundary wall (BH on villa_3d.py:279) runs unbroken to both gate jambs, so there is no visibility splay at the crossover in either direction. Research also puts Gulf front walls at 1.8-2.0 m, often capped at 1.2-1.5 m solid (VILLA_RESEARCH.md:279-281) -- 2.4 m solid across the front is both a likely code breach and the thing that blinds the driver.

**Proposed fix:** Accept that 5.5-6.0 m of standing space is unattainable inside a 5.0 m front setback and design for it: recess the gate 1,500 mm (leaf line to y = 27150) with 45-degree splayed returns, drop the wall to 900 mm for 2,400 mm each side of the opening to give a 2.4 x 2.4 m visibility splay both ways, and fit a loop detector so the gate is already open on approach. Drop the front boundary wall to 1,800 mm overall with the top 600 mm as an open screen. Combined with the garage fix, the gate then serves a straight-in/straight-out movement instead of a blind manoeuvre.

### 51. The pool has a 0 mm surround on the house side -- you step out of the living room into 1.4 m of water. There is no terrace anywhere on the site.

**Severity:** FATAL

**Numbers:** north surround 0 mm (research 1.2 m min) | 200 mm step then 1.4 m water off a 5.6 m opening | E/W surrounds 8.75 m (2x the 3.5-4.5 needed) | south 1.25 m, 1.0 m of it an open 1.54 m trench | paved terrace on site: 0 m2

**Evidence:** POOL_Y1 = 12500 is identical to WG_Y0 = 12500, the villa's south face (villa_3d.py:95, 87). The pool's north water edge is the building line. The 400 mm coping ring at y 12500..12900 lies underneath the villa's south wall and clashes 300 mm into the ground slab. Research (VILLA_RESEARCH.md:307-308) asks for 1.2 m minimum on back sides, 1.5 m where people walk, 3.5-4.5 m on the lounging side: provided is 0 mm.

The section makes it a fall hazard. FFL is 900, pool coping and top water are both 700, invert is -700. The structural glazing void (villa_3d.py:238-239) removes 5,600 mm of that wall from z 1000 to 4300. So the primary living space opens 5.6 m wide onto a 200 mm step down, 400 mm of coping, then 1.4 m of water, with no threshold, deck, level change or barrier.

East and west surrounds are 8.75 m each -- roughly twice the 3.5-4.5 m the research wants for lounging, and in the wrong places. The south end is 1.25 m to the wall face, and the catch-basin trench (1.0 m wide, invert -900, i.e. 1.54 m deep and uncovered as modelled) occupies most of it. Not one square metre of paved terrace -- lounge, dining or otherwise -- is modelled anywhere on the site.

**Proposed fix:** The rear zone is only 12,150 mm deep inside the wall and the scheme gave 10,300 mm of it to the pool shell. A compliant north-south pool is 12,150 - 1,500 (boundary/45-degree clearance) - 3,500 (lounging terrace) - 800 (coping) = 6,350 mm of water: shorter than what is drawn, not longer. So rotate the pool through 90 degrees. Water 13.0 x 4.0 m at x 5150..18150, y 2350..6350; shell x 4750..18550, y 1950..6750. That gives 1.60 m to the rear wall face, 4.40 m west, 5.10 m east, and a full-width 23.3 x 5.75 m = 134 m2 terrace between pool and house -- enough for the research's lounge (3.5-4.5 m) and dining (4.5-5.0 x 5.0-6.0) side by side. Pool becomes 52 m2 (7.5% of plot) with a 13.0 m lap length, clearing the 12 m threshold the current 9.5 m misses. Keep the axis with a 500 mm rill running south from the living room across the terrace to meet the pool's north edge at right angles -- which is precisely the Court of the Myrtles relationship the docstring invokes.

### 52. The sunken courtyard sits inside the building footprint -- it holes the family living room and the stair, and receives zero daylight

**Severity:** FATAL

**Numbers:** court 20.0 m2 inside the footprint | 15.0 of 28.6 m2 of family living is a 3.70 m void (52%) | stair tread 0 cut 1,500 of 1,600 mm wide | daylight to the court 0 | basement 142 m2 with no means of access

**Evidence:** CT is x 9500..14500, y 15400..19400 (villa_3d.py:104-105) and is cut from BASE_FL to GF+200, i.e. -2800 to 1100 (line 132). That rectangle is inside the ground-floor footprint, not in the open ground. Consequences, all measured:

- FAMILY LIVING is 9400..14600 x 12900..18400 = 28.6 m2. The court removes 5.0 x 3.0 = 15.0 m2 of its floor -- 52% of the room is a 3.70 m drop into the basement. villa_sheets.py:33 still schedules it as 28.6 m2, and the GF plan is cut at z = 2100, above the void's 1100 top, so the drawing shows a floor that does not exist.
- The stair (villa_3d.py:232-234) starts at x 13000..14600, y 18700. Tread 0 loses 200 of its 244 mm over 1,500 of its 1,600 mm width; treads 1-4 survive but hang over the void with no floor beneath them.
- It gets no light. The roof slab spans y 9500..24000 at z 8700 and the first-floor slab spans the north bar at z 4500; the court void stops at 1100 and cuts neither. The "sunken courtyard" is a fully roofed shaft. That destroys the premise of research finding 2 -- the court is what makes the basement a served space rather than a cellar (VILLA_RESEARCH.md:24-27, 58-60).
- Separately: the only stair modelled runs GF 900 to 4804. Nothing -- no stair, no lift, no ramp -- reaches the basement at -2800. 142 m2 of staff and plant accommodation is unreachable.

**Proposed fix:** A sunken court has to be in open ground. With the pool rotated south (see the pool finding), place it in the rear garden clear of the 3.0 m roof cantilever (which occupies y 9500..12500) -- e.g. 5.0 x 4.0 m in the east lawn at x 18000..23000, y 7500..11500, glazing the basement's east wall full height -- or, following AB House, put it in the front forecourt east of the rill at x 16000..21000, y 24400..28400 and move the pedestrian gate east to x 21400..22600 to keep the walk clear of it. Either way shrink the basement to y 18000..24000 (18 x 6 = 108 m2, ample for maid 15 + laundry 10 + store 8 + plant 16 + pool plant 14 = 63 m2 net) so it no longer runs under the living room. Then add the basement flight and a 1.6 x 1.7 m lift shaft; the research schedules both (VILLA_RESEARCH.md:327).

### 53. The double-height volume -- the most expensive thing in the villa -- is not visible from outside

**Severity:** MAJOR

**Numbers:** DH clear 7300 mm. Proposed single void 6000 x 7200 = 43.2 m2 vs current stacked 5600x3300 + 5200x3700 = 37.7 m2 split across two planes.

**Evidence:** Line 151 removes the slab over y 12500-18000, i.e. the void sits at the BACK of the living room, behind the cantilever. The research explicitly says the opposite: '40% double-height at the glazed garden edge'. At the glass you have the GF opening (z 1000-4300) on the cantilever face and, 3000 mm behind and above it, the FF opening (z 5300-7900) on the wing line. Two stacked windows on different planes with a floor between. You have a 7.30 m clear volume and you drew a floor line across its facade. Nobody outside will ever know it exists.

**Proposed fix:** Swap it: put the double-height at the garden edge and the single-height (3.0-3.2 m sofa zone) at the back, per the research's 60/40 rule. Then cut ONE opening, 6000 w x 7200 h (z 1000-8200), in a single plane recessed 600 mm behind the cantilever face, with a structural glass corner and no corner post at the west end -- the research names that as the single most legible architect signal in a villa. This becomes the one dominant void: 43 m2, roughly half of all void on the elevation, against small incisions everywhere else.

### 54. Every window is a flush hole -- the 400 mm wall's one asset is thrown away

**Severity:** MAJOR

**Numbers:** Wall 400 mm; current effective reveal 0 mm (opening overshoots the face by 300 mm each side). Target 400-550 mm reveal on wings, 600 mm on the centre; 20 mm shadow gap at every junction.

**Evidence:** Openings are cut with 300 mm overshoot on both sides of a 400 mm wall (e.g. line 174: y from WG_Y0-300 to WG_Y0+300, wall is 12500-12900). So the void is 600 mm through a 400 mm wall and the glazing plane is nominally flush with, or outside, the external face. There is no reveal, no shadow, nothing. This is why both views read as cardboard: not one line in the elevation is a shadow line. Same at the top -- the roof slab (line 154) is flush with the walls, zero overhang, and the parapet sits flush on it, so the building has no expressed top either.

**Proposed fix:** Two-stage every opening: outer reveal at full size 200 mm deep, glass plane recessed a further 200-350 mm, giving 400-550 mm of shadow on every jamb and head. On the centre, recess the whole glazed plane 600 mm. At the top, recess the parapet 300 mm behind the wall face and put a 20 mm shadow gap at the slab-to-wall junction. Add a 20 mm shadow gap at the cantilever soffit-to-wall junction, which the research names explicitly.

### 55. The fin geometry cannot shade west sun no matter how deep you make it

**Severity:** MAJOR

**Numbers:** Current cutoff arctan(420/450) = 43 deg vs required 0-15 deg HSA. Slenderness 180:7800 = 1:43. Proposed 300 x 900 @ 1200 c/c rotated 60 deg, z 0-10300, slenderness 1:34.

**Evidence:** 450 deep x 180 wide at 600 c/c gives a clear gap of 420 mm. A fin perpendicular to the wall blocks a ray only when tan(HSA) > 420/450, i.e. above 43 degrees off the wall normal. At 25N the killer west load is 16:00-18:00, solar azimuth 272-285 degrees, altitude 30 down to 15 -- horizontal shadow angle 0-15 degrees off normal. The fins block nothing in the window that matters. Deepening does not fix it: at 300 x 900 @ 1200 c/c the cutoff is still 45 degrees. Perpendicular fins are geometrically incapable of blocking near-normal sun. Separately the proportion is wrong: 180 wide x 7800 tall is 1:43, which reads as a catalogue aluminium louvre screen, and they float 250 mm off the wall, start 900 above grade and stop at 8700 with 1600 mm of blank parapet above -- they align to nothing top or bottom, so they read as bolted on.

**Proposed fix:** If fins stay: rotate each fin 55-65 degrees from the wall plane so its face is roughly normal to azimuth 280 degrees; 300 wide x 900 deep at 1200 c/c; run them grade (0) to parapet top (10300) so they read as piers, not a screen; set the outer face flush with the wall plane at x=3000, not 250 mm proud; and put glass behind them. Preferred alternative: delete them and use the 1800 mm recess described above -- the wall does the shading, the elevation gains a 1800 mm deep shadow, and you stop paying for 9 concrete fins.

### 56. Zero material or textural differentiation; no base, middle or top

**Severity:** MAJOR

**Numbers:** Materials currently: 1. Target 3. Plinth 900 h. Stone 40 mm, courses 600 x 1200. Shadow gaps 20 x 20.

**Evidence:** The model is one boolean solid. No cladding change, no plinth, no reveal, no coursing, no shadow gap, no parapet expression. The research names the devices -- 20 mm shadow gaps, 30-40 mm stone on kerf, 100-150 mm stone with a rebated return so no thin edge shows, one setting-out grid -- and not one appears. The 900 mm privacy raise (line 69) is a real move that has no external expression whatsoever: the house just starts at 900. A 10.3 m tall elevation with a single 1100 mm parapet band at the top and nothing else is a spec elevation.

**Proposed fix:** Exactly three materials, each with a job. (1) Plinth: the 900 raise as a dark basalt/granite base, grade to GF, 20 mm shadow gap at its top, returning into the garden as the pool coping so house and water share one material. (2) Stone field: both wings and the north bar, 40 mm limestone on stainless kerf, 600 x 1200 courses on the grid, 20 mm open joints, 150 mm rebated return at corners. (3) Concrete field: the central volume, cantilever and roof pavilion, fair-faced, 1200 x 2400 shutter panels with cone holes on the grid, 20 mm shadow gap at every junction with stone. The parti (mass-void-mass) then reads in material as well as form.

### 57. The roof pavilion is a cake topper aligned to nothing, on a bare 261 m2 slab

**Severity:** MAJOR

**Numbers:** Current PV 6000 x 5000 x 3000 h, centred on AXIS, 14.5 m from the garden edge. Proposed 4800 x 5400 x 2700, two faces aligned to walls below. Roof deck 261 m2, pergola 90 m2 (BUA-excluded).

**Evidence:** PV = (9000, 19000, 15000, 24000), line 106. It is dead on the axis in x (so in south elevation it appears as a symmetrical block plonked on the centreline) and jammed hard against the north boundary in y, over the garage and entrance. It reads as centred and arbitrary at the same time. It aligns with no vertical plane below except the central volume it does not sit above, gives no shade to the south roof terrace, and stands as a tower over the street entrance. Meanwhile the roof is 18.0 x 14.5 = 261 m2 of bare slab with a 1100 parapet and nothing on it. The research points at 60-90 m2 of shaded roof terrace under a pergola, BUA-excluded in Dubai -- free luxury you have not taken.

**Proposed fix:** Move PV to (16200, 18000, 21000, 23400): 4800 x 5400, east face on x=21000 (the east wing's east wall, a plane running basement to roof) and south face on y=18000 (the north bar's south wall). Two of its faces now continue walls below, so it reads as the head of a vertical element, not a topping. Drop clear height 3000 to 2700 and open the south and west sides as a pergola -- lightweight above solid. Then add a 12000 x 7500 = 90 m2 aluminium pergola over the south roof deck at 2700 clear on 200 x 200 posts at 3000 c/c. That gives the top of the elevation a second horizontal layer, which a flat 18 m parapet band badly needs.

### 58. There is no setting-out grid -- the research says that discipline is what reads as expensive

**Severity:** MAJOR

**Numbers:** 18000 / 600 = 30 modules. Current dims sharing no common factor: 180, 250, 400, 450, 500, 700, 750, 1000, 1100, 2250, 2600, 2650.

**Evidence:** Dimensions in use: wall 400, slab 500, parapet 1100 with a 250 skin, fin 180 wide x 450 deep at 600 c/c, slot 1000, bays 5000/6000, windows 2600 wide x 2650 and 2250 high, opening offsets 200 and 300, rill half-width 750, pool raise 700, roof pavilion skin 250, fin setback 250. Not one common module. The fins run x 2300-2750 across y 12800-17780 while the wing is 12500-18000, so they stop 220 mm short at each end -- off-grid against their own host. The research is explicit: stone joint, ceiling joint, door head, window head and skirting all on the same module, and that is what reads as expensive.

**Proposed fix:** Adopt a 600 mm setting-out module and force every dimension to it. Bays 4800 / 1800 / 6000 / 1200 / 4200 = 18000. Slab 600. Parapet 1200 (still above the 1100 minimum). Windows 1200 / 1800 / 3600 / 6000 wide, 2400 / 3200 / 6600 / 7200 high. Fins 300 at 1200 c/c. Stone courses 600 x 1200. Shadow gaps 20. Keep the 400 mm wall as structure but set out from face lines that land on the 600 grid.

### 59. The 1.0 m light slots are neither light wells nor reveals

**Severity:** MAJOR

**Numbers:** Current 1000 w x 9900 h = 1:9.9. Proposed 1800 (west) and 1200 (east), or 300 mm reveal.

**Evidence:** Lines 162-166: slots 1000 wide x 6100 long x 9900 tall between grade and parapet top. Aspect 1:9.9. The research's own courtyard numbers are H/W 1.0-1.5 for daylight without glare and 1.5 for summer shade; at 1:9.9 this is a chimney, daylight at the bottom is negligible, and it is unmaintainable. Compositionally they are worse: at 1000 mm across an 18000 mm elevation they read as pinstripes -- in the render they are literally two hairlines. They are too thin to register as void and too wide to read as a reveal, which is the worst of both.

**Proposed fix:** Commit one way. Either widen the west slot to 1800 and the east to 1200 (per the asymmetric bay rhythm above) so they become legible voids with H/W 5.5 and 8.3 -- still tall, but they read as slots and they let you glaze both flanks of the wings, fixing the blank-end-wall problem; or collapse them to 300 mm true reveals so the wings and centre read as three separated masses with a shadow line between. Do not leave them at 1000.

### 60. The pool aligns with nothing and its deck margins are backwards

**Severity:** MAJOR

**Numbers:** Current 5000 x 9500 = 1.9:1, 47.5 m2, side margins 9150 / 9150, south end 1250. Proposed 4200 x 10700 = 2.55:1, 45 m2 (6.5% of plot), west terrace 6400, south end 1800.

**Evidence:** POOL 5000 x 9500 = 47.5 m2 at 1.9:1. The docstring on line 32 promises 12.0 x 4.0 m; the code does not deliver it. More important, the research's headline finding is the Alhambra 4.8:1 axial water body -- 1.9:1 is a fat rectangle that reads as a domestic swimming pool. And it aligns with nothing: 5000 wide against a 6000 central volume, not to the slots, not to the bays. Margins are inverted -- 9150 mm of dead deck on the east AND west, but only 1250 mm south of the catch basin, against the research's 1.2 m minimum on back sides and 3.5-4.5 m on the lounging side. In the aerial it reads as a small rectangle floating in an empty forecourt.

**Proposed fix:** Narrow to 4200 (7 modules) and lengthen: y 1800 to 12500 = 10700, giving 2.55:1 and 45 m2, still running 3000 mm under the cantilever. Centre it on AXIS so it sits inside the 6000 central bay with a 900 mm reveal each side -- the water now visibly belongs to the room. Then make the garden asymmetric to match the elevation: 6400 mm lounging terrace on the WEST (x 3500-9900) at the research's 3.5-4.5 m, lawn on the east. South end deck 1800 mm clear of the basin, not 1250.

### 61. The waterwall and its basin are invisible from every occupied position

**Severity:** MAJOR

**Numbers:** Sightline over the crest at (y 3000, +700), basin working level ≈ -300 mm. Living-room eye at +3.0 m / y 13500: sightline passes basin at +503, clearing the basin water by 803 mm. Garden eye 1.6 m at y 6000: +430, clearing by 730 mm. First-floor cantilever eye at +6.1 m: +6, clearing by 306 mm. To see the sheet or the basin at standing eye height you must be within 400 mm of the crest.

**Evidence:** The spill face is at the pool's far south end, y 3000, facing the south boundary wall (inner face y 350), and the crest sits 700 mm above the garden. Every viewer in the house, on the cantilever terrace or on the garden deck is north of it and above it, so the 700 mm rim occludes its own spill face and basin. The only position from which the waterwall reads is the 1.25 m strip between the basin outer face (y 1600) and the boundary wall -- a dead service margin. Research §1 option (b) justifies the raised pool specifically because "the spill face becomes a waterwall into a visible basin." The geometry defeats the only reason for the raise. What a guest actually sees from the living room is a 700 mm blank concrete band across the far end of the water, with a 2.4 m stone wall behind it.

**Proposed fix:** Move the spill to a long side. Put the crest on the west face (x 9100, 9.5 m long) with the basin running alongside at x 7900-9100, and view it obliquely from the east terrace and from the cantilever above -- the sheet then reads across its full 9.5 m at 15-30° rather than end-on. If the south end must stay, drop the pool rim there to +450 and step the basin up to invert -450 so the sightline from a garden eye at 1.6 m at y 6000 lands inside the basin instead of 730 mm above it.

### 62. The spill is on the 5.0 m short side, not the long side the brief and docstring both specify

**Severity:** MAJOR

**Numbers:** Pool 5.0 m (x) × 9.5 m (y). Long sides = east and west faces, 9.5 m. Spill face as coded = south, 5.0 m -- 47% shorter than a long side.

**Evidence:** POOL_X0/X1 = 9500/14500 and POOL_Y0/Y1 = 3000/12500 (lines 93-94) make the north and south faces the short ones. The docstring at line 20 says the pool "overflows one long side as a waterwall," and the brief says "overflowing its south long side." The south side is the short side. This is not just nomenclature: it halves the crest length, and crest length is what sets the sheet. It also compounds the previous finding, because the short side is the one pointing away from the viewer down the 9.5 m axis.

**Proposed fix:** Either rotate the pool (POOL_X0/X1 = 8000/17500 for a 9.5 m east-west width, POOL_Y0/Y1 = 3000/8000 for 5.0 m north-south) so the south face is genuinely the long side and faces the house broadside, or accept the north-south axis and move the spill to the west long face per the previous finding. Do not leave the docstring claiming a long-side spill that the constants contradict.

### 63. No plant room is designated, and the shortest possible pipe run is 20.2 m against a 15 m limit

**Severity:** MAJOR

**Numbers:** Basin (x 12000, y 2100, invert -900) to the only candidate space, the basement (y ≥ 15000, floor -2800): 3.4 m east to clear the shell + 12.9 m north + 1.9 m vertical drop + 2.0 m in-room = 20.2 m developed, 35% over the 15 m rule; 25.0 m with four 90° bends at 1.2 m equivalent length, 67% over.

**Evidence:** The script models a basement envelope (lines 101-104, 123-127) but designates nothing inside it -- no plant room, no pool plant, no balance chamber, no tank. Research §3 requires a pool plant room of 12-18 m² clear at 2.4 m clear height, floor 1.0-1.5 m below pool water level, with a floor gully, a 1.0 m clear door, mechanical ventilation and acoustic separation, and states "keep the pipe run under 15 m." The direct line from basin to basement is blocked: the pool shell base slab occupies y 2600-12900 continuously across x 9100-14900, so 10.3 m of the route is under a water-retaining structure that cannot have services cast through it if leak detection is to work, and the remaining 2.1 m passes under the living-volume foundations. Separately, the basement floor at -2800 is 3.5 m below the pool water line at +700, against the research band of 1.0-1.5 m -- good for flooded suction, but it means the overflow pump lifts 3.5 m static before friction, and the room is 2.0 m deeper than it needs to be.

**Proposed fix:** Do not put the pool plant in the main basement. Sink a dedicated pool plant chamber alongside the pool on the west deck, x 6000-9000, y 5000-10000 (15 m² clear), floor at -800 (1.5 m below pool water level, exactly the research band), roofed at grade with a removable deck hatch and a 1.0 m door off the side service strip. Basin-to-plant run then drops to about 5 m, the run stays outside both the shell and the house foundations, and the chamber is 12 m from the nearest bedroom, satisfying the acoustic rule. Add the floor gully and a mechanical vent riser in the boundary-wall pier.

### 64. Basin volume is adequate but its form is wrong: an open trough cannot hold a stable level

**Severity:** MAJOR

**Numbers:** Basin 5.8 × 1.0 × 0.9 m = 5.22 m³ gross; usable 3,045 L after 200 mm freeboard and 175 mm low-level cut-out. Required = max(40.7 L/m² × 47.5 m² = 1,933 L; honest build-up 800 bather + 150 transit + 1,500 backwash = 2,450 L) = 2,450 L. Margin 24%. But 8-10 bathers displacing 500-800 L over a 5.8 m² plan area move the visible level 86-138 mm. Invert -900 = 1.6 m below the pool water line, outside the research band of 1.0-1.5 m.

**Evidence:** BASIN_D = 900 (line 97) with the void 5.8 m × 1.0 m (line 195-196). On volume it works -- that is the one number in the water design that survives. But research §3 permits the catch basin to double as the balance tank only "if sized, accessible, ventilated and level-controlled," and gives the physical form for 2,500-3,500 L as 2.0 × 1.2 × 1.6 m deep -- compact and deep, so the working level moves little. This design spreads the same volume over 5.8 m² of open surface facing the sky and the garden. Three consequences with numbers: the working level swings 86-138 mm every time a group gets in, in full view, so the "visible basin" reads as fluctuating plumbing; 5.8 m² of open trough at 5-10 mm/day adds 29-58 L/day of evaporation on top of the pool's own 238-475 L/day and feeds every leaf and every kilo of blown sand directly into the pump suction; and the 900 mm open trench sits 1.25 m from the boundary wall with no guarding, cover or grating anywhere in the model.

**Proposed fix:** Split the function. Keep a shallow visible spill trough 250 mm deep × 600 mm wide at the crest, grated flush with the deck, and let it gravity-feed a concealed balance tank of 2.0 × 1.2 × 1.6 m (3,840 L gross, ~2,700 L usable) buried under the west deck at x 7000-9000, invert -1500, with an access hatch, a 100 mm vent, level probes and the autofill solenoid on the tank rather than the pool. The visible trough then holds a constant level because the surge is taken out of sight.

### 65. The scheme asks one body of water to be both an Alhambra mirror and a waterwall

**Severity:** MAJOR

**Numbers:** Crest 5.0 m at research flow rates: thin sheet 40-60 L/min/m = 200-300 L/min = 12-18 m³/h; heavy curtain 90-150 L/min/m = 450-750 L/min = 27-45 m³/h. Pool volume 47.5 m² × 1.4 m = 66.5 m³, so the entire body passes over the edge every 5.5 h (thin) to 1.5 h (heavy), continuously.

**Evidence:** The docstring's third design finding (lines 28-32) makes the Court of the Myrtles the parti and carries the axis on water; research §2 sets the rules for that kind of water -- "darkness and stillness make the mirror," "submerged low-velocity inlets, no visible jets, no audible splash." The same pool is then asked to run a waterwall over a 5.0 m crest. At 12-45 m³/h of continuous surface draw the water is in permanent motion toward the crest and the reflection is broken. The research itself flags the fork: §1 offers (a) perimeter/knife-edge overflow, "mirror-flat... the correct answer for a flat walled site. This is the Lautner detail," or (b) the raised waterwall. The design claims (b) in prose and, by leaving all four rims flush at +700 with no slot or gutter, has accidentally drawn a bad version of (a).

**Proposed fix:** Commit to (a) and match the parti. Keep the 700 mm raise for privacy, the boundary-wall clearance and the concealed gutter, but detail a true perimeter overflow: 19-25 mm slot on all four sides, 75 × 75 mm minimum gutter falling 1:48, 75-100 mm drop pipes at 1.5 m centres with 38 mm vents, bond beam 500-610 mm wide extending 600 mm down, 9.5 mm granite edge tile with a bevelled leading arris laid falling away. Flow drops to what a level-trim pump needs rather than 27-45 m³/h, the surface goes still, and the mirror the Alhambra premise depends on actually appears.

### 66. Only 7.3 m of swimmable water -- by the research's own definition a plunge pool

**Severity:** MAJOR

**Numbers:** Pool water 9.5 m long. Baja shelf occupies y 10300-12500 = 2.2 m, at full 5.0 m width, top at +400 (300 mm submerged). Full-depth water = 7.3 m. Research: "Lap swim ≥12 m; below 8 m is a plunge pool"; shelf should be 2.5-4.0 m along one end, so 5.0 m is 25-100% over-wide. Docstring line 32 claims "12.0 x 4.0 m."

**Evidence:** Line 197-198 builds the shelf across the pool's entire width rather than along part of one end. Combined with the 9.5 m water length set at line 94, the swimmable run is 7.3 m -- 0.7 m short of the plunge-pool threshold and 4.7 m short of the lap minimum. The docstring's own statement that the axis terminates "in the swimming pool proper at 12.0 x 4.0 m" is contradicted by the constants that build the model; the printed output says 5.0 × 9.5. Research §3's dimensional target for this plot size was 10-14 m × 3.5-4.5 m. The design has it 2.5 m too short and 0.5-1.5 m too wide, which is also why the aspect ratio is 1.9:1 against the Court of the Myrtles' 4.8:1 that the docstring cites as the generator. Separately, the shelf edge at y 10300 is a 1.1 m vertical drop from +400 to the floor at -700 in the middle of a 1.4 m constant-depth pool, with no steps, no transition and no handhold modelled anywhere -- research requires a break of slope at the deep end and steps at 300 rise / 300 going with the top step at deck level.

**Proposed fix:** Narrow the shelf to 3.0 m of the 5.0 m width (x 9500-12500) and set POOL_Y0 to 2300 and POOL_Y1 to 11800 per the isolation-joint fix, giving 9.5 m of water with 6.5 m full-depth. Better, take the research target directly: with the north wall pulled clear of the house and the shelf on one end only, x 9000-13500 (4.5 m) by y 2300-12200 (9.9 m) is the most a 24 m plot allows once the 3.0 m cantilever and the house line are fixed -- so state honestly in the docstring that this is a 9.9 m swim pool, not a 12 m lap pool, rather than claiming a dimension the code does not build. Add steps at the shelf face, 300/300, three risers.

### 67. 45° load spread: clears the boundary wall with 1.78 m to spare, but sits exactly on the limit against the basement

**Severity:** MAJOR

**Numbers:** Boundary wall: pool base -1100 at y 2600; a 700 mm footing on the 2.4 m wall founded at -800 has its inner edge at y ≈ 525, so the 45° plane requires y ≥ 825 -- actual 2600, clear by 1,775 mm. Basement: pool base -1100 at north face y 12900; basement excavation -3200 at y 15000. Depth difference 2,100 mm, horizontal clearance 2,100 mm -- exactly 45.0°, zero margin.

**Evidence:** The docstring (lines 21-22) claims the 700 mm raise is what "lifts the shell clear of the 45-degree load-spread zone of the boundary-wall footing." It is not: with the pool at grade (floor -1400, base -1800) the 45° plane would require y ≥ 1,525, and the 2.25 m setback from the wall face still satisfies it. The raise is a good move for other reasons but the stated structural justification is post-hoc. The real 45° problem is on the other side and the design does not mention it. The basement retaining wall at y 15000 (BS_Y0, line 102) is founded at BASE_FL-400 = -3200, 2,100 mm below the pool base and 2,100 mm away in plan. Any basement toe or raft projection -- typically 300-500 mm, reaching y 14500-14700 -- puts the deeper excavation inside the pool's load-spread zone by 300-500 mm. Worse, the 2.1 m strip of ground between the two excavations is what carries the living-volume south wall at y 12500: two storeys plus the 3.0 m cantilever's back-span reaction, undermined to -1100 on one side and -3200 on the other.

**Proposed fix:** Design the basement's south retaining wall and the pool's north wall as a single propped structural line, or increase the gap. Pulling POOL_Y1 to 11800 (per the isolation fix) moves the shell face to 12200 and gives 2,800 mm against a 2,100 mm requirement -- 700 mm of margin, enough to absorb a 500 mm toe. Alternatively found the pool base at -900 rather than -1100 by reducing the shell base slab from 400 to 250 mm (research: shell RC 250-300 mm) and take the required clearance down to 1,900 mm. State the construction sequence: basement and its retaining wall first, pool second.

### 68. Arrival is 4.0 m off the axis, up a 900 mm plinth with no steps, against a blank 10.3 m wall

**Severity:** MAJOR

**Numbers:** Gate centre x=16000 vs axis x=12000, off by 4.0 m. Door sill +900 over ground +0, steps modelled: none. North facade 18.0 x 10.3 m, 3 openings, all below 3.3 m.

**Evidence:** The pedestrian gate (line 211) is blk(15400, ..., 16600, ...) -- centred at x=16000, while AXIS=12000. A guest enters 4.0 m off the axis, so the rill runs past them sideways instead of toward them and the front door is oblique. The guest door void (line 179) is cut from GF to GF+2400, i.e. z=900 to 3300, but the forecourt is at z=0 and no step, ramp or plinth edge is modelled anywhere -- the door floats 900 mm above the ground it opens onto (the two garage doors have the same problem, with cars). The north elevation the guest faces is 18.0 m wide and 10.3 m to parapet with exactly three holes in it, all under 3.3 m, and nothing above: a 10.3 m cliff at 4.65 m from a 2.4 m boundary wall, H/W 2.2.

**Proposed fix:** Move the pedestrian gate onto the axis and widen it to read as a portal: blk(AXIS-900, PLOT_D-BW-200, STREET, AXIS+900, PLOT_D+200, 2700). Model the external steps the research specifies (rise 120-140, going 300-400, 2R+G 600-650) -- 7 risers at 128 across the full 3.0 m axis width, so the ascent is part of the axis rather than a detail. Then compress: the first threshold is the gate at 2.7 m, the release is the forecourt with the rill, the second compression is the entry soffit. That is the 'do it twice' sequence the research asks for and it is currently done zero times.

### 69. The scheme has six gestures and the stated idea is the only one not built; the light slots are a second, stronger parti that puts the axis in the solid

**Severity:** MAJOR

**Numbers:** 6 organizing gestures; 1 supports the axis; 1 actively contradicts it; the headline idea is unbuilt. Alternative parti: 2 x 6.75 x 14.5 x 2 storeys = 391 + 30 = 421 m2 vs brief 418; axis 24.0 m; water 60 m2 = 8.6% of plot.

**Evidence:** Built and legible: (1) tripartite mass split by two 1.0 m full-height slots (lines 163-166); (2) F.LOT semi-basement + sunken court; (3) raised half-level + 3.0 m cantilever over the pool; (4) roof pavilion; (5) west brise-soleil; (6) the water axis -- claimed, not built. The slots are the problem. They divide the house into three N-S bars and read powerfully in every plan, elevation and both aerials -- that is Vienna Way's thirds. But they place the axis in the centre of the *solid* bar while the two *voids* sit 3.0 m either side of it. The one move that supports the axis is the cantilever. So the drawings argue for thirds while the docstring argues for an axis, and an experienced reader will believe the drawings.

**Proposed fix:** Pick one, and make it the same one. The research's own finding 3 points to a parti where the axis IS the void, and it fits this plot almost exactly: two bars x 3000-9750 and x 14250-21000 (6.75 m wide), y 9500-24000 (14.5 m deep), two storeys = 391 m2 + 30 m2 roof = 421 m2 against the 418 brief. Between them an axial void x 9750-14250 (4.5 m) running y 3000-27000 = 24.0 m -- inside the research's 20-24 m x 4.5-5.0 m target. Pool 4.5 x 12.0 = 54 m2 at y 3000-15000 (so it runs 5.5 m into the embrace of the two bars), rill 0.5 x 12.0 from y 15000 to the gate at 27000, both at +700. One first-floor glazed bridge at y 18000-21000 crosses the axis once, which dramatises it. Delete both light slots, delete the roof pavilion or fold it into the east bar, and the villa has one idea, stated four times: gate, water, bars, bridge.

### 70. The sunken courtyard is punched through the axis -- a 3.7 m hole in the walking line and 13 m2 out of a 33 m2 living room

**Severity:** MAJOR

**Numbers:** Court 5.0 x 4.0 m centred on the axis; removes 13.0 of 33.0 m2 of living-room floor (leaving 20.0 m2 under a 7.8 m shaft) and 7.0 m2 of hall; drop in the axis 3.7 m; bridges modelled: 0.

**Evidence:** CT_X0-CT_X1 = 9500-14500 is centred on AXIS=12000, and CT_Y0-CT_Y1 = 15400-19400 straddles the hall/living-volume wall. The cut (line 127) runs from BASE_FL up to GF+200, so it removes 13.0 m2 from the 33.0 m2 living-volume floor and 7.0 m2 from the entrance-hall floor, leaving a 3.7 m drop directly in the path of the axis, with no upstand, guarding or bridge modelled. The 800 mm hall/living wall bridges over the void, so the GF plan will show a wall crossing a hole. The one move that makes the basement habitable and the one move that is supposed to organise the house are competing for the same 5.0 x 4.0 m of ground.

**Proposed fix:** Either move the court off the axis -- x 15600-20600 under the east half of the north bar, where it lights staff and plant and leaves the axis clear -- or keep it on axis and commit to it as the drama: model the axis crossing it on a 1.5 m bridge with the rill running in the bridge and falling into the court as a waterfall lighting the basement. The second is better architecture and is exactly Fish House's move (the pool is the basement's light source), but it must be modelled as a bridge, not left as a hole.

### 71. The pool is 9.5 x 5.0 at 1.9:1 -- not the 12.0 x 4.0 the docstring claims, and not the Alhambra proportion the whole argument rests on

**Severity:** MAJOR

**Numbers:** Built 9.5 x 5.0 = 47.5 m2, 1.9:1. Docstring 12.0 x 4.0 (3.0:1). Research 12.0 x 4.0 / 20-24 x 4.5-5.0, Alhambra 4.8:1. Lap minimum 12 m. Pool area 48 m2 vs research 45-50 m2 = on target.

**Evidence:** Lines 93-94 give POOL 9500 long x 5000 wide. The docstring, line 32, states 'the swimming pool proper at 12.0 x 4.0 m'. The research target is 12.0 x 4.0 (line 187) and the Alhambra ratio is 4.8:1 (line 36), with a note that the earlier 12 x 3.5 running the short way was already 'weaker'. What is built is 1.9:1 -- a fat rectangle that reads as a plunge court, not an axial water body -- and at 9.5 m it is below the research's own 12 m lap minimum. An architect will scale this off the plan in ten seconds and find both the docstring and the Alhambra rationale contradicted by the drawing.

**Proposed fix:** Either correct the docstring to what is built and drop the Alhambra claim, or build the claim. It does not fit the current massing -- 12 m of pool plus 11.5 m of house is 23.5 m against 21 m of buildable depth -- which is itself the argument for the two-bar parti above, where a 12.0 x 4.5 m pool sits in the axial void and runs 5.5 m between the bars. Separately, the printed line 'pool 6.8% of plot; research target ~10%' misreads the research: the 10% is of the ~490 m2 of OPEN ground, and the research's stated figure is 45-50 m2. At 48 m2 the pool hits the target exactly -- the script advertises a failure it did not commit.

### 72. The double-height volume is a 5.2 x 4.7 m shaft with no walls above 4.5 m, open on three sides to the weather

**Severity:** MAJOR

**Numbers:** Interior 5.2 x 4.7 m, clear 7.8 m, H/W 1.5. Walls stop at 4.5 m; next solid is the roof soffit at 8.7 m -- 4.2 m of the shaft is unenclosed on three sides. Floor after the court: 20.0 m2. Research: >=5 x 5 m, 6.0-7.0 m clear, 60/40 split.

**Evidence:** The living volume's walls are built GF to GF+GF_CH only (line 135) and line 151 then voids the whole 6.0 x 5.5 footprint from 4500 to FF. Above 4500 nothing is added at x 9000-15000, y 12900-18000 until the roof soffit at 8700. So the volume has enclosure for its lower 3.6 m and none for its upper 4.2 m: on the east and west it opens straight into the 1.0 m light slots, which are open to the sky, and on the south into the cantilever loggia, whose own south end (line 149, void reaching y=9500, the outer face) has no wall either. Against the research: 'plan it at least as wide as it is tall in one direction; below ~5 x 5 m it reads as a shaft' -- this is 5.2 x 4.7 x 7.8 clear, H/W 1.5, and after the sunken court only 20 m2 of floor. And 'best practice ~60% single-height at 3.0-3.2 m (the sofa zone), 40% double-height at the glazed garden edge' -- here it is 100% double-height with no sofa zone at all.

**Proposed fix:** Carry the living-volume walls to RF so the volume is a room, with the south face glazed full height to the pool, and take the 40/60 split literally: keep the 3.0 m nearest the glass double-height and drop a 3.2 m soffit over the back 2.5 m under the first-floor slab. Then widen it -- at 7.8 m clear it wants 7-8 m of plan in one direction to stop being a shaft, which the two-bar parti gives free (the void is the room). If the slot-flanked massing is kept, glaze the slots at the living volume so the space is interior.

### 73. Threshold compression is arithmetic, not geometry -- and the printed clear height is 500 mm wrong

**Severity:** MAJOR

**Numbers:** Printed DH clear 7.30 m; built 7.80 m. Printed compression 1:3.0; experienced 2.4 -> 3.6 = 1:1.5, then a wall. FF declared 3.2 m, built 3.7 m. Parapet 10.3 m, pavilion 12.2 m vs research benchmark 8.6 m; front setback 4.65 m to the boundary wall gives H/W 2.2.

**Evidence:** The docstring claims 'threshold compression at a 2.4 m soffit releasing into the tall volume, past the 1:2.2 ratio', and the script prints 'compression ratio 1:3.0'. But the compression is a 400 mm wall thickness, not a zone (research wants 1.5-2.0 m wide and low, with dwell), and the release never happens because there is no opening between the hall and the tall volume: the sequence is 2.4 m door, 3.6 m hall, dead end. The printed ratio divides two numbers that are never experienced in sequence. The number itself is also wrong: (RF-SLAB-GF)/1000 = 7.30 m, but SLAB is added above RF, so the clear height from GF floor to roof soffit is 7.80 m. The same slip inflates the first floor -- FF_CH=3200 is declared but the void is cut FF to RF = 3700 clear -- and pushes the parapet to 10.3 m and the pavilion to 12.2 m against the research's 8.6 m benchmark for G+1+roof.

**Proposed fix:** Build the sequence before printing a ratio for it: a 2.4 m soffit held for 1.8-2.0 m of depth (a loggia inside the wall thickness, not the wall thickness itself), then the opening into the volume. Fix the height arithmetic -- either set RF = FF + FF_CH so FF_CH means what it says and the parapet lands near 9.5 m, or rename the constants. And print the ratio only from a measured soffit-to-soffit path, or not at all.

### 74. The overflow spills off the short end, away from the house, into a 1.0 m basin 1.25 m from the boundary wall

**Severity:** MAJOR

**Numbers:** Spill face 5.0 m (short end) vs 9.5 m (long side). Basin 1.0 m wide, 1.25 m clear to a 2.4 m wall. Spill face height 700 mm, viewed end-on from 12-20 m.

**Evidence:** The docstring (line 20) says the pool 'overflows one long side as a waterwall into a visible basin'. Lines 195-196 cut the spill and basin at POOL_Y0 - 1400 to POOL_Y0 - 400, i.e. across the 5.0 m SOUTH SHORT END, at the far end of the pool from the house, with the 2.4 m stone boundary wall 1.25 m beyond the basin. So the single dramatic water event in the scheme is 5.0 m wide instead of 9.5 m, faces the back wall, and is seen from the living room only end-on at 12-20 m as a 700 mm sliver. This is the failure mode the research spent its first finding warning about, reintroduced at the far edge.

**Proposed fix:** Move the spill to a long side as the docstring says -- the west face, x=POOL_X0, y 3000-12500 -- so it is seen broadside from the entry axis and from the east terrace, 9.5 m of sheet instead of 5.0 m. Or better, given the axis: spill the NORTH head of the pool back toward the house is wrong, so spill west and let the basin double as the balance tank the research recommends (one chamber, 2.0 x 1.2 x 1.6 m deep, invert 1.0-1.5 m below pool water line, autofill on the tank not the pool). Also model the 45-degree check the research demands: the basin invert at -900 and the boundary footing 1.25 m away is exactly the condition it flags.

### 75. The printed 7.30 m clear height is wrong: the volume is 7.80 m, because the slab is counted twice

**Severity:** MAJOR

**Numbers:** Modelled clear height 7.80 m, printed 7.30 m (error 500 mm). Compression ratio is 7800/2400 = 1:3.25, not the printed 1:3.0. Parapet top 10.30 m above street, pavilion top 12.20 m. Research benchmark: parapet approx. 8.6 m before the roof enclosure -- 9.5 m allowing the 900 mm raise. The model is 0.8 m over that, or 0.3 m over once the phantom slab is deleted.

**Evidence:** Line 74 sets RF = FF + FF_CH + SLAB = 8700, i.e. RF already includes a 500 mm slab allowance above the 3200 mm first-floor ceiling. Line 154 then builds the physical roof slab from RF to RF+SLAB (8700 to 9200) on top of that. The first-floor rooms are voided FF to RF, so the ceiling soffit is at 8700 and the double-height volume runs from GF 900 to 8700. The print statement at line 238 computes (RF - SLAB - GF) = 7300, subtracting a slab that sits above the number it is measuring. Every section figure quoted to the client is therefore 500 mm out, and the building carries 500 mm of dead height it does not use.

**Proposed fix:** Set RF = FF + FF_CH (8200) and keep the physical roof slab at 8200-8700. Parapet top drops to 9.80 m, clear void to 7.30 m -- which is what the print claims -- and the whole building loses 500 mm of height against the G+1+roof envelope. Then correct line 238 to (RF - GF).

### 76. The double-height volume fails both proportion tests: taller than it is wide, and 100% void

**Severity:** MAJOR

**Numbers:** Void 6.0 x 5.5 x 7.80 h. Height/width 1.30, height/depth 1.42; both should be <=1.0. Single-height share 7% vs the researched 60%. To satisfy the 60/40 rule at 33 m2: 19.8 m2 at 3.0-3.2 m, 13.2 m2 double-height. Research target for a two-storey void: 6.0-7.0 m clear -- the model is 0.8-1.8 m over.

**Evidence:** The living volume is 6.0 x 5.5 m in plan (LV_X0/X1 9000-15000, WG_Y0/Y1 12500-18000) and 7.80 m clear. VILLA_RESEARCH.md s.2: 'Plan it at least as wide as it is tall in one direction.' 6.0 < 7.80 in x and 5.5 < 7.80 in y -- it fails in both. It clears the 'below ~5 x 5 m reads as a shaft' threshold on gross plan only, and once the courtyard hole is subtracted the usable floor is 5.2 x 2.5 m and it fails that too. Separately, line 151 voids the ENTIRE LV footprint between GF+GF_CH and FF, so the split is 100% double-height / 0% single-height. The research's best-practice is ~60% single-height at 3.0-3.2 m (the sofa zone) with 40% double-height at the glazed edge; the only slab over the living room is the 400 mm back edge of the cantilever at y 12500-12900, i.e. 2.4 m2 of 33 m2 = 7%. A room with no low ceiling anywhere has no sofa zone and no measure against which the tall part reads as tall.

**Proposed fix:** Two moves together. (1) Widen: absorb the two 1.0 m slots so LV runs x 8000-16000 (8.0 m) -- 8.0 > 7.3 m clear once the phantom slab is deleted, and the volume stops reading as a chimney. (2) Re-slab the north 3.0 m of the LV at first floor (void only y 12500-15500, 40% of the depth, at the glazed edge exactly as researched). That restores a 3.2 m sofa zone AND returns ~24 m2 to the first floor, which covers the GFA shortfall in one stroke.

### 77. A 7.80 m tall volume lit only at its base, under a soffit that sits 200 mm above the glazing head

**Severity:** MAJOR

**Numbers:** Glazing 5.6 m wide x 3.3 m tall, head 3.40 m above GF. Overhang 3.0 m = 0.91 x opening height; research allows 0.6-0.8 x at 25N+ = 2.0-2.6 m for a 3.3 m opening, so it is 0.4-1.0 m over. Sky angle at head 3.8 deg, at sill 49.4 deg. 2.5 x head-height reach for a clerestory that does not exist: 8.5 m -- enough to wash the whole 4.7 m depth.

**Evidence:** The only aperture into the double-height volume is the ground-floor glazing at z 1000-4300 (line 169-170). Above it, the first-floor cantilever throws a 3.0 m soffit at z 4500 -- 200 mm above the window head. There is no clerestory on the double-height wall and no rooflight over the volume (line 154 roof slab is unbroken there). From the head of the glazing, the sky is visible only up to 3.8 degrees over the soffit edge; from the sill, up to 49.4 degrees. So the upper 4.5 m of the 7.80 m volume -- the part that makes it double-height at all -- receives no direct sky at any point, and the room is lit almost entirely by ground-bounce off the terrace. The research's own remedy is quoted and then not used: 'a clerestory at 3 m or on a double-height wall pushes daylight 4-6 m back -- a 2.5x head-height rule.'

**Proposed fix:** Lift the cantilever soffit to 5000 and drop the glazing head to 4100 so the head sees 15+ degrees of sky, or pull the glass 600 mm forward of the soffit line. Then cut a clerestory band in the double-height wall -- 600 mm high at z 7000-7600 across the full 5.6 m -- or a linear rooflight along the south edge of the roof slab over the void. Without top light this volume is a dark well with a bright floor.

### 78. The two 1.0 m light slots are ducts, not courts, and no window faces them

**Severity:** MAJOR

**Numbers:** Slot 1.0 m wide, 6.1 m long. H/W = 9.4 from ground-floor level, 13.1 from basement floor. Research courtyard H/W approx 1.5, aspect 1:1 to 2:1, minimum useful court 4 x 4 m -- these are 6 to 9 times the researched proportion and a quarter of the minimum width. Sky angle across the slot at basement floor 4.4 deg, at ground floor 6.1 deg. Two open holes into the basement, 1.0 x 2.6 m each = 5.2 m2. Plan area surrendered: 12.2 m2 per level over four levels.

**Evidence:** Lines 163-166 cut two slots at x 8000-9000 and x 15000-16000, y 12200-18300, from z 400 up to 10300. Because there is no ground-floor block spanning x 8000-9000 (WW ends at 8000, LV starts at 9000) and the basement's interior void already runs up to z 400, the slots are continuous with the basement: an open shaft from -2800 to +10300. Not one opening in the entire model faces them -- the LV's east and west walls (x 9000-9400, 14600-15000) and the wings' facing walls are solid at every level. So the slots give up plan area on four levels, sever the first floor from the wings and cut the roof slab and parapet, and light nothing. They also leave the basement open to the weather: over x 8000-9000 and 15000-16000, y 15400-18000 there is no slab at z 400 at all, and no drainage is modelled.

**Proposed fix:** Delete both slots and give the width to the living volume (LV x 8000-16000, per the proportion fix), OR keep one and widen it to 4.0-5.0 m so it is a real patio at H/W approx 2 with glazed walls onto it at basement, ground and first -- which is what 'AGi Wall House, patios developed three-dimensionally' actually means. A 1.0 m gap between two 9.4 m walls is a service riser.

### 79. The north bar -- half the house, and the only place the 4 bedrooms fit -- has no windows

**Severity:** MAJOR

**Numbers:** North bar interior 89.4 m2 per floor. Ground: 0 m2 daylight aperture; research asks a ventilation inlet alone of >=1/10 floor area = 8.9 m2. First: 2 x 4.4 x 0.65 = 5.72 m2 of clerestory = 6.4% of floor area, both at the extreme ends. Clerestory head 3.45 m above FF, 2.5 x head-height reach 8.6 m from each end wall -- nominally meeting in the middle of a 17.2 m room, but as a 650 mm slot 8.6 m away, not as usable light. Room depth 5.2 m with no aperture on either long face.

**Evidence:** The north bar (x 3000-21000, y 18000-24000, interior 17.2 x 5.2 m) is 108 m2 gross on each of two floors: 55% of the ground floor and 60% of the first. At ground level its only cuts are the 1.5 m guest door, two 2.7 m garage doors and a 1.1 m service door -- all opaque, and all blocked by the 100 mm leaf anyway. Zero glazing. At first floor the only apertures are the two clerestory bands (lines 176-178), and both are in the END walls at x 3000 and x 20500 of a 17.2 m long plan, so the middle 15 m of the floor has no opening in any direction. The bedrooms have nowhere else to go: the wings are 5.0 x 5.5 gross = 19.7 m2 interior each, against the research's 28-35 m2 per guest suite and 55-75 m2 for a master. Four bedrooms cannot be daylit in this model.

**Proposed fix:** Open the north bar's south face onto the court and the slots (it is the wall that faces the garden side of the plan), and put a real court in the middle of the bar. Concretely: extend the sunken court up through the north bar to the sky at x 9500-14500, y 18400-21400 and glaze all four of its walls at basement, ground and first -- that is one move that fixes the basement, the axis and the bedroom daylight together. Add a 1.5-2.0 m deep recessed glazing plane on the north (street) face at first floor behind the boundary wall for the remaining rooms.

### 80. A 3.0 m roof overhang runs the whole 18 m south face, 1.0 m above the first-floor window heads

**Severity:** MAJOR

**Numbers:** Overhang 3.0 m at z 8700; window 2.25 m tall (z 5450-7700), head 1.0 m below the soffit. Sky cut-off 18.4 deg at the head, 47 deg at the sill. Research: projection 0.6-0.8 x opening height at 25N+ = 1.35-1.80 m for a 2.25 m window. Over by 1.2-1.65 m. The same slab also sits 3.0 m x 18.0 m = 54 m2 unsupported over the wing bays at y 9500-12500.

**Evidence:** Line 154 takes the roof slab out to y 9500 across the full width x 3000-21000, not just over the cantilever. The wings' first floor stops at y 12500, so the roof projects 3.0 m past the entire south facade with nothing beneath it at x 3000-8000 and 15000-21000. The wings' first-floor windows have their head at z 7700 (line 175, FF+2700); the roof soffit is at 8700, 3.0 m out. From the window head the sky is cut off above 18.4 degrees. Those rooms are the guest bedrooms, and they are being shaded by a horizontal element sized for nothing in particular -- the research's south-overhang rule would put it at 1.35-1.80 m.

**Proposed fix:** Step the roof back to y 12500 over the wings and let the 3.0 m projection happen only over the living volume (x 9000-15000), where it is doing the researched job of shading the pool edge and reads as a cantilever rather than a brim. That also removes the unsupported 54 m2 of slab and makes the cantilever legible in elevation instead of being lost in a continuous eave.

### 81. No stair, no lift, no shaft anywhere between -2.80 and +12.20 m

**Severity:** MAJOR

**Numbers:** Vertical circulation modelled: 0 m2. Research allowance: 14-18 m2 per floor plus lift 1.6 x 1.7 m internal, 1.5 m pit, 3.6 m overrun. Roof pavilion 30 m2, openings 0. Total rise basement to roof deck 12.0 m = approx 68 risers at 175.

**Evidence:** The model contains four levels -- basement -2800, ground 900, first 5000, roof pavilion 9200 -- and not one vertical circulation element. No stair, no lift shaft, no basement ramp, no roof access. The roof pavilion (lines 158-160, 6.0 x 5.0 m, walls 250 mm, 3.0 m high) has no door and no window: a sealed 30 m2 box counted in GFA. The research names the floating stair under a clerestory acting as a sundial (Interlude House) as one of the scheme's signature section moves, and allots 14-18 m2 per floor to stair plus a 1.6 x 1.7 m lift shaft. Section AA is the drawing that has to carry this scheme, and it will show four floors with nothing connecting them.

**Proposed fix:** Put the stair where the section wants it: against the west face of the double-height volume, rising through the void with a clerestory above it, so the one drawing that matters shows light, stair and volume in the same cut. Lift shaft adjacent, 1.6 x 1.7 m internal, running -2800 to the pavilion (which then has a reason to exist and needs a door). Basement ramp is not feasible on 29 m -- the research says so and points at a car lift; either way it must be modelled.

### 82. The cantilever bears on two 200 x 400 mm piers and has no back-span

**Severity:** MAJOR

**Numbers:** Cantilever 3.0 m carrying 18 m2 of first floor + 18 m2 of roof + 3.70 m of wall. Full-thickness bearing: 2 piers of 200 x 400 mm, 5.6 m apart. Research: a 3.0 m RC cantilever wants 215-375 mm effective depth carrying itself alone; span/250 appearance limit = 12 mm deflection at the tip.

**Evidence:** Lines 147-149 build a 6.0 x 3.4 m first-floor box (slab 4500-5000, walls 5000-8700) at y 9500-12900. The LV void at line 151 then cuts the slab back to y 12500, so 3.0 m of slab plus a 3.70 m tall storey plus roof cantilever off the line y 12500. The only thing under that line is the LV's south wall (y 12500-12900), and the glazing void at line 169 rebates 300 of its 400 mm across x 9200-14800 -- leaving full-thickness bearing only at x 9000-9200 and 14800-15000. Meanwhile the two 1.0 m slots cut through the first floor and roof for y 12200-18300, severing the box from the wings on both sides, and the sunken court undermines the LV's north wall (y 17600-18000) for 5.0 of its 6.0 m. So the cantilever has no back-span in either direction, and no downstand, beam or column is modelled. In section AA at x 12000 it will draw as a storey flying 3.0 m off nothing.

**Proposed fix:** Give it a back-span: run the two side walls of the box (x 9000-9400, 14600-15000) north through y 18000 into the north bar as 400 mm RC blades -- which means bridging or deleting the light slots at first-floor level and keeping the court clear of y 17600-18000. Then the box is a propped cantilever off two blades and the section is honest. Alternatively hang the tip from the roof plate and draw the hanger.

### 83. There is no service gate -- staff enter through the guest arrival court

**Severity:** MAJOR

**Numbers:** Boundary-wall openings: 2, both on the north/street boundary. East side strip clear width 21000 to 23650 = 2.65 m, currently a dead end. Distance staff must travel through the guest forecourt: ~9 m.

**Evidence:** The docstring (line 47-48) claims 'service on the east boundary reaching the dirty kitchen without crossing guest or family space'. The service DOOR is on the east face of the north bar (line 183-184, x 20700-21300, y 18700-19800), but the boundary wall (lines 206-211) has exactly two openings and both are in the NORTH wall facing the street: a 4.5 m vehicle gate at x 3800-8300 and a 1.2 m pedestrian gate at x 15400-16600. There is no gate on the east boundary. Staff must therefore come through the same front gate as guests, cross the arrival court where the rill and the guest approach are, then walk 3 m down the east side strip to the service door. The service route crosses the guest route at the one point the Gulf discipline exists to prevent.

**Proposed fix:** Cut a 1.0-1.2 m service gate in the east boundary wall at about y 19000, aligned with the existing service door, and screen the east strip from the forecourt with a return wall at y 24000.

### 84. The researched service corridor to the majlis does not fit -- the north bar is 300 mm too shallow

**Severity:** MAJOR

**Numbers:** Available bar depth 5.2 m; kitchen + service corridor + walls = 5.5 m. Short by 300 mm before the majlis is drawn. Frontage test at 5.2 m depth: garage 6.40 + hall 3.46 + guest WC 0.67 + stair 2.69 + lift 0.67 + show kitchen 3.85 + dirty kitchen 2.31 + pantry 0.77 + majlis 4.81 = 25.63 m required against 17.20 m available -- over by 8.43 m of frontage = 43.8 m2.

**Evidence:** VILLA_RESEARCH.md section 5: 'The service route must reach the majlis for coffee without crossing family living -- on a small plot that means a short service corridor behind the show kitchen with a discreet door into the majlis.' That section needs show kitchen depth 3.5 + service corridor 1.2 + two internal walls 0.2 = 4.9 m plus the external wall face, i.e. 5.5 m clear minimum. The north bar (NB_Y0/NB_Y1, line 84) gives 6.0 m gross = 5.2 m clear. There is no depth left over for the majlis itself at that x, so the kitchen and the majlis compete for the same frontage, and the only route from the dirty kitchen (which must sit by the service door at the east end) to the majlis is the single 1.2 m spine corridor that is also the guest route from the front door and the family route from the garage. All three separated routes collapse into one.

**Proposed fix:** Take the north bar to 9.0 m deep (NB_Y0 = 15000): kitchen zone 3.5 + service corridor 1.4 + majlis 3.6 stacked front-to-back gives the discreet coffee door without the corridor ever entering guest or family space. That costs 3.0 m off the wings/garden band, which the pool re-planning below has to absorb.

### 85. There is no separate family entrance

**Severity:** MAJOR

**Numbers:** Garage internal x 3400-9800; entrance hall on axis x ~10000-13500; stair centred x 12000. Family route passes through the guest hall every day.

**Evidence:** The docstring (line 47) claims 'family via the garage'. The garage doors are at x 3800-9600 on the north face (lines 181-182), at the WEST end of the bar; the guest entrance is at x 11250-12750 on the axis (lines 179-180), in the CENTRE; the stair is pinned to the centre by the roof pavilion. So the family arriving by car must walk east along the single spine corridor and through the guest entrance hall to reach either the stair or the living volume -- and to reach the living volume they must additionally cross the sunken-court hole. A family entrance that discharges into the guest foyer is not a family entrance.

**Proposed fix:** Put the family door on the west face of the garage into a boot room / secondary lobby against the west light slot, with its own door into the family living, and move the main stair off the entry axis so the guest hall is not the hub.

### 86. The two-car garage does not work: 300 mm too shallow, the second bay is blocked by the boundary wall, and the 900 mm apron ramp is 1:5.2

**Severity:** MAJOR

**Numbers:** Depth 5.2 m vs 5.5 m min (300 mm short) / 6.5 m comfortable (1.3 m short). Bay 2 obstructed 1300 mm of 2700 mm. Apron gradient 900/4650 = 1:5.2, against research 1:6 max and 1:8 comfortable, with zero room for the 2.0-2.5 m half-gradient transitions at each end. Research standing space between gate line and street 5.5-6.0 m: provided 0 m -- a car waiting for the gate stands in the street, on the ramp.

**Evidence:** Three separate failures on the same element. (1) Depth: the garage sits in the north bar with 5.2 m clear (line 84), against the research's 'Garage 2 cars: min 5.5 x 5.5' and 'comfortable 6.0 x 6.5'. A 5.0 m SUV leaves 100 mm at each end, and the researched 600 mm clearance to walls is impossible. (2) Alignment: the garage doors are at x 3800-6500 and 6900-9600 (line 181-182) but the vehicle gate in the boundary wall is only x 3800-8300 (line 210), so 1.3 m of the second bay's 2.7 m door is behind solid stone -- a car physically cannot enter bay 2. (3) Level: GF = +900 (line 70) and the front setback is 5.0 m, so from the boundary wall's inner face to the garage door is 4.65 m clear carrying a 900 mm rise. No ramp is modelled anywhere.

**Proposed fix:** Widen the vehicle gate to x 3600-9800 so both doors are clear of stone, deepen the bar to 9.0 m so the garage gets 6.5 m depth plus a boot room, and drop the garage floor to street level +0 with the 900 mm step taken internally at the boot-room door rather than on the apron.

### 87. The basement is under-used by 58 m2 while the ground floor is 48 m2 short -- and the one move that fixes it cannot be built

**Severity:** MAJOR

**Numbers:** Basement net 121 m2, programmed 63 m2, spare 58 m2. Ramp required 21.3 m, available 4.65 m. Ground-floor deficit 47.6 m2. A car lift (research pit ~3.0 x 6.0 m) is the only geometry that fits.

**Evidence:** Basement 18.0 x 9.0 gross (lines 101-102), net 17.2 x 8.2 = 141.0 less the 20 m2 court = 121 m2 net. The research's own workable semi-basement schedule less the garage is maid's room + bath 15 + laundry 10 + store 8 + plant 16 + pool plant 14 = 63 m2. So 58 m2 of serviced, lit, excavated floor sits empty directly beneath a ground floor that is 48 m2 short. The reason is that the research put the garage (46 m2) down there and this scheme did not -- and cannot: the basement floor is at -2800 (line 77), so a ramp at the research's 1:6 maximum needs 16.8 m of run plus two 2.25 m transitions = 21.3 m, against 4.65 m of forecourt. Also note there is no stair or lift shaft modelled from the basement, and with the only core in the centre of the north bar the staff surface in the guest entrance hall; and the plant room ends up directly under the majlis, against the research's 'never share a wall with a bedroom or the majlis'.

**Proposed fix:** Either take the car lift (3.0 x 6.0 m pit, garage in the basement, 46 m2 off the ground floor -- which closes the ground-floor deficit almost exactly), or extend the basement south to y 12000 under the wings and move the majlis's service suite, dining store and a service stair down there. Add a dedicated service stair at the east end so staff never surface in the hall.

### 88. The entry axis is blocked by its own rill, and the guest gate is 4 m off it

**Severity:** MAJOR

**Numbers:** Rill length 3.9 m (the docstring calls it the long axis of a 29 m plot). Clear gap at rill south end 400 mm, north end 350 mm. Guest gate offset from axis 4.0 m. Pool is on the opposite side of a 12 m deep house from the rill -- the two water bodies never see each other; total water on the 'axis' 13.4 m in two disconnected pieces.

**Evidence:** The rill runs x 11750-12250, y 24400-28300 (lines 199-202), dead on AXIS. The front door is at y 24000-23700 on the same axis. So the rill occupies the entire 3.9 m approach and stops 400 mm from the door face -- there is no landing, no doorstep, and no way to stand square to a 1.5 m pivot door. It also divides the forecourt into two halves with only a 400 mm gap at its south end (to the house face) and a 350 mm gap at its north end (to the boundary wall). Meanwhile the pedestrian gate is at x 15400-16600 (line 211), centred 4.0 m east of the axis, and the boundary wall is solid where the axis crosses it -- so the Casa Merida move the docstring claims (line 30-31, 'an uninterrupted perspective from the entrance door to the pool') actually terminates on a blank stone wall 4.65 m from the door, and a guest arriving on foot has to step over the water channel to reach the door.

**Proposed fix:** Put the pedestrian gate on the axis at x 11400-12600, stop the rill 2.4 m short of the door to give a proper landing (or bridge it with a single 1.5 m stone slab flush with the paving), and accept that on this plot the long axis has to run THROUGH the house -- carry the water under the glazed threshold into the living volume and out to the pool, which is the only way the 20-24 m Alhambra proportion can exist here.

### 89. The pool has zero deck on the house side -- the living-room glass wall opens onto a 900 mm drop into the water

**Severity:** MAJOR

**Numbers:** House-side deck 0.00 m vs 3.5-4.5 m researched for the lounging side. Side decks 9.15 m each (over-provided). Rear walkway behind the catch basin 1.25 m, just over the 1.2 m minimum. Cantilever oversails 3.0 m of the 9.5 m pool = 32%, which does match the Interlude precedent.

**Evidence:** POOL_Y1 = 12500 (line 94) is identical to WG_Y0 = 12500 (line 85), the building line. So the pool's north coping IS the south face of the house. The ground floor is at +900 and the pool water at +700 (POOL_TW, line 95), so the 5.6 m wide structural glazing (line 169-170) opens onto a 200 mm step down to a coping that is itself the pool edge. There is no terrace, no threshold, no guard, and no way to walk round the pool on the principal side. Research: 'Pool surround: 1.2 m min on back sides, 1.5 m where people walk, 3.5-4.5 m on the lounging side. A 600 mm coping walk is a developer's pool.'

**Proposed fix:** Pull the pool south to y 3000-11000 (8.0 m) or re-proportion it to the research's own target of 12.0 x 4.0 running east-west, and give the house side a 3.5 m terrace at +900 stepping down to the water. The 900 mm level change is the seat-height pool edge the research asks for -- use it, don't fall off it.

### 90. The double-height volume is a shaft by the research's own rule, and it is 100% double-height

**Severity:** MAJOR

**Numbers:** 7.30 m tall vs 5.2 m widest clear dimension: H/W 1.40 (needs <=1.00). Research double-height band 6.0-7.0 m clear -- 7.30 exceeds it. Usable floor 13.4 m2 against the 'below 5 x 5 = 25 m2 reads as a shaft' threshold. Compression zone length 400 mm against the researched 1.5-2.0 m.

**Evidence:** The script prints 7.30 m clear (line 238). The clear plan is 5.2 x 4.7 m, cut to a 5.2 x 2.5 m usable strip by the sunken court. VILLA_RESEARCH.md section 2: 'Plan it at least as wide as it is tall in one direction; below ~5 x 5 m it reads as a shaft', and 'Best practice: ~60% of the living room single-height at 3.0-3.2 m (the sofa zone), 40% double-height at the glazed garden edge.' This volume is taller than it is wide in both directions and is double-height over its whole area, so there is no sofa zone. Separately, as modelled it is not enclosed: above z 4500 there is no solid at x 9000-15000, y 12500-18000 on the east, west or south sides -- it is open to both light slots and to the cantilever void, roofed but weatherless. The compression/release the docstring claims (line 43-44) is also not adjacent: the 2.4 m soffit is only the 400 mm door thickness, then a 3.6 m hall, then 6.0 m of north bar, then the courtyard hole, before you reach the tall volume.

**Proposed fix:** Widen the living volume to 7.5-8.0 m clear in one direction (absorbing the light slots), keep the double-height to the 3.5-4.0 m glazed strip at the pool edge and drop the rest to a 3.2 m ceiling with the master above it, and make the compression a real 2.0 m long, 2.4 m soffit loggia between the gate and the hall.

### 91. The 1.0 m light slots are 10:1 ducts that buy no daylight and cost the plan its continuity

**Severity:** MAJOR

**Numbers:** Slot H/W 10.3 vs researched 1.1-1.6. Footprint cost 2 x 1.0 x 5.5 = 11 m2 plus four extra external wall faces. North-bar wall left at those two points: 100 mm of 400 mm.

**Evidence:** Lines 163-166 cut two 1.0 m wide voids full height from GF-SLAB to the top of the parapet, between each wing and the living volume. They cite the AGi Wall House 'patios developed three-dimensionally' (line 42-43), but the research's own courtyard guidance is 'a 5-7 m wide court gives H/W 1.1-1.6' and 'hot-dry height/width ~1.5'. At 1.0 m wide and 10.3 m to the parapet the H/W is 10.3 -- a duct, not a patio; a shaft that narrow and that deep delivers effectively no sky component at ground level. What it does deliver is fragmentation: the ground floor becomes three detached fingers whose only link is the north bar, which is why every guest, family and service route is forced through the same 5.2 m deep strip. The slots also overrun the north bar by 300 mm (void y extends to 18300 against a wall at 18000-18400), leaving a 100 mm sliver of its south wall at two points.

**Proposed fix:** Delete both slots. Put the daylight where it earns its keep -- one 5.0 x 5.0 m court between the north bar and the south band, and clerestories on the blank east and west boundary walls, which the research says will push light 4-6 m in.

### 92. Garage clear depth is 5.20 m -- a Land Cruiser leaves 105 mm at each end and a Range Rover LWB does not fit

**Severity:** MAJOR

**Evidence:** The north bar is NB_Y0 18000 to NB_Y1 24000 = 6.00 m, less WALL 400 each side = 5,200 mm clear, and there is no way to make it deeper without moving the bar. Research: 'Garage 2 cars: min 5.5 x 5.5 (30 m2); comfortable 6.0 x 6.5 (39 m2); luxury 6.5-7.0 wide x 7.0 deep.' LC300 4,985 mm leaves 215 mm total -- you cannot open a tailgate, walk in front of the bonnet, or fit a bike/bin/store. Range Rover LWB 5,252 and Escalade ESV 5,766 will not close the door. Widths are fine: bay centres 3,100 mm apart give 1,120 mm between 1,980 mm bodies (research wants 900), and 760 mm from the west car flank to the interior wall at x=3400 (research wants 600). Clear door height is 2,400 mm -- the bare research minimum, with no allowance for the 2.7 m the research asks for if a car lift is ever added.

**Proposed fix:** Take the bar to 6.80 m deep (6.00 clear) as part of the southward shift, and raise the door head to 2.7 m clear.

### 93. The 900 mm level change is not resolved anywhere -- the driveway would be 1:5.2 and the front door has no landing

**Severity:** MAJOR

**Evidence:** GF = 900 and STREET = 0, so the garage floor, front door threshold and service door all sit 900 mm above the forecourt. Nothing bridges them: the garage door void runs z 900-3300 with grade at 0 outside, and no ramp or step is modelled. Driveway: 900 mm over the 4,650 mm court = 19.4% = 1:5.2. Research sec.4: ramp 1:8 comfortable, 1:6 max, transitions at half gradient over 2.0-2.5 m. 1:5.2 already breaks the maximum, and the two transitions alone would consume 4.0-5.0 m -- the whole court -- leaving 0.65 m of run for 512 mm of rise. Front door: 900 mm needs 7 risers at 129 with 350 going = 2.10 m of stair plus a 1.5 m landing = 3.60 m of the 4.65 m court, but the rill occupies exactly that ground -- its surround runs x 11500-12500, y 24400-28300, i.e. the door face at y=24000 clears the rill's south end by 400 mm. An accessible 1:12 ramp would need 10.8 m. The pool is also raised 700 mm above the garden with no external steps modelled (research: rise 100-150, 2R+G = 600-650, so 5 risers at 140).

**Proposed fix:** Drop the garage and its bar to street level (z=0) -- the privacy lift is only needed under the living floors -- and take the 900 mm internally as 6 risers between garage and hall. At the entry, turn the rill into the level change: a 900 mm axial cascade in 6 x 150 steps from the threshold down to the court, with the entry stair flanking it. That converts the conflict into the parti.

### 94. The section as drawn needs 33.7 m of a 29.0 m plot -- the rear setback is over-observed by 9.5 m while the front sits at the minimum

**Severity:** MAJOR

**Numbers:** 33.70 m required vs 29.00 available; house 12.0 m deep in a 21.0 m buildable band

**Evidence:** Depth budget north to south, using the design's own dimensions and the research's minima: front wall 0.35 + garage aisle 6.00 + garage bar 6.80 (6.0 clear + 2 x 0.4) + wings/living volume 5.50 + pool terrace 4.00 + pool 9.50 + rear surround 1.20 + rear wall 0.35 = 33.70 m against 29.00 m available. Over by 4.70 m -- which is exactly why the forecourt is 4.65 instead of 6.0 and the pool terrace is 0.30 instead of 4.0. The plot is not overcrowded: the house occupies y 12500-24000 = 12.0 m of a 21.0 m buildable depth (rear setback line y=3000), so 9.0 m of slack sits behind the pool where nothing needs it, while every failure is in the 4.65 m at the front. Footprint 196 m2 / 28.2% coverage is comfortably inside the 27-32% the research predicts, so this is a distribution problem, not a density problem.

**Proposed fix:** Two moves, taken together. (1) Shift the house 2.15 m south: forecourt 6.80 m, rear band 10.0 m. (2) Turn the pool east-west at 12.0 x 4.0 = 48 m2 -- the research's exact target, and a proper 12 m lap length. Revised budget: 0.35 + 6.80 + 6.80 + 5.50 + 3.00 terrace + 4.00 pool + 2.20 south deck + 0.35 = 29.00 m, fitting the plot with the pool ends 5.65 m clear of both side walls (lounging deck goes on an end, meeting 3.5-4.5).

### 95. The overflow, weir and catch basin do not exist in the geometry -- the pool is a closed 700 mm plinth box

**Severity:** MAJOR

**Numbers:** void y 1600-2600 vs shell y 2600-12900: zero intersection; crest 60 mm low vs 2-6 mm; plant run 19-21 m vs 15 m max

**Evidence:** The shell solid spans y 2600-12900 (blk(POOL_X0-400, POOL_Y0-400, ...) with POOL_Y0=3000). The 'spill + basin' void spans y 1600-2600 (blk(POOL_X0-400, POOL_Y0-1400, ...)). The two ranges are adjacent, not overlapping -- they meet at y=2600 and share zero volume, so the subtraction removes nothing. There is no weir, no lip, no basin, no waterwall. The docstring's founding move ('the pool is RAISED 700 mm above the garden and overflows one long side as a waterwall into a visible basin') is absent from the model. Two further inconsistencies in the same block: the void is 5.8 m wide in x, so even if it cut, it would spill off the 5.0 m SHORT end, not the long side the docstring claims; and its top at POOL_TW-60 = 640 puts the crest 60 mm below water level against the research's 2-6 mm ('a 25 mm error destroys the effect'). In landscape terms the garden currently reads a blank 700 mm render plinth on the pool's south face. Servicing also does not close: if the basin were built at y~2100, the pipe run to the basement plant room (basement starts y=15000) is ~12.9 m horizontal + 1.9 m vertical + 4-6 m inside the basement = 19-21 m against the research's 15 m limit.

**Proposed fix:** Make the void overlap the shell -- extend it north to at least y=3000 so it cuts the south wall -- and set its top at POOL_TW-4. With the pool turned east-west, spill off the long south side into a basin along the deck edge and put the balance chamber directly under the south deck, which also brings the pipe run inside 15 m.

### 96. The garden is 142 m2 of planting in two disconnected halves, and no door from the house reaches it

**Severity:** MAJOR

**Numbers:** 463.4 m2 open (66.6%); rear 225.7 in pieces of 106.3 / 106.3 / 13.1; ~142 m2 planted in two halves

**Evidence:** Open ground inside the walls = 23.3 x 28.3 = 659.4 m2, less 196.0 footprint = 463.4 m2 (66.6% of the plot). It breaks down as: front court 108.4 (of which the rill takes 3.9), side strips 61.0, light slots 11.0, rear 283.1 less 57.4 of pool shell = 225.7. Against the research's allocation for ~490 m2 open (pool+deck 100-120, arrival+drive 90-110, garden 150-200, side strips 60-80) every area lands -- the failure is dimensional and topological, not areal. The rear 225.7 is three pieces: west 8.75 x 12.15 = 106.3, east 8.75 x 12.15 = 106.3, and a 5.8 x 2.25 = 13.1 strip behind the pool. Subtract a 4.0 m lounging deck west (48.6) and a 1.8 m walk east (21.9) and the dead strip, and planted garden is ~142 m2 in two pieces of 57.7 and 84.4 -- a ring around a pool block, pinched to 300 mm at the house end. Getting from the west garden to the east means walking round the south. Getting there from inside means leaving by the front door and walking a 2.65 m side alley (1.95 m on the west past the fins) -- both of which pass the 1.5-1.8 m circulation minimum, but neither is a garden route. Nothing is designated: no terrace, no deck, no path, no tree position, no planting bed appears anywhere in the model.

**Proposed fix:** With the pool turned east-west the rear becomes one 23.3 x 10.0 m room instead of a ring: terrace at the glass under the cantilever, pool across it, deck and planting beyond, with the lounging deck on the east end where the east wing throws late-afternoon shade. Put a garden door in each wing's south face (drop the 450 mm sills to thresholds) so the garden has three ways in.

### 97. The sunken courtyard has no sky and the light slots are 1 m shafts at H/W 10.3

**Severity:** MAJOR

**Numbers:** court roofed at +9.2 m; slot H/W 10.3 vs ~1.5 target; 20 m2 of ground floor missing but counted in GFA

**Evidence:** CT is x 9500-14500, y 15400-19400, cut from BASE_FL up to GF+200 = 1100 -- 5.0 x 4.0 x 2.8 m deep, dimensionally correct against the research (min 4x4, ideally 5-6 m, excavate 2.7-3.3). But the roof slab blk(HX0, WG_Y0-CANT, RF, HX1, NB_Y1, RF+SLAB) spans x 3000-21000, y 9500-24000 at z 8700-9200, and the two light slots that pierce it are at x 8000-9000 and 15000-16000 -- either side of the court, not over it. So the court is roofed 9.2 m overhead. It is a 2.8 m pit inside a covered volume, not a courtyard, and the research's whole point ('the pebble court is what makes the basement a served space, not a cellar') does not land. It also punches 20 m2 out of the ground-floor slab (13 m2 in the living volume, 7 m2 in the entry bar, directly on the arrival axis) with no bridge or guarding modelled -- and the printed GFA still counts that 20 m2, so ground is 176 not 196 and GFA 387 not 407. Separately, the two light slots are 1.0 m wide x 5.5 m long x 10.3 m tall: H/W = 10.3 against the research's hot-dry courtyard target of ~1.5, and well under the '5 x 5 m or it reads as a shaft' threshold. They consume 11.0 m2 of ground and deliver a 5.7 deg sky view at the base.

**Proposed fix:** Open the roof slab over the court (x 9500-14500, y 15400-19400) so it is genuinely exterior, and bridge the entry axis across it in glass -- the F.LOT move the research cites. Widen the two slots to 2.0-2.5 m (H/W 4-5) or delete one and spend the width on the other; a 1.0 m slot 10 m deep is not a patio.

### 98. The pool runs hard into the house: no terrace, no threshold, and the cantilever shades water instead of people

**Severity:** MAJOR

**Numbers:** Pool shell north face 12900 vs building face 12500 = -400 mm (inside). Cantilever 3.0 m, 100% over water. Glazing sill +1000 → coping +700 → water floor -700. Deck at north end: 0 mm.

**Evidence:** The pool shell's north face is at y = 12900; the living volume's south face is at y = 12500. The shell is buried 400 mm inside the building line and is unioned with the ground slab (z 400-900) -- they are one solid. Three consequences. (a) The pool's north wall and the two-storey wall carrying the 3.0 m cantilever occupy the same line, with the pool excavation at -1100 running alongside a footing that must be founded below it: the 45° load-spread question the brief asks is satisfied at the boundary wall but violated at the house. (b) The cantilever (y 9500→12500) oversails water for its entire 3.0 m projection, so there is no shaded terrace under it -- which is the only reason to cantilever over a pool. (c) Stepping out of the structural glazing (sill +1000, FFL +900) you land on the 400 mm-wide top of the pool wall at +700 -- a 300 mm drop onto a coping strip with 1.4 m of water immediately beyond, no deck, no guarding, no perimeter drainage channel. The research's deck rule (1.5 m where people walk, 3.5-4.5 m on the lounging side) is met on east and west (8.75 m each) and nowhere else.

**Proposed fix:** Pull the pool south by 3.0-3.5 m (POOL_Y1 from 12500 to ~9200). The cantilever then covers a 3.0 m shaded terrace at the water's edge -- the Interlude House move the docstring cites -- the north end frees up for the weir and basin, and the pool structure stops being the house's foundation. It also lengthens the south garden strip, which currently has no use.

### 99. The basin is only 6% oversized as a balance tank, and using it as one swings the visible water level 500 mm

**Severity:** MAJOR

**Numbers:** Basin 5,220 L gross / 2,900 L working; demand 2,744 L (margin 6%). Visible level swing 450-500 mm. Invert -900 = 1.6 m below the +700 water line (research 1.0-1.5 m -- acceptable, gravity fill fine). Evaporation 47.5 m² × 5-10 mm/day = 238-475 L/day for the still pool alone, roughly double with the sheet running.

**Evidence:** As drawn the basin is 5.8 × 1.0 × 0.9 m = 5,220 L gross. With the research's 200 mm freeboard and 200 mm low-level cut-out the working volume is 2,900 L. Demand built up honestly, per VILLA_RESEARCH.md §Catch basin: 8 bathers × 70 L = 560; water in transit in 2 × ~24 m of 100 mm pipe = 376; drawdown of a 5 mm film over a 47.5 m² surface = 238; backwash of a 1.0 m dia sand filter at 30 m/h for 4 min = 1,570. Total 2,744 L. The 40.7 L/m² rule gives 1,933 L, so the build-up governs. 2,900 vs 2,744 is 6% margin -- one longer backwash or a ten-person party breaks it. Worse, the working range means the water level in a 1.0 m wide *visible* garden basin rises and falls 450-500 mm in normal operation. The research's own standard for a water feature is that a mirror dropping 5 mm "reads as broken". And the basin is open to the sky: every leaf and every millimetre of rain lands in the balance tank and goes to the pumps, and the autofill float sits in an uncovered vessel.

**Proposed fix:** Split the two functions: a shallow constant-level catch trough that is the visible thing, weiring into a covered, ventilated, level-controlled balance tank of the research's 2.0 × 1.2 × 1.6 m (3.8 m³) inside the plant room. That also gets the autofill solenoid, the low-level cut-out and the leaf load out of the garden.

### 100. Plant floor would sit 3.5 m below the pool water line with no gully or sump -- a siphon puts 386 mm of water across the basement

**Severity:** MAJOR

**Numbers:** Static head plant-to-water 3,500 mm (rule 1,000-1,500). Siphon volume 54.4 m³ ÷ 141 m² = 386 mm depth. Court invert -2800, same level, no sump.

**Evidence:** Basement floor is -2800; pool water is +700. Any plant in the basement is 3.5 m below the water line, against the research's 1.0-1.5 m. Flooded suction is over-served; the real consequence is that a failed seal, a cracked filter body or an open valve siphons the pool down to pipe level. Net water volume is 54.4 m³ (66.5 m³ gross less the 12.1 m³ Baja shelf) -- spread over the 141 m² basement that is 386 mm deep across the whole floor, and the sunken court's invert is the same -2800 so it fills too. The research is explicit: the plant room "needs a floor gully (the room will flood)". Nothing in villa_3d.py models a gully, a sump, a fall, or any drainage anywhere on the site -- not on the roof, not in the court, not in the basement.

**Proposed fix:** Put the plant in the 12900-15000 strip at a raised floor (say -1000 to -1500, i.e. 1.7-2.2 m below the water line) rather than at basement datum; fit non-return and lockable isolating valves at the pool penetrations, a bunded floor with a pumped gully, and a second sump in the court.

### 101. The "south long side" is the 5.0 m short end -- the weir is half the length the brief describes

**Severity:** MAJOR

**Numbers:** Weir 5.0 m. Thin sheet at 40-60 L/min/m = 200-300 L/min = 12-18 m³/h; heavy curtain at 90-150 L/min/m = 450-750 L/min = 27-45 m³/h. Over 9.5 m those would be 380-570 and 855-1,425 L/min. Pool 47.5 m² = 6.8% of plot (research target ~10%, 45-50 m² -- surface area is right, proportion is not). Lap length 9.5 m vs 12 m minimum.

**Evidence:** POOL_X0..X1 = 9500..14500 gives 5.0 m; POOL_Y0..Y1 = 3000..12500 gives 9.5 m. The pool runs north-south, so its south face is the 5.0 m SHORT end. Both the brief and villa_3d.py's docstring call it the "south long side". Separately, the docstring at line 31-32 says the pool is "12.0 x 4.0 m" -- the research's target -- while the constants build 5.0 × 9.5. The 9.5 m length also falls short of the research's lap minimum ("Lap swim ≥12 m"). The hydraulic effect of the shorter weir is actually favourable, but it makes the waterwall a 5.0 m wide × ~1.1 m tall panel rather than the 9.5 m wall the description implies.

**Proposed fix:** Either fix the prose to match the geometry, or rotate the pool to 12.0 × 4.0 m running east-west across the garden as the research's Alhambra analysis recommends -- 48 m², a 12 m lap, and a 12 m weir facing the house. Size the dedicated overflow pump at ~15 m³/h for a 5 m thin sheet, separate from filtration, and say so on the drawing.

### 102. No steps, no ladder, a 700 mm rim to climb, and the Baja shelf takes the whole shaded end

**Severity:** MAJOR

**Numbers:** Rim +700 above garden; water floor -700; shelf top +400 (300 mm submerged); shelf 5.0 × 2.2 m = 11.0 m² = 23% of the water surface. Shelf displaces 12.1 m³ of the 66.5 m³ gross.

**Evidence:** Nothing in villa_3d.py models steps or a ladder. The research specifies 300 rise / 300 going with the top step at deck level. With the coping at +700 and the garden at 0, a swimmer must haul themselves over a 700 mm parapet from a 1.4 m deep tank; the raise is above the research's seat-height 450 mm, so the edge is a barrier, not the seat the raise is supposed to buy. The Baja shelf (villa_3d.py:271-272) is x 9500-14500 × y 10300-12500 × top +400: 300 mm submerged (research 250-350 ✓), 2.2 m front-to-back (1.8-2.5 ✓), but 5.0 m along the end against the research's 2.5-4.0 m -- it takes the entire width, and it is at the north end, under the cantilever and the building, where it gets no sun. A sun shelf in permanent shade is not a sun shelf.

**Proposed fix:** Move the shelf to the sunlit south or east end, cut it back to 3.0-4.0 m of the width, and take the steps out of it: 300/300 treads with the top step flush with the +700 coping and a submerged handhold. Keep the 1.4 m constant depth -- that part follows the research correctly.

### 103. The pool does not sit over the basement -- no suspended-slab water-retaining condition, but the F.LOT move the design claims is not built

**Severity:** MAJOR

**Numbers:** Clear gap 2,100 mm. Overlap 0.000 m³. Pool base -1100 vs basement raft -3200 = 2,100 mm below. Active wedge reach 1,850 mm < 2,100 mm gap. Unused strip 2.1 × 18 m = 37 m².

**Evidence:** Answering the brief's question directly: pool shell north face y = 12900, basement south face y = 15000 → 2,100 mm clear, and the computed overlap of the two solids is 0.000 m³. The pool is fully ground-bearing, base at -1100, with the basement raft 2.1 m below at -3200. So none of the research's §Structural "above a basement" package applies: no tanking over habitable space, no drained cavity with leak detection, no 0.2 mm crack-width design, no movement/isolation detail at a suspended perimeter. Structurally that is the safe answer and it is worth stating on the drawings. But villa_3d.py's design basis and VILLA_RESEARCH.md's "SECTION WORTH STEALING" both call for floating the pool over part of the basement, and the built geometry does not. I also checked the surcharge the other way: for a 3.2 m retained height, a Rankine active wedge at 60° reaches 3.2/tan 60° = 1.85 m from the basement wall -- the pool sits at 2.1 m, just outside it, so it imposes no significant surcharge either.

**Proposed fix:** Leave the pool ground-bearing -- it is the right call on this plot and it removes a whole tier of risk. Then use the 37 m² strip it created for the plant room and the north-facing weir/basin (see the plant-room and orientation findings), and delete the F.LOT claim from the docstring so the description matches what is drawn.

### 104. 45° load-spread clears at the pool by 1.6 m but the basin is inside it once you allow a base slab and working space

**Severity:** MAJOR

**Numbers:** Pool shell: needs y≥1025, has 2600 → +1,575 mm. Basin invert -900: needs y≥825, has 1600 → +775 mm. Basin with 300 mm slab (-1200): needs y≥1125 → +475 mm, and ~0 after working space. Basin to property line 1,600 mm vs 1,500 mm setback.

**Evidence:** Using the research's own assumption -- a boundary-wall footing 700 mm wide centred on the 350 mm wall with its base 600 mm below garden, so the inner bottom edge is at y = 525, z = -600 -- the required 45° clearance is y ≥ 525 + (depth below -600). Pool shell base at -1100 needs y ≥ 1025; the shell is at y = 2600, clear by 1,575 mm. That is a genuine pass and it is what the 700 mm raise bought. The basin is the problem: invert -900 needs y ≥ 825 and the basin face is at 1600, clear by 775 mm -- but add a 300 mm base slab and blinding to -1200 and the requirement rises to y ≥ 1125, leaving 475 mm, which disappears entirely once you allow the 500-600 mm of formwork working space you need outside a 900 mm deep chamber. And there is no room to move it north: the basin's south face is 1,600 mm from the property line, only 100 mm inside the typical 1.5 m pool setback.

**Proposed fix:** Moving the weir and basin to the north end removes this entirely. If the basin stays south, design the boundary-wall footing to bear on or below the basin structure, or make the basin's south wall a designed retaining wall carrying the boundary wall's surcharge -- and record the assumed footing depth on the drawing, because 600 mm is an assumption, not a survey.

### 105. The 1.0 m light slots are unglazed 9.9 m deep shafts capped by the roof -- they cost 12 m2 a floor and deliver nothing

**Severity:** MAJOR

**Numbers:** Slots 1,000 wide x 6,100 long, z 400-10300 → H/W = 9.9 against the research's courtyard target of ~1.5. Roof bridges 2,700 mm over the south end. Zero openings in any of the four walls facing each slot.

**Evidence:** Lines 174-177 cut x 8000-9000 and 15000-16000 from y 12200 to 18300. The roof (line 165) runs y 9500-24000, so 2.7 m of solid slab caps the south end of each slot -- it never reaches the garden edge and is never open to sky along its length. Nothing looks into them. They are two 1.0 m maintenance voids consuming 12.2 m2 per floor, and in the aerial they read as two rectangular holes punched in a roof plate rather than as slots splitting the mass. The AGi 'patios developed three-dimensionally' reference is not delivered.

**Proposed fix:** Either delete them and recover 12.2 m2 per floor, or commit. To commit: widen to 1,800 mm (x 7800-9600 and 15400-17200, H/W 5.7), glaze both flanks full height so the wings and the living volume actually look into them, floor them in white pebble per F.LOT, and extend the roof cut south to the roof's front edge (y 9000/11000) so each slot is open to sky for its whole length. The wings then genuinely detach and the aerial reads as three masses under one stepped roof -- which is the scheme you drew in the docstring.

### 106. Window proportion: two near-square punched holes per wing, identical, centred, stacked

**Severity:** MAJOR

**Numbers:** Ground 2,600 x 2,650 = 1.02:1. First 2,600 x 2,250 = 1.16:1. Both centred in a 5.0 m wing (1,200 mm each side). Both sills at +450 above their own floor.

**Evidence:** Lines 242-244. A square opening is the least considered proportion available, and two of them at nearly the same size stacked vertically reads as an oversight rather than a decision. Centring both in the wing is what a spec builder does. Separately, a 450 mm sill on the first floor at +5.0 m is a fall hazard with no guarding modelled -- it needs 1,100 mm of protection, and nothing in the model provides it.

**Proposed fix:** Stop punching holes; make the wings piers and glass. Per wing per floor, one glazed slot the full width between the 400 mm end piers: x 3400-7600 (4.2 m) and 16600-20600. Ground: sill +400, head +3,300 → 4,200 x 2,900 (1.45:1). First: sill +450, head +2,700 → 4,200 x 2,250 (1.87:1) with an 1,100 mm structural-glass guard set 100 mm inboard of the glass line. Set both glass planes 300 mm behind the outer wall face. The wings then read as two vertical stone piers with light between them, and the two floors read as related but not identical.

### 107. No reveals and no material differentiation -- 'deep reveals' exists only as a comment

**Severity:** MAJOR

**Numbers:** WALL = 400.0 annotated 'thick external wall, deep reveals' (line 80). Every opening void is cut from y−300 to y+300 -- 300 mm proud of the wall on BOTH faces. Actual reveal: 0 mm.

**Evidence:** Nothing in the model positions the glazing plane, so every window is a hole with no depth. There is also exactly one material in the entire villa: no cladding zone, no plinth, no change of texture between the raised ground floor and the storey above, no shadow gap anywhere. The research names the three cheap moves that read as expensive -- 100-150 mm rebated-return stone, 10-20 mm shadow gaps, one head datum -- and the model implements none of them. This is why the aerial reads as a massing study rather than a building.

**Proposed fix:** Three additions, all cheap in the model. (1) Set every glazing plane explicitly 300 mm behind the outer face; the 400 mm wall then reads as thickness in every opening. (2) Add a 900 mm stone plinth from street level (z 0) to the raised ground floor (z 900) in 100-150 mm rebated-return stone, separated from the render above by a 20 mm x 20 mm shadow gap -- this also visually explains the 900 mm privacy lift, which currently reads as an accident. (3) 20 mm shadow gap at every slab/wall junction and at the cantilever soffit, with a drip.

### 108. The roof is one unbroken 1.6 m x 18.0 m fascia and it flattens the whole composition

**Severity:** MAJOR

**Numbers:** Slab 500 + parapet 1,100 = 1,600 mm of continuous solid from z 8700 to 10300, spanning 18,000 mm with no break (lines 165-168).

**Evidence:** Because the slots stop short of the front edge (previous finding) and the roof projection is a uniform 3.0 m, the strongest element in the elevation is a single 18.0 m long, 1.6 m deep band sitting on everything. It is the heaviest line in the drawing and it is doing no compositional work -- it caps the three masses into one block and it is the reason the aerial reads as a lid on a box.

**Proposed fix:** Split it in section and in plan. Section: recess the parapet 350 mm behind the slab edge with a 40 mm shadow gap between them -- the eye then reads a 500 mm slab edge floating clear of a set-back parapet, and apparent depth drops from 1,600 to 500 mm. Plan: adopt the stepped roof edge from the cantilever finding (wings 1.5 m at y 11000, centre 3.5 m at y 9000) and cut the slots through to that edge. One 18.0 m line becomes five segments at three depths.

### 109. Roof pavilion is over the street, on the axis, roofless and unreachable

**Severity:** MAJOR

**Numbers:** PV = (9000, 19000, 15000, 24000) -- centre x 12000 = AXIS, north face flush with the street facade at y 24000. Adds 3.0 m to an already 10.3 m elevation. Walls only, no roof (lines 169-171). Stair runs GF→FF only (lines 232-235).

**Evidence:** It is placed at the wrong end of the roof: it sits directly above the entrance, on the centreline, making the street elevation a symmetrical 12.2 m tall composition topped by a 6.0 m box centred over a 1.5 m door -- top-heavy and unresolved. It has no roof, so it is a 6 x 5 m open pen 3.0 m tall that provides zero shade and reads from the street as a blind parapet extension. And there is no stair to it, so as modelled it cannot be entered.

**Proposed fix:** Move it to x 3000-9000, y 12500-17500 -- the south-west roof, over the west wing, facing the pool -- and pull it 1,000 mm back from the roof edge on every side so it never touches a facade plane. Give it a real 2,800 mm clear pergola or slab (the research's Gulf default is aluminium). Extend the stair core to roof level: 4,200 mm rise, 18 risers at 233 / 280 going, dog-leg inside the existing 1,600 x 3,200 void at x 13000-14600, y 18700-21900. That also removes 3.0 m from the street elevation and drops overall height from 12.2 m to 10.3 m.

### 110. The 3.0 m cantilever has a 400 mm backspan over a 5.6 m opening -- the section is a structural fiction

**Severity:** MAJOR

**Numbers:** Line 162 removes the first-floor slab over y 12500-18000. Line 142 puts the cantilever floor at y 9500-12900. Backspan = 400 mm for a 3,000 mm cantilever. Line 238 removes the ground-floor south wall below it (x 9200-14800, z 1000-4300), leaving a 100 mm skin at y 12800-12900.

**Evidence:** The box hangs off nothing and lands on nothing: the double-height void is directly behind it and a 5.6 m structural-glass opening is directly beneath it. Any architect reading the section sees this immediately, and it undercuts the cantilever's credibility more than any composition issue -- a cantilever that is obviously impossible cannot read as deliberate.

**Proposed fix:** Make the structure the composition. Hang the box from the roof slab on two 250 x 400 mm blades in the flank walls at x 9000-9250 and 14750-15000 -- the 3.5 m roof cantilever (500 mm slab, span/depth 7) is already sound, and expressing two hangers is legible and honest. Alternative: two 400 x 900 mm upstand beams in the box flanks carried back to the north-bar wall at y 18000 -- 5.5 m backspan for a 2.0 m cantilever = 2.75:1, correct -- expressed as a 900 mm downstand each side of the double-height volume, which also scales that shaft down.

### 111. Four different head heights on the ground floor -- the scheme breaks the one discipline the research names as the mark of expense

**Severity:** MAJOR

**Numbers:** Entrance head GF+2400 (line 249). Internal doors GF+2700 (DH, line 225). Wing window head GF+3100 (line 243). Living-volume glazing head GF+3400 (line 239). Ceiling GF+3600.

**Evidence:** VILLA_RESEARCH.md section 2 states it explicitly: 'One setting-out grid -- stone joint, ceiling joint, door head, window head and skirting all on the same module. That discipline is what reads as expensive.' The plan grid is disciplined; the section is not. The entrance in particular is 1,500 x 2,400 where the research calls for a pivot at 1,200-1,500 wide x 2,700-3,000 high, and a 2.4 m head in a 10.3 m facade is a 1:4.3 ratio that makes the door disappear.

**Proposed fix:** Two head lines, not four. Doors and the entrance pivot at +3,000 (entrance 1,500 x 3,000, z 900-3900). All south glazing head at +3,300. Ceiling at +3,600. Repeat the same two lines on the first floor at +2,400 and +2,700. Then cut a real entrance recess: 3,000 wide x 5,000 high x 1,200 deep into the north wall at x 10500-13500, y 22800-24000, with the pivot inside it -- that gives the street facade its one deep shadow, which it currently completely lacks.

### 112. Fin proportion is wrong for a west facade: 450 x 180 at 600 c/c gives a 43 degree cut-off

**Severity:** MAJOR

**Numbers:** Blade 450 deep x 180 wide, 600 c/c → clear gap 420 mm. Cut-off = arctan(420/450) = 43 degrees off-normal. 9 blades over y 12800-17780 inside a 12500-18000 wing: end margins 300 and 220 mm.

**Evidence:** Low afternoon west sun arrives within 20-30 degrees of normal to a west wall; an array that only starts to block at 43 degrees intercepts the midday sun that is not the problem and passes the 3-5 pm sun that is. The proportion is also wrong in elevation: a 180 mm blade 7,800 mm tall is a 43:1 sliver at 600 mm centres -- a pinstripe grain against a building whose every other module is 5-6 m. And 9 blades with unequal end margins is a detail an experienced eye catches instantly.

**Proposed fix:** 100 mm wide x 900 mm deep blades at 400 mm centres -- clear gap 300, cut-off arctan(300/900) = 18 degrees -- rotated 25 degrees toward north so the blade face is roughly normal to the 3-5 pm sun. 13 blades over the 5,500 mm wing with 300 mm equal end margins. Land them on a 450 mm plinth with a 40 mm shadow gap at the base and stop them 40 mm clear of the roof soffit. If 900 mm depth is too much for the 700 mm available in the setback, use 100 x 600 at 300 c/c (gap 200, cut-off 18.4 degrees) -- same performance, tighter grain.

### 113. Family living is 28.6 m², entirely double-height, and reads as a shaft rather than a room

**Severity:** MAJOR

**Numbers:** 28.6 m² vs 35-45 (-18%) · 5.2 × 5.5 m plan vs 7.30 m height · 100% double-height vs 40% recommended · family dining 0 m² vs 14-18 · 0 doors between the family living volume and the guest arrival sequence

**Evidence:** villa_sheets.py:33 -- 5.2 × 5.5 m = 28.6 m² against VILLA_RESEARCH.md:321 family living 35-45. All of it is double-height at 7.30 m clear, so the volume is taller than it is wide in both plan directions; VILLA_RESEARCH.md:124-128 says to plan such a volume at least as wide as it is tall and warns that below ~5 × 5 m it reads as a shaft, and prescribes ~60% single-height sofa zone at 3.0-3.2 m with 40% double-height at the glazed edge. Here it is 100% void, with no rooflight (the roof slab is solid over it) and its garden glazing blocked, so the compression-release at the 2.40 m entry soffit opens into a dark well. It is also left deliberately open to the entrance hall (villa_3d.py:202-203), so the family's only sitting room is the arrival space guests stand in. There is no enclosed family room and no family dining anywhere (VILLA_RESEARCH.md:322 family dining 14-18 m²: 0 m² provided).

**Proposed fix:** Keep the double height only over the 6.0 × 2.5 m glazed garden edge and floor the rest at first-floor level (which also recovers area for finding 1). Give the family room a door or a full-height sliding screen off the hall, and take the family dining out of the oversized landing area.

### 114. 48 m² of the 407 m² GFA -- 12% -- is floor nothing can reach

**Severity:** MAJOR

**Numbers:** orphan cantilever 18.0 m² gross / 13.5 m² net · roof pavilion 30 m² · 48 m² = 11.8% of GFA 407 m² unreachable · headline GFA falls to 359 m² of usable area

**Evidence:** The first-floor cantilever plate (villa_3d.py:140-142, FF_FOOT includes x 9000-15000, y 9500-18400) leaves an 18.0 m² gross / 13.5 m² internal room over the pool, walled on three sides, with no window and no door, separated from the landing by 5.5 m of open double-height void. It is counted in the printed "first 181.0 m2". The 30 m² roof pavilion (villa_3d.py:107, :169-171) is likewise counted in the 407 m² GFA and has no stair to it -- the only stair stops at FF. VILLA_RESEARCH.md:338 expects the roof level to carry the stair head, a roof WC and store plus 60-90 m² of shaded terrace.

**Proposed fix:** Continue the stair to the roof (it also fixes the pavilion's purpose), and either floor the void back to reach the cantilever as a shaded first-floor loggia over the pool, or delete the cantilever plate from the FF footprint so the GFA figure stops counting it.

### 115. A 35.6 m² landing is larger than any bedroom and 1.4× the entire master suite

**Severity:** MAJOR

**Numbers:** landing 35.6 m² vs 12 briefed · 27% of the first-floor net · master suite 24.9 m² · 23.6 m² recoverable

**Evidence:** villa_sheets.py:38 -- LANDING 8575,18400→15425,23600 = 6.85 × 5.2 = 35.62 m², which is 27% of the 131.6 m² first-floor net. VILLA_RESEARCH.md:336 budgets family landing 12 + circulation 13. It is windowless, and after the stair void (1.6 × 3.2 = 5.1 m²) it still leaves ~30 m² of unlit circulation while the master bedroom is 9.1 m² and three bedrooms have no bathroom.

**Proposed fix:** Cut the landing to a 1.4 m gallery plus the stair (≈14 m²) and give the 21 m² recovered to the master suite and to en-suites for Bedrooms 1 and 3.

### 116. None of the three guest bedrooms can become a guest suite: the 5.0 m wing module is only 4.2 m internally

**Severity:** MAJOR

**Numbers:** 22.5 / 22.5 / 26.1 m² vs 28-35 each · wing internal width 4.2 m · best achievable bed zone 13.9 m² vs 18-22 · shortfall 5.5-8.5 m² per suite

**Evidence:** villa_sheets.py:37,42,43 -- Bedroom 3 26.1 m², Bedrooms 1 and 2 22.5 m² each, all undivided, against VILLA_RESEARCH.md:317 guest suite 28-35 (bed 18-22, wardrobe 4-6, en-suite 6-8). The wings are WW_X0..WW_X1 = 3000..8000 and EW_X0..EW_X1 = 16000..21000 (villa_3d.py:87-88), i.e. 5.0 m external and 4.2 m internal. An en-suite needs 2.2-2.4 m of width, leaving 1.8 m -- too narrow for a bed alongside -- so the split has to run across the 5.35 m depth, giving bed 4.2 × 3.3 = 13.9 m² against the 18-22 required. The wing module itself, not the layout, is what fails.

**Proposed fix:** Widen the wings from 5.0 m to 6.0 m (WW_X1 → 9000, EW_X0 → 15000), which the 18.0 m buildable width can absorb if the two 1.0 m light slots are reduced to 600 mm, or accept three bedrooms plus one proper master.

### 117. The water axis is two disconnected ponds 11.9 m apart, at levels that run backwards

**Severity:** MAJOR

**Numbers:** rill 3.9 m + pool 9.5 m = 13.4 m of water on a 29.0 m plot, separated by 11.9 m of dry building. Levels: rill invert −300, coping +150; pool water +700 -- the axis runs uphill by 550-1000 mm.

**Evidence:** On the axis (x=12000) the model has: a rill from y=24400 to 28300 (3.9 m, lines 273-276) sitting entirely in the front setback, and the pool from y=3000 to 12500 (9.5 m) in the rear garden. Between them is 11.9 m of building with no water and -- per finding 1 -- no opening. The levels make the concept impossible even in principle: rill coping +150, invert −300; pool top water +700. The pool is 550-1000 mm HIGHER than the rill, so water cannot run from the entrance to the pool; a 'single water axis' implies one falling level. The rill also starts and ends at nothing -- 400 mm short of the house's north face, 350 mm short of the boundary wall -- with no source, no basin and no spill. And it is 500 mm wide against a 5000 mm pool: a 1:10 jump with nothing between.

**Proposed fix:** Make it one body at one falling level and run it through the house. Rill top water +900, flush with the ground-floor slab, from the boundary inner face y=28650 to the house at 24000; one 200 mm fall at the threshold; a 500 mm channel cast in the ground slab from y=23600 through the hall and living volume to 12500 (11.1 m); discharge into the pool at +700; the pool's own 700 mm overflow is then the last fall in the sequence. That gives 25.3 m of continuous water on a 29 m plot instead of 13.4 m in two pieces. The front door becomes a 1.2 m bridge over the channel, or two 1.2 m leaves flanking a 500 mm glass-covered slot.

### 118. The rill exists only as annotation: it is 150 mm proud of grade and appears in no model-derived drawing

**Severity:** MAJOR

**Numbers:** rill 3900 × 500 × 150 mm proud; plan cut planes at +1200 (GF), so 0 of 4 plans show it; section shows a 100 mm slab; 0 annotation entities in any model-derived drawing.

**Evidence:** The rill solid spans z −400 to +150 with a void −300 to +200, so it stands 150 mm above the entry court. Every plan is cut at 1200 mm above its floor, so the rill is invisible in VILLA_PLAN_GF.dxf -- the X/Y value dump contains 24400 and 28400 (the porch) but no 28300 (the rill). It reaches A-201 only because villa_sheets.py lines 74-75 draw a 2D box by hand and line 86 letters it 'REFLECTING RILL ON ENTRANCE AXIS'. In VILLA_SECTION_AA.dxf the axis cut passes down the middle of the channel and returns a 100 mm slab between z −400 and −300, in a section with no ground line, no water, no levels, no poché and zero text entities. The one element carrying the stated concept is legible in the caption and nowhere else -- precisely the failure mode the lens asks about.

**Proposed fix:** Model the water as a solid so it can be cut and rendered: a thin body at top-water level in the rill, the pool and the catch basin, on its own layer, exported to a WATER layer with a light screen. Add a ground/site solid at z=0 so sections have a grade line, and annotate SECTION AA with levels (+0.90 FFL, +0.70 TWL, −2.80 basement) and the compression/release dimension. A section on the axis that shows no water cannot argue a water axis.

### 119. Arrival never touches the axis, and there are no entrance steps for the 900 mm level change

**Severity:** MAJOR

**Numbers:** gate centre 16000 vs axis 12000 = 4.0 m off; porch occupies x 3500-10500 of the 24 m frontage; 900 mm level change with 0 steps modelled; 0 of 3 cameras on the axis.

**Evidence:** Line 285 puts the pedestrian gate at x 15400-16600 -- centre 16000, a full 4.0 m east of the axis at 12000. The vehicle gate (line 284) is at x 3800-8300 and the car porch (PORCH_X0/X1 = 3500-10500) occupies the whole west half of the front setback beside the rill. So whether you arrive on foot or by car you enter off-axis and walk past the rill sideways; there is no point on the site from which the sequence gate → rill → door → pool can be seen. The ground floor is at +900 with the entry court at 0 and no steps, ramp or threshold modelled anywhere on the site, so the axis cannot physically be walked. There is also no view down it in the drawing set: the three cameras are two aerials and 'POOL_EYE' at (12000, −14000, 2600), which is 14 m outside the south boundary -- VILLA_VIEW_POOL_EYE.png is half filled by the 2.4 m boundary wall.

**Proposed fix:** Move the pedestrian gate to AXIS±750 (x 11250-12750), the same width as the front door, and leave the vehicle gate where it is. Add the 900 mm rise as 6 risers at 150 with 400 going, the full width of the court and split either side of the rill, set 5.5 m back from the gate line for standing space. Then replace POOL_EYE with the only view that tests the scheme: eye at (12000, 30500, 1600), looking at (12000, 8000, 1200) -- standing at the gate, on the axis, at eye height.

### 120. The pool contradicts the Alhambra proportion the scheme is built on -- and its own docstring

**Severity:** MAJOR

**Numbers:** built 5.0 × 9.5 = 47.5 m² at 1.9:1; docstring 12.0 × 4.0; research 20-24 × 4.5-5.0 at 4.8:1. Terrace between house and water: 0 mm. South strip beyond the catch-basin trench: 1250 mm.

**Evidence:** The docstring (line 31-32) says the axis is 'carried the LONG way… terminating in the swimming pool proper at 12.0 × 4.0 m'. The constants (lines 94-95) build 5.0 × 9.5 m. That is 1.9:1, running the SHORT way relative to its own width, against the Court of the Myrtles' 34.0 × 7.10 = 4.79:1 that the design basis cites, and below the 12 m lap-swim threshold the research sets. At 5.0 m wide against a 24 m plot it also reads as a square block in the middle of the garden rather than an extension of a 500 mm rill. Compounding it: the pool's north wall is coincident with the building's south wall (pool shell 12500-12900, LV wall 12500-12900), so there is zero terrace and zero visible coping -- you step out of the living room into the water, 200 mm below the internal floor, with no guarding. And the one-sided overflow spills SOUTH, into an open 1.0 m × 0.9 m deep trench (line 269-270) with a 1.25 m strip beyond it before the boundary wall, so the designed waterwall faces the one edge of the site nobody can stand on.

**Proposed fix:** Narrow the pool to 4.0 m (x 10000-14000, inside the 6.0 m living-volume width so it reads as the rill widened) and lengthen it to the garden: y 3350-12500 gives 9.15 m, or pull the house's south face north to y=15000 to get the full 12.0 m the docstring claims. Turn the overflow through 90°: spill along the EAST long side into a basin the terrace looks across, and give the west side a 3.5 m lounging deck. Hold a 1.5 m walking edge between the building face and the water.

### 121. Not one idea -- three, and the drawing shows the one that wrecks the plan

**Severity:** MAJOR

**Numbers:** 13 declared moves; 3 partis; 2 light slots × 1.0 m causing 4 walk-through rooms; roof pavilion 30 m² with 0 stairs; fins at x 2300-2750, outside the 3000 setback line.

**Evidence:** The docstring stacks 13 declared moves on a 407 m² house: water axis, raised pool + waterwall, semi-basement + sunken court, ground floor raised 900, 3.0 m cantilever, double-height volume, two 1.0 m light slots, threshold compression, west fins, three entrances, roof pavilion, Alhambra proportion, Casa Mérida perspective. Three incompatible partis are fighting inside that list. (a) An AXIS -- Casa Mérida, one line from gate to pool. (b) A COMB -- AGi Wall House, three parallel bars separated by full-height slots. (c) A SECTION -- F.LOT/Interlude, void and court and cantilever. The comb wins in the geometry and it is the direct cause of the plan failures: the slots sever both wings at every level, which forces bedroom-through-bedroom, dining-through-kitchen and study-through-majlis. The axis wins only in the captions. The section idea then puts its sunken court ON the axis and its cantilever ACROSS the terminal view. VILLA_ELEV_S.png shows the result: a symmetrical A-B-A box with four identical punched squares and a boundary wall across its middle -- a courtyard elevation, not an axial one, and nothing of the stated scheme reads.

**Proposed fix:** Pick the axis and subordinate everything to it. Keep: the rill-through-house, the raised ground floor, the double-height volume, the cantilever as a slab. Demote: one light slot, not two (keep the west one as a real 1.5-2.0 m court with a tree, glaze the east junction and walk through it). Delete: the 30 m² roof pavilion that has no stair, and the west fins that sit outside the setback line. Then move the sunken court off-axis. Every remaining move should be answerable with 'it makes the axis longer, lower or brighter' -- if it isn't, it is the second idea.

### 122. The car porch cannot stand up, and sits inside the front setback

**Severity:** MAJOR

**Numbers:** slab 7.0 × 4.0 m on one 250 mm blade; two 'columns' 250 mm tall spanning z 3800-4050 with 3800 mm of air below; blade base at +900 over ground at 0; porch 28 m² inside a 5.0 m setback; coverage with porch 224/696 = 32.2%, not the printed 28%.

**Evidence:** Lines 253-256. The 7.0 × 4.0 m, 200 mm RC roof slab is carried by exactly one 250 mm blade wall at its east edge (PORCH_X1−250 to PORCH_X1). The two elements at x=3600 and x=6900 that read as columns are blocks from z=3800 to 4050 only -- 250 mm tall beams floating in mid-air with nothing beneath them. And the single blade that does carry the slab starts at z=GF=900 while the ground at the porch is z=0, so the only support hovers 900 mm above the ground. As modelled it is a 7 m cantilever off one 250 mm blade that touches nothing. Separately, PORCH_Y0/Y1 = 24400-28400 places a permanent roofed RC structure inside the 5.0 m front setback; the research's BUA lever is a lightweight pergola, not a 200 mm slab.

**Proposed fix:** Run the two blades full height, z=0 to GF+3150, and set them at the slab's third points; or drop the slab and use an aluminium pergola at 2.7-3.0 m clear, which is both buildable and the thing that is actually excluded from BUA. Add a build-time check that every solid's minimum z either equals 0 or sits on another solid.

### 123. The semi-basement is one empty 18 × 9 m box and the sunken courtyard is not an enclosure

**Severity:** MAJOR

**Numbers:** basement 162 m² gross / 141 m² internal, 1 room, 0 partitions, 0 windows, 0 stairs; court 20 m² with 0 enclosing walls; research schedule requires 6 rooms totalling ~114 m².

**Evidence:** VILLA_PLAN_BASEMENT.dxf contains four X values (3000, 3400, 20600, 21000) and four Y values (15000, 15400, 23600, 24000) -- a single rectangular ring and nothing else. No partitions for the maid's room, laundry, store, plant or pool plant that the scheme's own justification (docstring finding 2, research §5) depends on; no glazing anywhere in the perimeter, which is solid from −2800 to +400; no stair. The 'sunken courtyard' is not modelled as a court at all: CT lies inside the basement's interior, so cutting it changes nothing below and it exists only as the 5.0 × 4.0 hole it punches in the ground-floor slab above. The printed '142 m² excl. a 20 m² sunken court' is arithmetic on rectangles that have no counterpart in the geometry.

**Proposed fix:** Give the court real walls: drop it outside the basement footprint (excavate against the north bar's east end) so it has three retaining walls and one fully glazed face into the basement, white pebble floor, 5.0 × 4.0 minimum. Partition the basement -- maid's room 12 + bath 4 + laundry 10 + store 8 + plant 16 + pool plant 14 -- and connect it with the second stair from finding 5. Acoustic separation: the pool plant must not share a wall with the majlis above.

### 124. The two 1.0 m light slots are dark shafts that light nothing, and they sever the roof and first floor

**Severity:** MAJOR

**Numbers:** 1.0 m wide x 6.1 m long x 9.40 m deep. H/W 9.4:1. Well index 5.47 (useless above 2). Sky view factor at the ground-floor floor 2.05%, at basement level 1.09%. Sky angle across the slot 6.1 degrees. Zero glazing faces them. They cost 2.0 m of the 18.0 m buildable frontage (11%).

**Evidence:** The slots are cut at x 8000-9000 and 15000-16000, y 12200-18300, z 400-10300 (villa_3d.py lines 174-177). Against VILLA_RESEARCH.md's own courtyard rule -- hot-dry H/W ~1.5, a 5-7 m wide court on a two-storey villa -- a 9.40 m deep slot needs to be 6.3 m wide. At 1.0 m it is six times too narrow. I computed the sky view factor at the slot floor by the standard configuration factor for a rectangular aperture: 2.05% at ground level, 1.09% at basement level. Well index 5.47 means well efficiency around 10% even at 80% wall reflectance. Worse, no opening in the whole model faces a slot -- the walls of dining, family living and study that bound them are blank, so the slots do not light one square metre of anything. What they do achieve is damage: they disconnect the first floor (finding above), they cut the roof slab, and because the void stops at y 18300 against a north-bar inner face at 18400 they leave two free-standing concrete fins 100 mm thick, 1.0 m long and 9.9 m tall -- a slenderness ratio of 99. In VILLA_VIEW_AERIAL_SW they read as two thin slits in an otherwise unbroken box; the three-finger parti the design basis claims is invisible from the ground.

**Proposed fix:** Delete both slots and give the width to the living volume -- this is the single highest-value move in the scheme. 5.0 + 1.0 + 6.0 + 1.0 + 5.0 becomes 4.5 + 9.0 + 4.5 across the same 18.0 m. The living bay goes from a 6.0 m grid to 9.0 m, the clear volume becomes 8.2 x 5.5 x 7.8 m, h/w drops from 1.50 to 0.95, and family living becomes 45.1 m2 -- inside the researched 35-45 m2 band for the first time. If a slot must survive as a parti gesture, widen one to 3.0 m minimum (WI 2.34, SVF 6.1%) and glaze both flanking walls onto it, or the geometry is decoration.

### 125. The double-height volume is a shaft by the research's own test, and has no aperture above 4.30 m

**Severity:** MAJOR

**Numbers:** Clear 5.2 x 5.5 m x 7.80 m. h/w 1.50, h/d 1.42 -- height exceeds both plan dimensions. 223 m3 over 28.6 m2. Double-height share of the family living room: 100%, against a 40% target. Apertures above 4.30 m: zero.

**Evidence:** VILLA_RESEARCH.md section 2 gives two tests. First, 'Plan it at least as wide as it is tall in one direction; below ~5 x 5 m it reads as a shaft.' The clear plan is 5.2 x 5.5 m -- barely over the 5 x 5 threshold -- while the clear height is 7.80 m, so it fails the width-versus-height test in both directions by 2.3 m. Second, '~60% of the living room single-height at 3.0-3.2 m (the sofa zone), 40% double-height at the glazed garden edge.' The void here is the entire room: FF_FOOT (line 141) simply omits the living bay, so there is no first-floor slab anywhere over it and there is no sofa zone at all. And the volume is lit only from the bottom: the roof slab spans over it at z 8700 with no rooflight, no monitor, no clerestory. The research's own clerestory finding -- a high aperture pushes daylight 4-6 m back on a 2.5x head-height rule -- is quoted in the design-basis docstring and then not used. A head at 8.70 m would reach 21.8 m by that rule, lighting the whole ground floor including the dark north bar. Note also that build() prints '7.30 m clear' and 'compression ratio 1:3.0' using RF - SLAB; the soffit over the void is the roof slab at RF = 8700, so the true figures are 7.80 m and 1:3.25.

**Proposed fix:** Do both halves at once. Widen the bay to 9.0 m by absorbing the slots, then return the first-floor slab over the north 3.3 m of it: 60% single-height sofa zone under a 3.2 m ceiling, 40% (18.0 m2) double-height at the glazed south edge -- which also gives the island cantilever the floor connection it needs. Then put a north-facing roof monitor over the void, roughly 5.2 x 0.9 m of vertical glass = 4.7 m2, worth about 2-4% daylight factor with no direct sun. Correct the printed clear height to RF - GF.

### 126. The north bar -- 55% of the ground floor -- has not one window, with 5 m of free setback in front of it

**Severity:** MAJOR

**Numbers:** North bar 18.0 x 6.0 m = 108 m2 per floor. Ground-floor openings in it: 2 doors, 0 windows. Windowless ground-floor rooms: kitchen 26.1 + majlis 26.1 + hall 20.9 + guest WC 3.6 = 76.8 m2 = 39% of the 196 m2 ground floor. Available setback: 5.0 m north, 3.0 m each side.

**Evidence:** The complete opening list in villa_3d.py lines 237-258 contains, for the north bar at ground level, exactly two items: the 1.5 m entrance door and the 1.1 m service door -- and both are sealed by the 100 mm membrane. The 26.1 m2 women's majlis, which on this brief is the single most important room for receiving guests, has no daylight and no view whatever; its only opening is the service door, which also means the service route into the house lands directly in the majlis rather than reaching the dirty kitchen without crossing guest space, contradicting the claim in the module docstring. This is not a constrained-site problem: the north bar has 5.0 m of front setback and 3.0 m to each side boundary. A ground-floor window on the west face of the kitchen looking across a 3.0 m gap at a 2.4 m boundary wall sees sky above 7.6 degrees from a seated eye -- perfectly workable.

**Proposed fix:** Glaze the north bar. North-facing windows onto the arrival court for the kitchen and majlis (north light, no solar gain, the easiest daylight on the plot); a side window or high slot to the west for the kitchen and east for the majlis. Add a validation pass that fails the build if any habitable room in the schedule has zero opening area, rather than discovering it in a render.

### 127. Shading is applied in exactly the three wrong places: over-shaded glazing, unshaded glazing, and fins on a blank wall

**Severity:** MAJOR

**Numbers:** Living glazing: soffit projection 3.0 m over a 3.3 m opening = 0.91x, against a researched 0.6-0.8x -- over-shaded 14-52%. VSC falls from 39.6% unobstructed to 19.8% at the glass, 10.8% mid-room, 7.2% at the back wall. Dining and study south windows: projection 0.00 m, VSC 39.6%, full south sun. West brise-soleil: 9 fins, 7.8 m tall, shading 41.2 m2 of wall containing 0 openings.

**Evidence:** Three separate mismatches with VILLA_RESEARCH.md section 2. (1) The 3.0 m cantilever (line 100) sits at z 4500 over an opening whose head is at 4300, so the shadow angle is set at the sill, not the head: I computed the vertical sky component under a CIE overcast sky for the sky band actually visible -- 30.5 degrees at the glass, 18.0 mid-room, 12.7 at the back wall -- giving VSC 19.8 / 10.8 / 7.2%. BRE treats below 27% as noticeably reduced and below 15% as seriously reduced, so the back half of the living room is already in the serious band before you account for the room's own depth. The cantilever halves the daylight of the one room it was meant to serve. (2) The dining and study windows (line 243) are 2.6 x 2.65 m of unprotected south glass; the research asks for a 1.59-2.12 m projection at 25N+ and there is none -- the first floor above the wings is flush, not cantilevered. (3) The nine west fins (lines 261-263) are 450 deep x 180 wide at 600 centres running z 900-8700, standing off a west wall that contains no opening at ground or first floor. Spacing/depth is 133% against the researched 75% of blade width.

**Proposed fix:** Pull the cantilever soffit back to 2.2 m over the living glazing (0.67x, inside the researched band) and recover the lost depth as a lightweight pergola, which is BUA-excluded in Dubai anyway. Add a 1.8-2.0 m overhang or a fin screen over the dining and study windows. Move the west fins to a west wall that has windows in it -- or, better, put west glazing behind them so the 41 m2 of fin does some work.

### 128. The compression-release sequence is measured door-to-volume and skips the 3.6 m hall that actually sits between them

**Severity:** MAJOR

**Numbers:** Claimed 1:3.0 (2.40 m to 7.30 m). Real sequence: 2.40 m door reveal, 3.60 m hall for 5.3 m of travel, then 7.80 m volume. The release the visitor experiences is 1:2.17, below the researched 1:2.2 threshold. Compression depth: 400 mm.

**Evidence:** build() prints the ratio as (RF - SLAB - GF) / 2400 (lines 312-314) -- the entrance soffit against the tall volume, as if they were adjacent. They are not. The entrance door is at y 23700-24300 and the double-height volume starts at y 18400: between them lie 5.3 m of entrance hall at a 3.60 m clear ceiling. By the time you reach the void you have been in a 3.6 m space for five metres, so the step is 3.60 to 7.80 = 1:2.17, which fails the research's own 'ratio >= 1:2.2 for the release to register'. Separately, VILLA_RESEARCH.md asks for compression at a 2.1-2.4 m soffit that is 1.5-2.0 m wide -- a zone you move through. What is modelled is a 400 mm door reveal: you cross it in one step and it registers as a door head, not as compression.

**Proposed fix:** Build a real compression zone: drop a soffit to 2.4 m over a 2.0-2.5 m deep entry loggia and carry that soffit through the first 2 m of the hall, so the release happens the moment you clear it -- at 2.40 to 7.80 that is 1:3.25 and it lands. Then make the print reflect the sequence rather than the extremes: report the ratio at the actual moment of release.

### 129. 219.9 m2 of garden survives, but as two 106.3 m2 leftover strips rather than one garden

**Severity:** MAJOR

**Numbers:** open ground 463.4 m2 | garden 219.9 m2 = 106.3 + 106.3 + 7.2 | coverage 28.2% (32.2% incl. porch) | terrace 0 m2 | after the fix: one 134 m2 terrace

**Evidence:** Measured against the inside face of the boundary wall (659.4 m2): footprint 196.0 m2 (28.2% coverage, 32.2% if the porch is counted) leaves 463.4 m2 of open ground. That splits as front arrival court 108.3 (porch 28.0 + rill 3.9 + free 76.4), side strips 61.0 (2 x 2.65 x 11.5), light slots 11.0 (1.0 m chasms, not usable), rear zone 283.1. Inside the rear zone the pool shell takes 57.4 and the catch basin 5.8, leaving 219.9 m2 of garden -- comfortably over the research's 150-200 m2 target (VILLA_RESEARCH.md:276-278).

The problem is shape, not quantity. The pool sits dead centre, so the garden is a west lawn of 8.75 x 12.15 = 106.3 m2, an east lawn of 106.3 m2, and a 5.80 x 1.25 = 7.2 m2 south link that the open catch-basin trench interrupts. Neither lawn has a terrace, a tree, or a reason to be. The two halves are effectively disconnected at ground level. And the one designed spectacle -- the raised pool's overflow waterwall -- spills south, so the prime viewing position (the living room, on axis) sees it exactly end-on, the one direction from which a sheet of water reads as nothing; the only place to view it properly is a 1.25 m ledge trapped between the basin and a 2.4 m wall.

**Proposed fix:** Rotating the pool east-west (see the pool finding) consolidates the rear into one 23.3 x 5.75 m = 134 m2 terrace plus a single band of garden behind the pool, instead of two mirror-image strips. Turn the overflow to face north so the waterwall is read from the living room and the terrace across the water -- that is the whole point of raising the pool 700 mm. Then commit the leftover east and west bays to something: the research's 4 x 4 m minimum tree court with 1.0-1.2 m of soil, or the relocated sunken court.

### 130. Neither external door actually penetrates its wall -- a systematic 100 mm skin left on every opening

**Severity:** MAJOR

**Numbers:** wall 400 mm, void overruns the outer face by 300 -> 100 mm skin | affects the guest entrance, the service door, both wing south windows and the 5.6 m structural glazing

**Evidence:** shell() offsets the footprint inward, so a 400 mm wall on the north bar occupies y 23600..24000. The guest entrance void (villa_3d.py:248-249) is cut at NB_Y1 +/- 300 = 23700..24300, removing only the outer 300 mm and leaving a 100 mm skin at 23600..23700. The villa has no front door -- it has a blind niche, confirmed in the GF plan render where the inner wall line runs unbroken across the entrance. The same +/-300 pattern leaves exactly 100 mm on the service door (line 257), on both wings' south windows (line 243) and on the 5.6 m structural glazing to the pool (line 238). Four of the five external opening types in the model are sealed.

This matters beyond the model: the whole scheme's claim is that plan, section and elevation cannot disagree because they are all cut from one solid. Here they agree -- and they all agree on a villa with no openings.

**Proposed fix:** Cut openings about the wall's centreline, or over-run both faces: replace the WG_Y0 +/- 300 / NB_Y1 +/- 300 pattern with (face - WALL - 100) to (face + 100). Better, derive a helper -- cut_opening(face, thickness, inward=True) -- so the wall's inset side is never guessed. Then re-render and check that the inner wall line in the GF plan is actually broken at each door.

### 131. The service entrance opens into the women's majlis, and there is no service gate in the boundary wall

**Severity:** MAJOR

**Numbers:** service door x 20700..21300, y 18700..19800 -> opens into WOMEN'S MAJLIS (26.1 m2) | boundary-wall openings: 2, both in the north wall | service route from street ~25 m across the guest forecourt

**Evidence:** The service door is cut at x 20700..21300, y 18700..19800 (villa_3d.py:257-258) -- through the east wall of the north bar. The room on the other side of that wall is WOMEN'S MAJLIS, 15575..20600 x 18400..23600 (villa_sheets.py:31). Staff carrying deliveries would enter through the most privacy-sensitive room in a Gulf villa. The docstring (villa_3d.py:47-48) claims the service entrance "reach[es] the dirty kitchen without crossing guest or family space"; there is no dirty kitchen in the plan at all, and the door lands in the majlis.

There is also no way to reach that door from the street. The boundary wall has exactly two openings, both in the north wall: the 4.5 m vehicle gate and the 1.2 m pedestrian gate (villa_3d.py:284-285). A delivery has to come in through the vehicle gate at the west end of the forecourt, cross the entire arrival court eastwards past the guest entrance and the rill, then walk 9 m down the 2.65 m east side strip. The three-entrance discipline the research sets out (VILLA_RESEARCH.md:348-354) is not delivered: the villa has one working entrance route, and it is the ceremonial one.

**Proposed fix:** Put a 1.0 m service gate in the east boundary wall at roughly y 20000-21000, giving a direct run down the 2.65 m east strip. Move the service door north to y 21800..22800 so it lands in a service lobby carved off the north bar's east end, with a discreet second door into the majlis for coffee service (the research's explicit requirement) and a route to the kitchen that never crosses the hall. A dirty kitchen of 12-18 m2 needs to appear in the schedule; it currently does not exist.

### 132. The ground floor is 900 mm above the site and no step, ramp or threshold is modelled anywhere

**Severity:** MAJOR

**Numbers:** FFL 900 mm above site, 0 steps modelled | 6 risers at 150 x 350 = 2,100 mm run needed | front court depth 4,650 mm, shared with a 5,000 mm car

**Evidence:** GF = 900 (villa_3d.py:71) against STREET = 0. This is a deliberate and well-sourced move -- the Interlude House privacy device (VILLA_RESEARCH.md:363-365). But nothing in the model resolves it. Between z = 0 and z = 900 outside the footprint there is only the rill kerb (-400..150), the pool shell (-1100..700) and the boundary wall. There are no external steps to the guest entrance, no ramp, no arrival plinth. Section AA confirms it: no ground line, no threshold, the front door hanging 900 mm above nothing.

The research gives the exact geometry it should use: external steps 100-150 rise (120-140 sweet spot), 300-400 going, 2R + G = 600-650, and never a single step in an open terrace (VILLA_RESEARCH.md:367-369). At 140 mm rise that is 6-7 risers and 1.8-2.8 m of run -- which has to be found in the 4.65 m front court, competing with the car.

**Proposed fix:** Model the arrival plinth. Six risers at 150 x 350 gives 900 mm in 2,100 mm of run -- place it as a full-width flight across the entrance bay (x 10500..13500) so it reads as a plinth rather than a stair, landing at y 24000 and starting at 21900... which does not fit in the 4.65 m court alongside a car. That is the real message: the 900 mm lift, the gate standing space and the covered parking are three claims on the same 4.65 m strip, and only two can win. With the cars moved into the north bar the whole forecourt is free for the plinth. Also needed: a level or ramped route somewhere for accessibility, and site falls of 1.5-2% with drainage -- the entire site is currently modelled dead flat at z = 0 with a 2.8 m basement court and a 1.54 m basin pit and no sump.

### 133. The porch canopy is unsupported, floats 900 mm above the drive, walls its own occupants off from the front door, and blocks the gate

**Severity:** MAJOR

**Numbers:** slab 7.0 x 4.0 spanning 6,750 mm off one 250 mm blade | blade base 900 mm above the drive | pedestrian escape 400 mm | slider run-back 250 mm available vs 5,000 needed | 28.0 m2 roofed in the setback

**Evidence:** As coded (villa_3d.py:253-256): a 7.0 x 4.0 m slab at z 4050..4250, two 250 x 250 beams at x 3600 and 6900 spanning z 3800..4050 with nothing beneath them, and a single 250 mm blade wall at x 10250..10500 whose base sits at z = GF = 900 -- i.e. 900 mm above the drive it stands on. The slab therefore spans 6,750 mm off one 250 mm blade, and the blade itself floats. The aerial render shows it clearly.

Three consequences beyond the structure:
1. That blade wall is 4.0 m long and 3.15 m high along the porch's east edge, so on foot you cannot leave the porch toward the front door. The only ways past it are a 400 mm slot between the wall's south end and the villa face, or a 250 mm slot against the boundary wall. A porte-cochere that does not deliver you dry to a door is not a porte-cochere.
2. The canopy stops 250 mm short of the boundary wall. A cantilever slider needs run-back of opening + 500 = 5,000 mm along that face; 250 mm is not a track zone. A pair of inward-swinging leaves needs 2,250 mm of arc plus a 5,000 mm car in 4,650 mm of depth. Neither gate type works.
3. 28.0 m2 of roofed, part-walled RC structure sits wholly inside the 5.0 m front setback, 250 mm off the boundary. A lightweight car shade is commonly permitted there; a 200 mm slab on a 250 mm blade wall is a building, and it takes coverage to 32.2% if counted.

**Proposed fix:** Delete it with the garage move. If a porte-cochere is still wanted for arrival, make it a genuinely lightweight aluminium/steel canopy (research: Dubai excludes a pergola under 3 m high / 20 m2, designed for 1 kN/m2 wind) cantilevered off the villa's north face over the garage apron, with no element within 1.0 m of the boundary and no vertical member in the gate swing or slider run-back. If the RC blade is kept for the elevation, take it down to the drive at z = 0 and put real columns under both beams.

### 134. The entrance gate the brief asks for is not modelled, and the pedestrian gate is off the axis

**Severity:** MINOR

**Numbers:** Pedestrian gate currently 4150 mm off axis. Wall 350 x 2400, 24000 long, 0 piers, 0 joints, 0 coping. Rill 3900 mm long against a claimed uninterrupted axis.

**Evidence:** Lines 210-211 cut two holes in the north boundary wall -- 4500 vehicle and 1200 pedestrian -- with no gate leaves, no piers, no structure. The brief names an entrance gate as a deliverable. The pedestrian opening sits at x 15400-16600, but the axial guest door is at AXIS +/- 750 = 11250-12750, so you enter the plot 4150 mm off the axis and have to jink to reach the axial door -- which breaks the Casa Merida claim in the docstring. The rill only runs y 24400-28300 = 3900 mm, in the front setback, on the opposite side of the house from the pool. The boundary wall itself is a plain 350 x 2400 band running 24 m dead flat with no piers, no movement joints and no coping, against the research's piers at 3.0-4.0 m, joints every 6-8 m and a 100-150 mm coping with a drip. In the south elevation that flat band crops the building at exactly the height where the ground floor should be getting interesting.

**Proposed fix:** Move the pedestrian opening to AXIS +/- 600 (x 11400-12600) so the rill, the gate and the guest door share one line. Model the gate: 4200 mm clear cantilever slider with 4700 mm run-back, 400 x 400 stone piers each side, 5500 mm standing space to the street. Give the wall piers at 3600 c/c on the 600 grid, a movement joint at 7200, and a 150 mm coping with a 6 mm drip groove set 20 mm back. Lower the wall in the south garden to 1800 with a 600 mm open screen above so the elevation is not cropped at 2400.

### 135. Pool is correctly clear of the basement, but the researched section move was silently abandoned

**Severity:** MINOR

**Numbers:** Pool shell north face y 12900; basement south face y 15000. Clear 2,100 mm. No overlap in plan at any level, so the pool is on grade throughout -- not a water-retaining structure on a suspended slab.

**Evidence:** This is the one thing the water design gets right against the parent's checklist, and it is worth saying plainly: the pool bears on ground, so none of research §3's suspended-slab requirements (crack width ≤ 0.2 mm over a habitable space, full tanking, drained cavity with leak detection above an occupied room) are triggered. But it was arrived at by dropping the move the research called "THE SECTION WORTH STEALING" -- "float the pool over part of it," the F.LOT strategy of 3-car parking directly under the pool. The docstring cites F.LOT as design basis finding 2 (lines 24-27) and takes the sunken-court half of it while dropping the pool-over-garage half without saying so. The consequence is traceable: the garage went back up to the ground floor of the north bar (two 2.7 m doors at lines 181-182 in the y 18000-24000 bar), consuming roughly 46 m² of a 196 m² footprint, which is most of why the GFA lands at 407 m² against the 418 m² brief and why the pool ends up 47.5 m² jammed against the house with zero north surround and 8.75 m of dead paving on each flank.

**Proposed fix:** Keep the pool on grade -- reversing this would import the whole suspended-slab water-retaining problem for a 66.5 m³ tank over staff accommodation. But update the docstring to say the F.LOT pool-over-parking move was considered and rejected on the 45°/tanking grounds, rather than implying it was adopted. If the 418 m² target matters more, the alternative is to extend the basement south to y 12000 and put the garage under the pool with a car lift (pit 3.0 × 6.0 m), which research §4 names as the answer when a 3.0 m drop at 1:6 needs 18 m of ramp run that a 29 m plot cannot give.

### 136. No roof drainage: a 90 mm/h storm fills the entire balance volume in under 8 minutes

**Severity:** MINOR

**Numbers:** Parapet-enclosed roof 18.0 × 14.5 m = 261 m². At 90 mm/h that is 23.5 m³/h. Basin usable balance volume 3,045 L, so it fills in 7.8 minutes if roof water reaches it. Open basin catching direct rainfall alone: 5.8 m² × 80 mm = 464 L.

**Evidence:** Lines 154-157 build a continuous 1,100 mm parapet around the whole roof with no outlets, scuppers or overflows cut anywhere. Research §6 is explicit: "provide an overflow because the parapet encloses the area," deck fall 1:80 min. Nothing in the model falls, drains or overflows. Because the basin is an open trough at grade at the low end of the site, whatever the roof and terraces shed will find it, and it is also the balance tank -- so a storm event does not merely flood the garden, it overwhelms the pool's level control and pushes the pool over its own rim, 200 mm below the living-room floor.

**Proposed fix:** Cut two 100 mm outlets per roof bay plus overflow scuppers through the parapet at 50 mm above the outlet invert, falling 1:80 to them, and take rainwater down in the wall thickness to a garden soakaway on the east service strip -- not to the basin. Give the basin its own high-level overflow weir at -100 discharging to that soakaway, and a pumped sump, which research §6 already requires for the sunken court against a 1-in-100-year event.

### 137. The rill never reaches the pool, is 3× too deep, and is a second unacknowledged water system

**Severity:** MINOR

**Numbers:** Rill channel x 11750-12250 (500 mm wide, in band), y 24400-28300 = 3.9 m long, invert -300, surround top +150 → 450 mm deep against a research figure of 50-150 mm (standard 75 mm). Volume at 75-150 mm = 146-293 L. Evaporation 5-10 mm/day = 9.8-19.5 L/day = 5-13% of its own volume per day. Distance from the rill's south end to the pool's north end: 11.5 m of building.

**Evidence:** Lines 199-202 place the rill entirely in the north forecourt between the house face (y 24000) and the rear boundary wall (y 28650). The pool is on the opposite side of the villa. The docstring (lines 29-32) claims the axis is "carried the LONG way by a 500 mm rill (Casa Merida: an uninterrupted perspective from the entrance door to the pool), terminating in the swimming pool proper." The rill stops at the front door and the perspective is interrupted by the entire house -- and, at ground level, by a 5.0 × 4.0 m unguarded floor void, since the sunken-court cut at line 127 removes 5000 × 1400 mm of the north bar's entrance-hall slab and 5000 × 2600 mm of the living-volume slab (both measured). Technically the rill also sits 400 mm outside the basement retaining wall with its invert at -400, so any leak saturates the basement backfill at the entrance, and it needs its own turnover (2-4 h), filtration, dosing, autofill float and winter drain-down that nothing accounts for.

**Proposed fix:** Reduce the channel to 150 mm deep over a black-finished slab and run it at 75 mm of water. Then either carry it through the house on the axis as a glazed floor slot to a spill point at the living-volume face, so the Casa Mérida claim is true, or delete it and say the axis is carried dry by the setting-out grid. Tank the channel independently and set it back 1.0 m from the basement wall. If it stays, give it a float valve -- research: "a mirror that drops 5 mm reads as broken," and this one loses 5-10 mm a day.

### 138. Detail figures out of band: 400 mm shell, 700 mm rim, and a misreported pool-area benchmark

**Severity:** MINOR

**Numbers:** Shell 400 mm against research 250-300 mm (33-60% over). Rim height 700 mm against the research seat-height edge of 450 mm and against any barrier height (1.2 m typical). Pool 47.5 m² = 6.8% of the 696 m² plot; the script prints "research target ~10%" as if that were a miss.

**Evidence:** Line 192-193 offsets the shell 400 mm on all faces and 400 mm under the base -- the same WALL thickness used for the building. That extra 100-150 mm per face is exactly what pushes the shell into the house slab (5800 × 400 mm overlap) and what drives the base to -1100, which is what puts the 45° check against the basement on the knife edge. On the rim: research §6 says lifting the pool 450-900 mm gives "a seat-height edge at 450"; at 700 the edge is too high to sit on and too low to guard, with a 1.4 m drop and 66.5 m³ of water behind it and no barrier modelled anywhere on the plot side. On the print at lines 235-237: research §3 says "~10% of plot" loosely but then gives the operative figure -- "with ~490 m² open, 45-50 m² is right; above ~60 m² the garden disappears." 47.5 m² is squarely inside that band. The script compares against 10% (= 70 m², which the research itself calls too much) and so reports its own compliant pool as short.

**Proposed fix:** Take the shell to 300 mm walls and a 250 mm base: base rises to -950, the 45° clearance requirement against the basement drops from 2,100 to 1,950 mm, and the north face pulls back 100 mm. Drop POOL_TW to +450 if the perimeter-overflow route is taken, recovering the seat edge; if the 700 mm raise is kept for the waterwall, add a compliant barrier or a self-closing gated deck. Change the printed benchmark to "45-50 m² for ~490 m² open (research §3)" so the deliverable stops flagging a correct number as a defect.

### 139. Three entrances open into one undivided room; the service door has no street access

**Severity:** MINOR

**Numbers:** North bar 89.4 m2, 1 room, 4 external doors. East boundary wall openings: 0. Boundary gates in the whole model: 2.

**Evidence:** The docstring claims the Gulf three-entrance discipline -- guest, family via garage, service to the dirty kitchen without crossing guest or family space. In the model the north bar is a single undivided 17.2 x 5.2 m = 89.4 m2 room, and the guest door, both garage doors and the service door all open into it. The whole point of the discipline is separation, and the model delivers three doors into the same space. The service door (line 183-184) sits in the house's east wall at x 20700-21300, opening into the 3.0 m east setback strip -- and there is no opening anywhere in the east boundary wall, so it cannot be reached from the street at all.

**Proposed fix:** Cut a 1.0-1.2 m service gate in the east boundary wall opposite the door (blk(PLOT_W-BW-200, 18700, STREET, PLOT_W+200, 19900, 2200)), and model at least the three partitions that make the claim true: garage/hall, hall/service corridor, and a discreet service door into the majlis, so the coffee route the research names exists in the drawing.

### 140. The brise-soleil shades a blank wall, and the one west-facing opening has no fins

**Severity:** MINOR

**Numbers:** 9 fins, 450 mm deep at 600 mm centres = 133% of blade width vs research 75% (338 mm). Openings behind the fins: 0. West clerestory at z 7800-8450: unshaded.

**Evidence:** The nine fins (lines 187-189) sit at x 2300-2750, y 12800-17780 -- on the west face of the WEST WING. There is no opening anywhere in that wall: the wing's west wall spans x 3000-3400, y 12500-18000 and no V entry touches it. The only west-facing glazing in the model is the clerestory at y 18800-23200, z 7800-8450, in the north bar (line 176-178) -- and the fins do not extend that far north, so the one thing that actually needs shading has none. Fin spacing is also 600 mm at 450 mm projection = 133% of blade width, against the research's ~75% rule (338 mm), so even over glazing they would not close the low western sun.

**Proposed fix:** Move the fin array north to y 18400-23600 to cover the clerestory, or put glazing behind the existing fins. Set spacing to 340 mm (research: 75% of the 450 mm blade), which needs 15 fins over 5.0 m rather than 9. As drawn this is decoration on a blank elevation, and it is the kind of detail that tells an experienced reader the shading was applied as a motif rather than sized.

### 141. Roof plan is cut 100 mm above the parapet, so it renders as an empty pavilion

**Severity:** MINOR

**Numbers:** Cut z = 10400; parapet top z = 10300; miss = 100 mm. All three other plan cuts (BASEMENT -1600, GF 2100, FF 6200) are correctly 1200 above their floors.

**Evidence:** Line 279 cuts the roof plan at RF + SLAB + 1200 = 10400. The parapet top is RF + SLAB + PARAPET = 10300. The cut plane is 100 mm clear of the whole roof, so VILLA_PLAN_ROOF.dxf will contain only the roof pavilion's four walls (9200-12200) floating in white space -- no roof edge, no parapet, no light slots, no pavilion context.

**Proposed fix:** Cut the roof plan at RF + SLAB + 600 = 9800 -- mid-parapet -- so the plan shows the parapet, the slot openings and the pavilion together.

### 142. Courtyard is deeper than researched and undermines two 400 mm walls over a 5.0 m span

**Severity:** MINOR

**Numbers:** Depth 3.70 m below GF vs researched 2.7-3.3 m (0.4-1.0 m over). Court H/W across the 4.0 m dimension = 0.93. Two 400 mm walls undermined over 5.0 m each. No pumped sump or 1-in-100-year drainage modelled, which the research requires for a sunken court.

**Evidence:** CT is 5.0 x 4.0 m (lines 103-104) with the void running -2800 to +1100 = 3.90 m, i.e. 3.70 m below finished ground floor. The research (s.6) gives excavate 2.7-3.3 m, minimum 4 x 4 m, ideally 5-6 m facing the glazing -- the face that would be glazed into the basement's main body is the 5.0 m north face, so that dimension is at the bottom of the ideal band and the depth is over it. The void also passes straight through the LV's north wall (y 17600-18000) and the north bar's south wall (y 18000-18400) for 5.0 m of their length, from the slab soffit at 400 up to 1100, with no beam, transfer or column modelled: two 400 mm walls, each carrying a storey and a roof, left spanning 5.0 m on nothing.

**Proposed fix:** Take the court to 5.0 x 5.0 m and raise the basement floor to -2200 so the excavation is 3.10 m, inside the researched band and inside a normal shoring depth. Model a 400 x 900 mm RC beam over the court on both wall lines, or reduce the opening to 4.0 m and land the walls.

### 143. GFA is overstated by ~20 m2 -- the courtyard hole is counted as ground-floor area

**Severity:** MINOR

**Numbers:** Court double-counted: 13.0 m2 in LV + 7.0 m2 in NB = 20.0 m2. Corrected ground floor 176 m2; GFA 176 + 181 + 30 = 387 m2 = 4,166 sq ft against the 418 m2 / 4,500 sq ft brief -- short by 31 m2 / 334 sq ft, where the print reports a 11 m2 shortfall. Site coverage 176/696 = 25%, not 28%. Basement net 121 m2 against a researched semi-basement schedule of 109 m2 plus circulation.

**Evidence:** Lines 215-223 compute the ground floor as the four block footprints (196 m2) with no deduction for the court, while simultaneously deducting the same 20 m2 from the basement figure. The court removes 5.0 x 2.6 m from the living volume's floor and 5.0 x 1.4 m from the north bar's. The same passage also reports the basement as gross external minus court (162 - 20 = 142) while the wings and bar are measured gross too -- so 'basement 142 m2' is 121 m2 of net internal area.

**Proposed fix:** Subtract the court footprint from whichever floors it passes through in the area routine, and report gross external and net internal consistently. Re-slabbing the north 3.0 m of the living volume (see the 60/40 fix) returns ~24 m2 to the first floor and closes most of the gap.

### 144. Nine west brise-soleil fins shade a wall with no openings in it

**Severity:** MINOR

**Numbers:** 9 fins, 180 x 450 mm at 600 mm centres, 7.80 m tall = slenderness 43:1 on the thin axis. Openings behind them: 0. Fins sit in the 3.0 m side setback, 2.30-2.75 m from the boundary, behind a 2.4 m boundary wall.

**Evidence:** Lines 187-189 stand 9 fins at x 2300-2750 (250 mm clear of the west wing's west face at x 3000), spanning z 900-8700. The research is right that east/west cannot be shaded by horizontals and wants vertical fins -- but the west wing's west wall contains no opening at any level in this model. The fins are 7.80 m tall and 180 mm thick, freestanding, with no return or tie modelled.

**Proposed fix:** Either put windows behind them -- the west wing at first floor is a bedroom with only a south window today -- or delete them and spend the money on the double-height clerestory the volume actually needs. If kept, thicken to 250 mm or tie them back to the slab edges at 5000 and 8700.

### 145. Every entrance door and every wing window is blocked by a 100 mm skin of wall

**Severity:** MINOR

**Numbers:** Residual wall at every +/-300 opening: 100 mm. Affected: 1 guest door, 2 garage doors, 1 service door, 4 wing windows, 1 structural glazing wall.

**Evidence:** The opening voids use a +/-300 mm reach against 400 mm walls (WALL, line 79). Guest entrance (line 179-180): void y 23700-24300 against a wall at y 23600-24000, so 100 mm of wall survives on the inside face. Both garage doors (line 181-182): same +/-300 pattern, same 100 mm skin. Service entrance (line 183-184): void x 20700-21300 against a wall at 20600-21000, 100 mm survives. Wing windows and the ground-floor structural glazing (lines 169-175): void reaches y 12800 against a wall at 12500-12900, 100 mm survives. None of the three entrances the docstring is built around actually penetrate the model, so the plans, sections and elevations the script derives all show sealed openings.

**Proposed fix:** Change the opening voids to reach +/-(WALL + 100) -- i.e. +/-500 against a 400 mm wall -- so every void clears both faces.

### 146. Roof level: clerestory band 400 mm effective, lift overrun breaks the pavilion, pavilion 11 m2 short

**Severity:** MINOR

**Numbers:** Clerestory 400 mm effective vs 450-750 researched. Pavilion net 21.8 m2 vs 33 m2 required, 11.2 m2 short. Lift overrun overshoot 600 mm.

**Evidence:** Three small numeric conflicts at roof level. (1) The clerestory void runs z 7800-8450 (lines 176-178) but the first-floor ceiling is at FF + FF_CH = 8200 and the slab occupies 8200-8700, so the top 250 mm of the 650 mm band is buried in the slab -- 400 mm effective, below the researched 450-750 mm. (2) The roof pavilion is 6.0 x 5.0 = 30 m2 gross (PV, line 106), 5.2 x 4.2 = 21.8 m2 net, against a roof programme of stair head + lift overrun 16 + roof WC 8 + store 9 = 33 m2. (3) The research's 3.6 m lift overrun measured from the pavilion floor at 9200 reaches 12800, but the pavilion top is 9200 + PAV_CH 3000 = 12200 -- the shaft breaks through the pavilion roof by 600 mm.

**Proposed fix:** Set the clerestory head at RF - SLAB - 100 = 8100 and the sill at 7450 for a clear 650 mm; enlarge the pavilion to 7.0 x 5.5; specify a machine-room-less lift with a 2.8 m overrun, or raise PAV_CH to 3.6 m over the shaft only.

### 147. The docstring describes a pool and an axis the code does not build

**Severity:** MINOR

**Numbers:** Stated pool 12.0 x 4.0 = 48 m2; built 5.0 x 9.5 = 48 m2 -- same area, different shape, and 9.5 m is below the research's 12 m lap-swim threshold. Stated rill 'the long way'; built 3.9 m.

**Evidence:** Line 31-32 states the axis terminates 'in the swimming pool proper at 12.0 x 4.0 m'; POOL_X0/POOL_Y0 (lines 93-94) build 5.0 x 9.5 m. Line 29-31 states the axis is 'carried the LONG way by a 500 mm rill'; the rill (lines 199-202) is 3.9 m long on a 29 m plot. Line 24-26 states 'staff, laundry, store and all plant go into a SEMI-BASEMENT', which is true, but line 24 also inherits the research's resolution of the area problem, which depended on the garage going down with them -- it did not, and that is where the 48 m2 ground-floor deficit comes from. Anyone reading the module header will believe the scheme resolves problems it does not resolve.

**Proposed fix:** Rewrite the header against the constants after the plan is fixed, and either build the 12.0 m pool the header claims or change the header. A print-time assertion comparing the header's quoted dimensions to the grid constants would stop this recurring.

### 148. The pool is 9.5 x 5.0 at 1.9:1 -- not the 12.0 x 4.0 the docstring claims, and not the proportion the Alhambra argument requires

**Severity:** MINOR

**Evidence:** POOL_X0/X1 = 9500/14500 and POOL_Y0/Y1 = 3000/12500 give 5.0 x 9.5 m = 47.5 m2 (6.8% of plot). The docstring says 'terminating in the swimming pool proper at 12.0 x 4.0 m' -- the code disagrees with its own design note. Area is right (research: target 48 m2, 45-50 m2 for ~490 m2 open) but proportion is not: 1.9:1 against the research's 12.0 x 4.0 = 3:1 and the Court of the Myrtles' 4.8:1 that finding 3 is built on. At 9.5 m it is also not a lap pool ('Lap swim >=12 m'). The axis it is meant to terminate totals 13.4 m of water on a 29 m plot -- a 3.9 m rill (y 24400-28300) and a 9.5 m pool -- in two pieces separated by 11.5 m of building, with no axial opening modelled between the entry bar and the living volume (solid wall y 17600-18400) so the 'uninterrupted perspective from the entrance door to the pool' cannot be seen.

**Proposed fix:** Take the pool to 12.0 x 4.0 = 48 m2 as the research and the docstring both specify. Running it east-west (see the depth budget) makes the axis terminate ON it rather than run along a stub, which is the Myrtles relationship anyway, and it frees the depth the terrace and forecourt need. Cut an axial opening through y 17600-18400 if the long view is to be claimed.

### 149. Arrival sequence: pedestrian gate 4.0 m off the ceremonial axis, only two gates for three entrances, and every reverse is blind

**Severity:** MINOR

**Evidence:** The pedestrian gate void is x 15400-16600, centre 16000, while the axis, the rill and the front door are all at x=12000 -- a guest arrives 4.0 m off the axis the whole scheme is organised on, and must then edge round the rill's south end through the 400 mm gap at y 24000-24400. Only two gates are cut in the wall, so the service route (door at x=21000, y 18700-19800) shares the guest gate and crosses the guest forecourt, against the research's three-entrance Gulf discipline. The boundary wall is 2,400 mm high hard to both vehicle-gate jambs with no splay or height drop, so a driver reversing out of a garage 4.65 m away sees no footpath until the bumper is at the property line. The front wall is also 2,400 all round, where the research notes Gulf front-setback walls are commonly capped at 1.8-2.0 m, sometimes 1.2-1.5 solid plus screen -- verify. No visitor bay, bin store or condenser/heat-pump yard is provided; the only candidate ground is the 2.65 m service strip.

**Proposed fix:** Move the pedestrian gate onto the axis at x 11250-12750 so the rill starts at the gate (the Casa Merida relationship), add a third gate for service at the east end of the front wall feeding the east strip, and drop the wall to 900 mm for 2.0-2.5 m each side of the vehicle gate for sight lines. Reserve ~12 m2 of the east strip, screened, for condensers and bins.

### 150. West brise-soleil fins project 700 mm into the 3.0 m side setback to shade a blank wall

**Severity:** MINOR

**Evidence:** Nine fins at blk(HX0-700, yy, GF, HX0-250, yy+180, RF) sit x 2300-2750, y 12800-18080, z 900-8700 -- 700 mm proud of the building face at x=3000, inside the 3.0 m side setback (typical permitted projection is 600 mm; verify). They front the west wing (y 12500-18000), which has no west-facing opening in the model at all -- the only west glazing is the clerestory band at x 2900-3600, y 18800-23200 in the entry bar, where there are no fins. So the fins shade masonry and leave the glass unshaded. They also narrow the west circulation route from 2.65 m to 1.95 m over 5.3 m of its length (still above the 1.5-1.8 m minimum, so passable) and start 900 mm above grade with nothing beneath them.

**Proposed fix:** Move the fins north to y 18800-23200 to cover the clerestory they are for, and pull them back to 600 mm projection to stay inside the setback allowance -- or delete them from the west wing and give that wall a deep reveal instead.

### 151. The rill is 3.9 m long, on the opposite side of the house from the pool, 300 mm deep, and unserviced

**Severity:** MINOR

**Numbers:** Rill 0.5 × 3.9 m, invert -300 (research 50-150 mm deep). Volume 0.59 m³, turnover 0.15-0.30 m³/h. Distance rill→pool 21 m through the house. Gate offset from axis 4,000 mm.

**Evidence:** villa_3d.py:273-276 puts the rill at x 11750-12250, y 24400-28300 -- 0.5 × 3.9 m in the entrance forecourt, NORTH of the house. The pool is 21 m south of the entrance door. The Casa Mérida move the docstring cites ("an uninterrupted perspective from the entrance door to the pool") does survive as an alignment -- door at x=12000, hall 8575-15425, living volume 9000-15000, pool 9500-14500, all centred -- but the water axis itself is two disconnected bodies with 12 m of house between them, and the rill points away from the pool toward the street. Depth: the channel solid runs -400→+150 and the void -300→+200, so the invert is 300 mm below garden against the research's 50-150 mm (75 mm standard over a black slab) for a reflecting element. It is a third independent water system -- 0.5 × 3.9 × 0.3 = 0.59 m³ at a 2-4 h turnover -- with no pump, balance point, autofill or drain anywhere in the model. The pedestrian gate (villa_3d.py:285) is at x 15400-16600, 4.0 m off the axis, so the rill is approached obliquely rather than walked along.

**Proposed fix:** Shallow it to a 75 mm film over a black slab with a float valve, and either run it through the house on the axis (a slot in the hall floor, glazed at the living volume) so it genuinely terminates in the pool, or drop it and put the water budget into the north-facing waterwall. Move the pedestrian gate onto x=12000 so the axis starts at the gate.

### 152. The model has no way to express the two tolerances the whole detail depends on

**Severity:** MINOR

**Numbers:** Crest differential 2-6 mm; level tolerance ±0.8 mm over ~29 m of perimeter; slot 19-25 mm; gutter ≥75 × 75 mm; drop pipes 75-100 mm at 1,500 mm centres; bond beam 500-610 mm. Makeup ~0.5-1.0 m³/day.

**Evidence:** POOL_TW = 700.0 is a single constant used simultaneously as the top of the shell and the water level, so the crest set-down that actually makes an overflow work -- the research's 2-6 mm differential, which "not the pump" sets sheet thickness -- is not expressible; nor is the ±0.8 mm level tolerance over the perimeter that the research says "decides whether the pool works", nor the 19-25 mm slot, 75 × 75 mm gutter, 75-100 mm drop pipes at 1.5 m centres, or the 500-610 mm bond beam. A drawing set aimed at a 20-year architect will be read for exactly these. Also absent: any pool cover, so makeup water is 238-475 L/day for the still surface and roughly double that with a 5 m aerated sheet running, in a hot-dry climate.

**Proposed fix:** Add POOL_CREST = POOL_TW - 6 and drive the south wall top off it, so the section shows the differential. Then add a 1:10 pool edge detail as a separate sheet -- crest, granite coping with a 3-6 mm arris, slot, gutter, drop pipe, basin, tank, and a note on the ±0.8 mm laser set-out at pour and at tiling. That one sheet is what makes the pool read as engineered rather than drawn.

### 153. The pool is 1.9:1 -- a rectangle, not a canal, and 2.5 m short of a lap length

**Severity:** MINOR

**Numbers:** 5,000 x 9,500 = 47.5 m2, aspect 1.9:1 (lines 94-95). Research target 12.0 x 4.0 = 3.0:1; Court of the Myrtles 4.8:1; lap swim minimum 12 m. Catch basin at y 1600-2600 sits inside the 3.0 m rear setback, 1,250 mm from the boundary wall inner face.

**Evidence:** VILLA_RESEARCH.md finding 3 is explicit that the earlier 12 x 3.5 running the short way was already 'weaker' than the Alhambra proportion -- 5.0 x 9.5 is weaker still, and it is the one element in the aerial that looks bought rather than designed. It also fails the 12 m lap threshold the same document sets, and it is 5.0 m wide with a 3.0 m cantilever over it, so 60% of its width is in permanent shadow at the head.

**Proposed fix:** The swim length cannot run north-south here -- only 9.5 m exists between the building and the rear setback. Turn it. Lap pool 4,000 x 14,000 at x 4500-18500, y 4500-8500 (56 m2, 3.5:1, 8.0% of plot), running east-west across the garden; extend the on-axis rill 700 mm wide from the entrance straight through the house and out across the terrace so it crosses and terminates in the pool. That is the Alhambra proportion on the only dimension this plot offers, gives a genuine 14 m lap, keeps the axis, and moves the catch basin out of the 45-degree load-spread zone of the boundary footing.

### 154. The car porch is a 7.0 x 4.0 m slab cantilevered 6.75 m off one 250 mm blade wall, and it is too shallow for a car

**Severity:** MINOR

**Numbers:** Canopy x 3500-10500, y 24400-28400 (7.0 x 4.0 m). Only ground support: a 250 mm blade at x 10250-10500 (line 256). Cantilever 6,750 mm. Soffit at z 4050 = 4.05 m above the drive. Depth 4.0 m vs a 4.8-5.0 m car. Gate at the plot line: zero standing space.

**Evidence:** Lines 253-256. The two 'columns' at x 3600 and 6900 are high-level beams (z 3800-4050) that never reach the ground. In the aerial the canopy floats. Separately the front composition -- a 7.0 m canopy hard west, a 4.5 m gate, a 0.5 m rill -- is asymmetric in front of a rigidly symmetric house, so neither reading is committed to.

**Proposed fix:** Deepen to 5,800 mm (y 22600-28400 would breach the setback, so instead y 24000-28400 = 4.4 m plus a 1.4 m open apron, or accept the porch as a 5.8 m canopy oversailing the boundary-wall line if permitted). Support it honestly: two 300 x 800 mm blade walls at x 3500-3800 and 10200-10500 give a 6.4 m simple span, or a 300 x 600 edge beam on three 250 mm columns at 3.2 m centres. Drop the soffit to 2,700 mm above the drive -- 4.05 m is a portico, not a car port, and the extra 1.35 m is the reason the north-west corner looks unresolved. Then pull the gate 5.5 m back from the street to create the standing space the research specifies, and align the canopy's east edge with the west light slot at x 8600 so the front composition has one line in common with the house.

### 155. One 3.65 m² WC, unventilated and on axis from the front door, serves the majlis, dining, study and living room

**Severity:** MINOR

**Numbers:** 1 WC · 3.65 m² · 0 windows, 0 extract shaft · door 1.5 m off the entry axis · 7.0 m from the majlis door

**Evidence:** villa_sheets.py:30 -- GUEST WC 1.825 × 2.0 m = 3.65 m², the only WC on the ground floor. VILLA_RESEARCH.md:319 allows 3.5-5 for a WC serving the majlis, so the size just passes, but it is an internal room with no window and no shaft modelled, and its door (villa_3d.py:198) faces east into the entrance hall 1.5 m off the entry axis, so it is on show from the front door. A 26.1 m² majlis seating 10-14 plus a formal dining room has no second facility.

**Proposed fix:** Move it into a short lobby between the hall and the majlis so it serves guests without being seen from the door, add a mechanical extract riser, and add a second WC in the service zone once the dirty kitchen exists.

### 156. The pool is 5.0 × 9.5 m, not the 12.0 × 4.0 m the code's own docstring claims, and has zero surround on the house side

**Severity:** MINOR

**Numbers:** 9.5 m vs 12.0 m lap minimum · 5.0 m vs 3.5-4.5 m width · pool surround 0 mm vs 1200 min · pool shell overlaps the building wall by 400 mm · water 200 mm below FFL at the glass line

**Evidence:** villa_3d.py:94-95 gives POOL 9500-14500 × 3000-12500 = 5.0 × 9.5 m = 47.5 m². The area target is met, but villa_3d.py:31-32 states "terminating in the swimming pool proper at 12.0 x 4.0 m" and VILLA_RESEARCH.md:187-188 sets 10-14 m × 3.5-4.5 m with lap swim ≥12 m -- the pool is 2.5 m short of a lap length and 1.0 m too wide. Its north edge at y=12500 is exactly the wing façade line, so the pool surround on the house side is 0 mm against the 1.2 m minimum (1.5 m where people walk) at VILLA_RESEARCH.md:307-309; the pool coping solid (villa_3d.py:266-267) actually extends to y=12900 and intersects the living-room wall. Water level is z=+700 with the ground floor at z=+900, so the surface sits 200 mm below the internal floor hard against the glazing, with no threshold, upstand or drainage channel.

**Proposed fix:** Rotate the pool east-west along the south boundary at 12.0 × 4.0 m, pull its north edge back to y=9000 to leave a 3.5 m lounging terrace under the cantilever, and detail a 150 mm upstand with a recessed linear channel at the glazing threshold.

### 157. The printed metrics are recomputed from constants, not measured off the model, so they drift from it

**Severity:** MINOR

**Numbers:** 7.30 printed vs 7.80 actual (−500 mm); 1:3.0 printed vs 1:3.25; GFA 407 printed vs 359 reachable; family living 28.6 printed vs 13.6 actual; coverage 28% printed vs 32.2% with the porch.

**Evidence:** The build() print block (lines 301-315) re-derives every headline number from the same constants that built the model rather than querying the resulting solid, so any modelling error is invisible to it. Three drifts are already live. (a) 'DH volume 7.30 m clear' -- the roof soffit is at RF=8700 and the FFL at 900, so the clear height is 7.80 m and the compression ratio is 1:3.25, not 1:3.0. (b) GFA 407 m² counts the 30 m² roof pavilion and the ~18 m² cantilever box, neither of which can be reached, so reachable GFA is 359 m². (c) villa_sheets.py computes room areas from schedule rectangles that are honestly derived from the partition layout but take no account of what has been cut out of the floor, which is how 'FAMILY LIVING 28.6 m2' gets printed over 13.6 m². The module docstring's claim that areas are 'computed, never typed in' is true and still yields a wrong drawing.

**Proposed fix:** Measure, don't recompute. Take the floor areas from a section of the model at each FFL+50 and intersect the resulting faces with the schedule rectangles; take the clear height from the actual gap between the slab faces on the axis section. Print both the model-measured value and the intended constant, and assert they agree.

### 158. The sunken courtyard is deeper and narrower than the research allows, and nothing connects the basement to the house

**Severity:** MINOR

**Numbers:** 3.90 m deep against a researched 2.7-3.3 m -- 0.60 m over. 4.0 m in the direction facing the glazing against an ideal 5-6 m. Court SVF at its own floor 29%. Far basement corners 7.41 m from the only light source. Basement net 121 m2, printed as 142 m2 (+17%). Stairs, ramps or lifts between -2800 and +900: none.

**Evidence:** CT is 5.0 x 4.0 = 20 m2 (villa_3d.py lines 104-105) cut from BASE_FL to GF + 200, so rim 1100 to floor -2800 = 3.90 m. It clears the 4 x 4 m minimum but the long dimension runs east-west while the glazing that matters faces it north-south across only 4.0 m, so the researched 'ideally 5-6 m facing the glazing' is missed by 1-2 m. Its south edge at y 15400 is the basement's own south wall (BS_Y0 + WALL), so only three of four sides can ever be glazed. The basement itself is a single undivided 17.2 x 8.2 m hollow with no partitions for the staff room, laundry, store, plant or pool plant the brief requires, and no vertical circulation of any kind is modelled -- the pool plant room the research spends a page specifying does not exist. The printed 'basement 142 m2' in build() line 306 is the gross footprint less the court; net of the 400 mm walls it is 121 m2.

**Proposed fix:** Widen the court in the north-south direction to 5.0-5.5 m and lift the basement floor to bring the excavation back to 3.2-3.3 m. Add the stair down (it can share the main stair core) and partition the basement to the researched schedule, keeping the pool plant off any wall shared with the majlis. Report basement area net of walls so it is comparable with the room schedule.

### 159. The ceremonial water axis is 3.9 m of rill terminating at a blank wall, and the gate is 4.0 m off it

**Severity:** MINOR

**Numbers:** rill 3.90 m long, ends 350 mm from a blank wall | ped gate 4,000 mm off axis | crossing gaps 350 / 400 mm | axial water 13.40 m = 46% of 29 m (Myrtles 93%) | pool 5.0 x 9.5 coded vs 12.0 x 4.0 documented | 9.5 m is 2,500 mm short of lap length

**Evidence:** The docstring (villa_3d.py:28-32) invokes Casa Merida's "uninterrupted perspective from the entrance door to the pool" and the Court of the Myrtles, whose pool runs 93% of the court's length. Delivered: the rill is x 11500..12500, y 24400..28300 -- 3.90 m long. Its north end stops 350 mm short of the inner face of the boundary wall, so the axis terminates on blank stone, not on the gate. The pedestrian gate is at x 15400..16600, centre 16000 -- 4,000 mm east of the axis at x 12000. A guest therefore enters off-axis, walks west, and meets the 1.0 m rill broadside with no bridge or crossing modelled; the ways past are a 350 mm gap at its north end or a 400 mm gap at its south end. Total axial water is 3.90 (rill) + 9.50 (pool) = 13.40 m over a 29 m plot = 46%, and the two are separated by 11.5 m of building.

The pool itself contradicts its own documentation: the docstring says "terminating in the swimming pool proper at 12.0 x 4.0 m" and the research targets 12.0 x 4.0 = 48 m2; the code is 5.0 x 9.5 = 47.5 m2. Same area, wrong proportion (1.9:1 against the Myrtles' 4.8:1), and 9.5 m is 2,500 mm short of the 12 m lap-swim threshold.

**Proposed fix:** Move the pedestrian gate onto the axis at x 11400..12600 so the rill runs from the gate threshold to the door, and run it the full 4.25 m to the wall face with the gate reveal as its head. That alone turns 3.9 m of ornament into a real approach. Then, inside, the rotated pool (see the pool finding) gives 13.0 m of lap length and lets the axial rill continue south across the terrace to meet it -- 3.9 + 5.75 + 4.0 = 13.65 m of water read as one continuous move rather than two disconnected pieces. Fix the docstring to match the code, or fix the code to match the docstring; right now the file argues with itself.

### 160. The catch basin is 4.6x oversized and modelled as an open 1.54 m trench in the garden

**Severity:** MINOR

**Numbers:** basin 5.8 x 1.0 x 1.54 m = 8,932 L | required 1,950 L | trade range 1,900-5,700 L | 1,250 mm from the rear wall | invert 1.60 m below top water (rule: 1.0-1.5 m)

**Evidence:** The basin void (villa_3d.py:269-270) is x 9100..14900, y 1600..2600, z -900 to 640 -- 5.8 x 1.0 x 1.54 m = 8,932 L. The research sizes it at 40.7 L/m2, so 48 m2 needs about 1,950 L, with a residential trade range of 1,900-5,700 L (VILLA_RESEARCH.md:212-218). This is 4.6x the requirement and 57% above the top of the trade range. Nothing covers it: as modelled it is an open pit 1.0 m wide and 1.54 m deep sitting 1,250 mm from the inner face of the rear boundary wall, occupying most of the only walkable strip at the pool's south end. Its invert at -900 is 1.60 m below top water, which correctly satisfies the research's 1.0-1.5 m gravity-fill rule, so the level is right and only the volume and the covering are wrong.

**Proposed fix:** Size it honestly: bather displacement 8-10 people at 60-80 L = 500-800, water in transit in a 30 m gutter = 400-800, backwash 500-1,500, plus freeboard and low-level cut-out -- call it 3,000-3,500 L, which the research puts at about 2.0 x 1.2 x 1.6 m deep. Move it under the terrace as a single accessible, ventilated, level-controlled chamber doubling as the balance tank (the research's explicit recommendation for a small plot: one chamber, not two), with the autofill solenoid and float on the tank rather than the pool. Grate or slab over whatever remains in the walking zone. Keep the pipe run to the plant room under 15 m -- worth checking once the basement is re-planned.


---

## Verification verdicts

Each verifier was instructed to REFUTE its finding, defaulting to
`real=false` when uncertain or when the point was taste rather
than defect. Those below survived that test.

### Upheld 1

Half real, and not the half claimed. The alignment charge is refuted by the coordinates. PV x-extents are 9000-15000, identical to LV_X0/LV_X1 (line 89): the pavilion's east and west faces sit exactly on the living-volume wall planes, which run continuously from the basement slab (z=400) to the parapet (z=10300) as the light-slot faces (lines 174-177). PV[3]=24000=NB_Y1: the north face is coplanar with the north external wall of both storeys AND with the parapet's outer face (line 166), giving one unbroken plane from z=400 to z=12200. So three of four faces continue planes below, and in the south elevation the pavilion is the same 6.0 m width on the same two vertical lines as the double-height volume and the cantilever - it reads as the head of the central volume, not a topping. "Over the garage" is simply false: lines 250-256 build a car porch at x 3500-10500, y 24400-28400, outside the footprint in the front setback, and the comment says so explicitly. What is under the pavilion is the stair core, x 13000-14600, y 18700-21900 (lines 232-235), entirely inside PV in x - the only rational place for a roof enclosure. "Tower over the street entrance" is an overstatement by a factor of about five: PV top 12200 vs parapet top 10300 is 1,900 mm of visible mass on a 10.3 m facade, set back 5.0 m from the boundary. The proposed relocation is actively harmful: (16200, 18000, 21000, 23400) sits over the master bed, dressing and en-suite (PARTS_FF), 3 m from the stair with no route to it; its south face on y=18000 is not a wall at all but an internal line of the merged footprint that shell() offsets away (line 149); it gains one true alignment (x=21000=HX1) where the current position has three; and at 25.9 m2 it cuts GFA to 403, or 377 if opened as a pergola, against a brief of 418 that the scheme already misses by 11. What IS real is the second half. There is no pergola anywhere in the file. The bare deck is 219 m2, not 261 (two light slots remove 12.2, the pavilion 30), but it is bare, unshaded, and - the harder defect, which the reviewer only grazes - unreachable: the stair has 16 risers ending at FF (line 232), no opening is cut in the roof slab, and the pavilion void on lines 170-171 spans the full 3000 height so the box has no lid either. Thirty square metres of counted GFA is an open-topped tube with no floor opening. Research line 338 asks for 60-90 m2 of pergola-shaded roof terrace, BUA-excluded in Dubai; line 383 gives 65-70 C deck temperatures, which makes an unshaded roof terrace unusable most of the year. That is a genuine omission against the design's own research basis, not taste. The fix is therefore to keep the pavilion where it is and finish the roof.

**Corrected fix:**

KEEP the pavilion on the axis. Do not move it east. Three changes, all on the existing grid, all inside the current 12.20 m building height.

1. EXTEND THE PAVILION SOUTH TO A WALL LINE, AND CAP IT.
   PV = (9000.0, 18400.0, 15000.0, 24000.0)   # 6.0 x 5.6 = 33.6 m2
   PAV_CH = 2800.0 ; PAV_SLAB = 200.0
   y=18400 is the north face of the cross partitions that run on both floors, PARTS_GF/PARTS_FF (3400,18250,7600,18400) and (16400,18250,20600,18400) - so the fourth face now continues a plane below too, and the enclosure is big enough to hold a stair head. Give it a roof:
     S.append(blk(PV[0], PV[1], RF+SLAB, PV[2], PV[3], RF+SLAB+PAV_CH+PAV_SLAB))
     V.append(blk(PV[0]+250, PV[1]+250, RF+SLAB, PV[2]-250, PV[3]-250, RF+SLAB+PAV_CH))
   Top stays at 9200+2800+200 = 12200, identical to now, so no planning consequence. Door on the axis, x 11400-12600, 1200 x 2400, in the south wall - the roof-terrace door then lands on the same axis as the entrance door, the rill and the pool.
   GFA becomes 196 + 181 + 33.6 = 411 m2 = 4,421 sq ft, closer to the 418 brief than the current 407, and 33.6 m2 matches the research schedule's "Roof ~33 enclosed: stair head + roof pantry/WC + store".

2. MAKE THE ROOF REACHABLE. Second flight FF (5000) to roof deck (9200): rise 4200 = 24 risers at 175, going 290. Dogleg, two 1400-wide flights side by side with a 200 gap, half-landing 3000 x 1400 at z=7100. Footprint x 11800-14800, y 19000-23200 (3.0 x 4.2 m), which sits wholly inside the new pavilion. Cut the matching opening in the roof slab:
     V.append(blk(11800, 19000, RF, 14800, 23200, RF+SLAB))
   Supporting wall RC, not blockwork (research line 160).

3. ADD THE PERGOLA - 89 m2, BUA-excluded, in two rectangles forming one structure:
   A: x 3000-21000, y 9500-12500  = 18.0 x 3.0 = 54.0 m2
   B: x 9000-15000, y 12500-18400 =  6.0 x 5.9 = 35.4 m2
   Band A is exactly 3.0 m deep, sitting over the 3.0 m RC cantilever below (y 9500 = WG_Y0-CANT, y 12500 = WG_Y0), so the pergola line repeats the cantilever line. Band B is exactly the living-volume width and lands on its 400 mm walls at x 9000-9400 and 14600-15000.
   Aluminium, 2.8 m clear under 200 mm beams: soffit 12000, top 12200 - the SAME datum as the new pavilion roof, so the top of the elevation reads as one plane 1.9 m above the 10.30 parapet, with an 18.0 m horizontal line across the full facade width. Design for 1 kN/m2 wind; permit required (>20 m2).
   Posts 250 x 250 (matching parapet and pavilion wall thickness), centres: band A on y=9750 and y=12625 (the latter landing on the wing/LV south wall), x = 3125, 6000, 9200, 12000, 15000, 17800, 20875; band B on x=9200 and x=14800 (both on the LV walls), y = 12625, 15500, 18375. Do not roof the light slots at x 8000-9000 and 15000-16000 - the pergola stops at their faces.
   Result: 219 m2 of deck, 89 m2 shaded (41%), all of it on the south side where the sun is, reached by a real stair, under a pavilion that still marks the axis and still sits on the stair.

### Upheld 2

CONFIRMED -- and the usual refutation ("it's a massing model, material comes later") does not survive contact with the file.

WHAT I CHECKED IN villa_3d.py

1. One solid, no material data. Line 287: `model = (Part() + S) - V`. The only DXF layers are A-CUT and A-ELEV (lines 343-344). There is no cladding zone, no material attribute, no second body. Grep for stone/clad/gap/coping/course/reveal returns nothing but the word "reveals" in a comment on line 80.

2. The 900 raise genuinely has no external expression. Line 155 extrudes the ground slab from the SAME footprint `fp_gf`, GF-SLAB (400) to GF (900). It is coplanar with the wall above, so after the fuse it is not even an edge in the derived elevation. There is also no external step or ramp anywhere: the guest entrance void (line 248) is cut from z=900 to 3300 and the service door (line 257) from 900 to 3300, with grade at STREET=0. The house literally starts at 900 with nothing to climb.

3. The base is worse than "unexpressed" -- it is undefined. The basement (line 129) spans Y 15000-24000, but the wings and living volume sit at Y 12500-18000. Over Y 12500-15000 the ground slab's bottom edge at z=400 has nothing below it. In elevation the south end of the house has a 400 mm bottom line floating above grade.

4. The top is flush. Roof slab (165) and parapet (166) run X 3000-21000 = HX0..HX1, the same plane as the walls below, and the parapet ring is the same face, not set back. The pavilion PV (line 107) has Y1 = 24000 = NB_Y1, so it is flush with the street facade too. The "1100 parapet band" the reviewer mentions does not even draw as a band -- it is one continuous plane from the slab edge to the coping.

5. Nothing lands on a vertical grid. Line 83 claims "one setting-out grid: every wall, slot and opening lands on it." Vertically, floor-to-floor is 4100 (GF_CH 3600 + SLAB 500) and 3700 above (line 73-75); those are not a multiple of any plausible stone course. Opening heads are at 3300, 4000, 4300, 7250, 7900 -- five different datums, no module. So the research's single most-quoted "reads as expensive" device is asserted in a comment, not built.

6. The LOD defence fails on the file's own terms. The model already carries 150 mm partitions (line 185), 180 mm brise-soleil fins (263) and 250 mm parapet insets (167). Its level of detail is ~150 mm, an order of magnitude below the 90 mm plane change and 900 mm plinth that are missing. A model that resolves a 150 mm stud wall but not a 900 mm base is not "too coarse for material" -- it simply skipped the elevation.

WHERE THE REVIEWER OVERSTATES: the south elevation is not blank. There are two full-height 1000 mm light slots (174-177), a 3000 mm cantilever, a roof slab that oversails the wings by 3000, and nine west fins. But all of that is formal relief on one face; the north (street) elevation -- the one that gets judged first -- is an 18.0 x 10.3 m unbroken plane with a single 1.5 x 2.4 m hole in it, and none of the relief anywhere is material.

WHERE THE REVIEWER'S FIX IS WRONG: (a) In a model whose deliverable is a derived line elevation, a cladding change draws NOTHING unless there is a plane change -- the fix must be geometry first, material second. (b) 20 mm shadow gaps at junctions AND 20 mm open joints in the stone field gives one joint size everywhere and therefore no hierarchy. (c) The research's 100-150 mm rebated return applies to the boundary wall (which is currently a plain 350 x 2400 slab with no piers, no movement joints and no coping, lines 279-283), not to a 40 mm ventilated rainscreen. (d) "600 x 1200 courses on the grid" is unbuildable as stated because no vertical grid exists to course to.

**Corrected fix:**

Fix the geometry first so the zones draw in the derived elevations, then hang three materials on them.

STEP 0 -- CREATE THE VERTICAL GRID (costs nothing, changes no area)
GF_CH 3600 -> 3700 and FF_CH 3200 -> 3100. Then FF = 5100, RF stays 8700, overall height stays 10300, GFA stays 407 m2, double-height clear stays 7300. Now every datum lands on a 600 course above a base top of 900: FFL1 900, FFL2 5100 (7 courses), roof soffit 8700 (13 courses).

1. BASE -- 0 to 900 (dark honed basalt)
- 100 mm basalt on a 20 mm bed, finished face 120 mm off the RC, with a 150 mm rebated return at every external corner so no thin edge shows. Runs 0 to 880.
- Continuous 20 x 20 mm shadow gap from 880 to 900 (cut it in the model as a perimeter void; it is the line that makes the plinth read).
- Field above is 90 mm off the RC, so the base stands 30 mm proud -- that step is the drip line as well as the reveal.
- Close the floating edge: extend the basement/podium wall south from BS_Y0 15000 to WG_Y0 12500 under the wings so the base is continuous 0-900 on all four faces.
- Bring the water onto the same datum: POOL_TW 700 -> 900, POOL_FL -700 -> -500 (1.40 m constant depth preserved, still inside the research's 600-900 raise). Pool coping = same basalt, 40 mm thick, 25 mm overhang, 8 mm drip groove set 15 mm back, 15 mm shadow gap to the deck. House plinth and pool coping are then one line at one level.
- Entrance steps, currently absent: 6 risers at 150, going 350 (2R+G = 650), full 6.0 m width across the entrance bay, top tread flush with FFL 900.

2. FIELD -- 900 to 8700 (limestone, 13 courses)
- 40 mm limestone on stainless kerf clips, 30 mm cavity, 20 mm rail: 90 mm off the RC.
- Courses 600 high x 1200 long, 8 mm open joints (NOT 20 -- keep 20 for junctions only, so there are exactly two joint sizes and the hierarchy reads).
- 13 courses from 900 to 8700, joint lines at 1500, 2100, 2700, 3300 ... 8100.
- Re-datum the ground openings onto it: entrance head 3300 (already correct), wing windows sill 1200 / head 3900 (2700 = the full-height door dimension; sill 300 above FFL keeps the seated view), living-room glazing 900 to 4500. First floor: sill 5700, head 7500, with a 600 mm panel and a 20 mm gap between head and soffit.

3. SPINE -- concrete, X 9000 to 15000, ground to pavilion
- Fair-faced concrete held flush with the RC, i.e. 90 mm behind the stone face; 1200 x 2400 shutter panels, cone holes on the same 600 grid.
- 20 x 20 mm shadow gap at every stone/concrete junction (model it: two vertical voids at X 9000 and 15000, z 900 to 10300, on the north face and through the parapet).
- Move the hall partitions so the material joint lands on structure: PARTS_GF/PARTS_FF x-pairs 8425/8575 -> 8925/9075 and 15425/15575 -> 14925/15075 (hall 30.4 m2, kitchen 28.7 m2, majlis 28.7 m2 -- all still inside the research bands). South of the north bar the joint needs no gap: the two 1000 mm light slots already are the joint.

4. TOP -- 8700 to 10300
- Stone stops at 8700 with a 20 x 20 gap; the 1600 mm slab-edge-plus-parapet band above is concrete, face aligned with the spine (90 mm back from the stone). That single set-back turns a flush wall into a legible cornice.
- 60 mm precast coping, 20 mm overhang, 8 mm drip 15 mm back.
- Step the pavilion back: PV = (9000.0, 18000.0, 15000.0, 23000.0). North face pulled back 1000 mm (the same 1000 module as the slots), south face on the NB_Y0 grid line, area unchanged at 30 m2, GFA unchanged at 407 m2.

5. BOUNDARY WALL (the reviewer's own device, applied where the research actually put it)
- 350 mm wall: blockwork core with 100 mm basalt both faces, rebated return at the piers so no thin edge is visible; piers at 3500 centres, movement joint every 7000, 150 mm coping with a drip. Same stone as the plinth, so base, wall and pool coping are one family.

6. MAKE IT VISIBLE IN THE DELIVERABLE
Add layers A-ELEV-BASE (0.50), A-ELEV-STONE (0.35), A-ELEV-CONC (0.35) in new_dxf() and add the three zone outlines as separate shapes, so VILLA_ELEV_*.dxf carries the material zones as line work rather than relying on a note.

### Upheld 3

REAL -- I could not refute it, and checking the model turned up a defect worse than the one alleged.

GEOMETRY AS MODELLED (C:\Users\asdfv\autocad-mcp\villa_3d.py lines 260-263):
    for i in range(9):
        yy = WG_Y0 + 300 + i * 600
        S.append(blk(HX0 - 700, yy, GF, HX0 - 250, yy + 180, RF))
x = 2300..2750 (450 deep), y = yy..yy+180 (180 wide) at 600 c/c, z = 900..8700. Every number in the criticism checks out exactly: clear gap 420, outer face 250 short of the wall plane at x=3000, bottom 900 above grade, top 8700 with parapet top at RF+SLAB+PARAPET = 10300 so 1600 mm blank above, slenderness 7800/180 = 1:43. Full-cutoff HSA = arctan(420/450) = 43.0 deg. Correct.

SOLAR CHECK (my computation, 25N and 29.4N, summer solstice and equinox):
  25N solstice 16:00-18:00 -> alt 35.7/22.5/9.7, az 281.9/286.4/291.5, HSA +11.9/+16.4/+21.5
  25N equinox 16:00-17:00 -> az 256.3/263.5, HSA -13.7/-6.5 (sun SOUTH of west)
  29.4N solstice -> HSA +8.7 to +20.7
The reviewer's stated az 272-285 / alt 30-15 / HSA 0-15 is slightly wrong (summer sun is further north and lower), but the correction does not rescue the fins: 12-21.5 deg is still nowhere near the 43 deg cutoff. The conclusion is latitude-robust across 25-29N.

WHERE I CAN PARTIALLY REFUTE: "the fins block nothing" is an overstatement. The blades' own 180 mm width covers 30% of the elevation at every angle, so total wall shaded = (180 + min(420, 450·tanHSA))/600 = 46% at HSA 12, 52% at 16.4, 60% at 21.5, and 30% at dead-west normal incidence. That is poor, not nil. The reviewer's cutoff arithmetic is right; the rhetoric is not.

THE FATAL FINDING THE REVIEWER MISSED: there is no glazing behind them. The west wall of the west wing (x=3000, y 12500..18000) has zero openings on either floor. I traced every V.append opening cut: the south-face windows are at y=WG_Y0 (12500); the only cut near x=3000 is the clerestory band, x 2900..3600 but y 18800..23200 -- that is the north bar, 1020 mm north of the last fin (fins span y 12800..17780). So nine bespoke concrete blades are shading a blank 400 mm mass wall. The docstring at line 45 justifies them as "West brise-soleil fins -- east/west CANNOT be shaded by horizontals", quoting VILLA_RESEARCH.md line 137. A brise-soleil with no aperture to protect is not a brise-soleil.

AND THEY DO NOT TOUCH THE BUILDING. x 2300..2750 vs the wall face at 3000 (250 gap); z 900..8700 vs grade 0 (900 gap). The GF slab, roof slab and boundary wall all start at x >= 3000 or x <= 350. Nothing in the model connects them. `Part() + S` yields nine free-floating 450x180x7800 solids. That is not a matter of reading "bolted on" -- they are unsupported, and an experienced reviewer will see nine bars hanging in mid-air on ELEV_W. They also project 700 mm into the 3.0 m side setback (SB_SIDE), above the 450-600 mm typically allowed for architectural projections.

TWO ERRORS IN THE PROPOSED FIX, which is why I am supplying my own:
1. "Rotate so the face is normal to azimuth 280" contradicts "55-65 deg from the wall plane". On a north-south wall, a blade at alpha from the wall plane has a face normal at azimuth 90-alpha; at alpha=60 that is 30/210 deg, seventy degrees off 280. A face genuinely normal to 280 needs alpha ~10 deg -- a nearly closed louvre screen. The angle number is roughly right; the stated reason is wrong.
2. Their 300x900 @ 1200 c/c at 60 deg only reaches 51% at HSA 12 and 63% at 21.5 -- barely better than what is there. At alpha=60 the along-wall projection is only 900·cos60 = 450 of a 1200 pitch.
3. Their preferred alternative fails its own test: an 1800 mm recess on a 2400 wide opening casts 383 mm of shadow at HSA 12 = 16% shaded. A recess is an elevation move on a west wall, not a shading move.

The governing truth, which supports the criticism at a deeper level than it argues: the fraction of near-normal west sun a vertical array blocks equals the fraction of the elevation it visually closes. You cannot block low near-normal west sun with an open vertical array. The correct climatic answer for a west facade at 25N -- blank high-mass wall, WWR under 30%, VILLA_RESEARCH.md line 141 -- is what the design already has. The fins are decoration carrying a performance claim they cannot honour, plus a modelling error.

**Corrected fix:**

PRIMARY FIX -- delete lines 260-263 of C:\Users\asdfv\autocad-mcp\villa_3d.py entirely, and delete the claim at line 45 of the docstring. Justification: the wall behind them has no openings, so there is nothing to shade; a blank 400 mm mass wall to the west is already the correct hot-dry answer (VILLA_RESEARCH.md line 141: WWR <30%, thermal mass 230 mm min). This costs nothing, removes nine unsupported floating solids from the model, and clears the 700 mm setback intrusion. Give the west elevation relief with a 20 mm shadow-gapped stone joint grid on the existing setting-out module instead.

SECOND FIX -- if the west elevation must carry a device, it needs an aperture and a working geometry. Both, or neither:

(a) One west aperture, first floor only, 1200 w x 2100 h, sill 450 (seated sill, VILLA_RESEARCH.md line 171):
    V.append(blk(HX0 - 300, 14000, FF + 450, HX0 + WALL + 300, 15200, FF + 2550))

(b) Replace the blades with four angled RC piers. Each 250 mm thick x 1275 mm long on plan, set at 45 deg to the wall, outer tip pointing SOUTH so the face turns to WNW (summer 16:00-18:00 azimuth 282-291). Projects 900 mm out and 900 mm along the wall. Root face flush with the wall plane at x=3000, tip at x=2100 (900 into the setback -- verify the allowance). Centres 1200. Full height, grade z=0 to parapet top z=10300, cast monolithic with the GF slab (400-900), FF slab (4500-5000) and roof slab (8700-9200), with a 20 mm shadow gap at each slab line.

    from build123d import Rot            # add to the import block
    # ============================================================ west piers
    FIN_T, FIN_L, FIN_S = 250.0, 1275.0, 1200.0        # 45 deg: 900 out x 900 along
    TOP = RF + SLAB + PARAPET                          # 10300
    for i in range(4):
        yy = 13100.0 + i * FIN_S                       # root on the wall face
        S.append(Pos(HX0 - 450, yy - 450, TOP / 2) * Rot(0, 0, 45)
                 * Box(FIN_L, FIN_T, TOP))

Performance, shaded fraction = min(1, (900 + 900·tan HSA)/1200):
    summer 16:00 HSA +11.9 -> 91%   (as modelled: 46%)
    summer 17:00 HSA +16.4 -> 97%   (52%)
    summer 18:00 HSA +21.5 -> 100%  (60%)
    equinox dead west HSA 0 -> 75%  (30%)
    equinox 16:00 HSA -13.7 -> 56%  (49%)
The blades tilt south because the summer sun is north of west (az 282-291) and the equinox sun south of it (az 256-264); no open vertical array can cover both, and peak cooling load is the summer case.

Proportion and alignment, which is the reviewer's second complaint: four piers, not nine blades. Grade to parapet top, so they align to the ground line at the bottom and the parapet at the top -- no 900 mm float below, no 1600 mm of blank above. Apparent width seen from due west is 900 + 250·sin45 = 1077 mm at 1200 centres, so the elevation reads 1:9.6 -- a pier order, not a 1:43 louvre. The 250 mm thin dimension is structurally irrelevant once the blade is 1275 deep on its strong axis and restrained at three slab levels.

### Upheld 4

CONFIRMED, though the reviewer got several supporting details wrong.

WHAT I VERIFIED IN C:\Users\asdfv\autocad-mcp\villa_3d.py (the cited lines 210-211 are actually first-floor partitions; the relevant lines are 284-285):

1. No gate is modelled. Lines 284-285 are two `V.append` voids only:
   `V.append(blk(3800, PLOT_D - BW - 200, STREET, 8300, PLOT_D + 200, BH))`   -> 4500 clear vehicle hole
   `V.append(blk(15400, PLOT_D - BW - 200, STREET, 16600, PLOT_D + 200, 2200))` -> 1200 x 2200 pedestrian hole
   Nothing is added back: no leaves, no piers, no track, no lintel. The brief names an entrance gate as a deliverable, so this is a missing deliverable, not just missing detail. The 2200 pedestrian void under a 2400 wall also leaves a 200 mm stone strip spanning 1200 mm with no lintel modelled. The omission matters because this model IS detailed elsewhere at the same scale - 450 x 180 brise-soleil fins at 600 c/c (line 261-263), 250 mm porch beams, 250 mm parapet shadow reveals, the Baja shelf, the rill surround. The wall and gate are the only elements left as pure massing.

2. The pedestrian gate is off the scheme's own axis. Confirmed by arithmetic: pedestrian opening 15400-16600, centre 16000; guest door (line 248) AXIS +/- 750 = 11250-12750, centre 12000. Offset is 4000 mm centre-to-centre (2650 mm between nearest edges). The reviewer's "4150" is edge-to-edge against the wrong edge - the honest number is 4000.

3. This is the sharpest form of the defect, and the reviewer under-stated it. I traced the internal axis and it is CLEAN: the north bar and the living volume are unioned before the inward offset (`shell()`, lines 144-153), so there is no wall on the y=18000 junction across x 9000-15000; the hall partitions sit at 8425-8575 and 15425-15575; the guest WC is at x 8575-10550, west of the axis; the stair is at 13000-14600, east of it; the south structural glazing is x 9200-14800; the pool is 9500-14500, centre 12000. So the Casa Merida axis IS delivered from the guest door all the way to the pool. The only break in it is a 1200 mm hole in the boundary wall sitting 4.0 m off. The scheme's single strongest move is broken at the one point it costs nothing to fix.

4. Wall detail gap is real and is a self-inconsistency with the project's own research. Lines 279-283: `BW, BH = 350.0, 2400.0` and four plain bands. VILLA_RESEARCH.md section 4 (the design's own source) specifies stone wall 300-400 overall, piers at 3.0-4.0 m centres, movement joint every 6-8 m, 100-150 mm coping with a drip. Zero of the four are modelled on 106 m of wall.

WHERE THE REVIEWER IS WRONG, AND WHY THE FIX MUST CHANGE:
- "Lower the wall in the south garden to 1800 with a 600 open screen." Wrong wall. North (y = PLOT_D) is the street - that is where the porch (y 24400-28400), the drive and both gates are. South is the REAR boundary screening the raised pool and garden from the neighbour, and the research allows 2.4 m solid side/rear. Lowering it exposes the one thing that needs the height. The wall that actually breaches the research is the NORTH one: 2400 solid against a researched front limit of 1.8-2.0 m solid.
- "4200 clear cantilever slider with 4700 run-back." Does not fit. West of the vehicle opening there is only 3450 mm to the side-boundary inner face (3800 - 350), and east there is ~2700 mm before the axis. A cantilever slider is geometrically impossible on this frontage; it has to be a bi-parting tracked slider.
- "5500 mm standing space to the street." Not available. The front setback is 5000 mm and the porch already runs to y 28400, 250 mm off the wall face. This should be dropped, not promised.
- "The rill only runs 3900 mm... against a claimed uninterrupted axis." The 3900 mm (y 24400-28300) is simply the depth of a 5.0 m front setback; it is not a defect and cannot be lengthened without moving the house. The docstring claims an uninterrupted PERSPECTIVE, not an uninterrupted water body, and the perspective checks out. But the rill does die 350 mm short of a blank wall 4 m from where you actually enter - that IS worth fixing, as a consequence of (2).
- "Crops the building at exactly the height where the ground floor should be getting interesting" is taste, and it is also just what a boundary wall does in an orthographic elevation.

Net: minor severity is correct. Two hard facts carry it - a named brief deliverable is unmodelled, and the arrival is 4.0 m off the axis the whole scheme is built on.

**Corrected fix:**

All edits are in villa_3d.py, replacing lines 278-285 (the `# boundary` block). Everything lands on the existing 600 mm setting-out grid.

1. PUT THE PEDESTRIAN GATE ON THE AXIS (the fix that actually matters)
   Replace the line-285 void with:
     V.append(blk(11400, PLOT_D - BW - 200, STREET, 12600, PLOT_D + 200, BH))
   1200 clear = AXIS +/- 600, research range 1.0-1.2 m, full 2400 height so no 200 mm stone strip is left spanning unsupported. Gate, rill, guest door, hall, double-height volume, south glazing and pool then share x = 12000 with nothing off it.

2. RE-SITE THE VEHICLE OPENING SO A SLIDER IS POSSIBLE
     V.append(blk(3600, PLOT_D - BW - 200, STREET, 7800, PLOT_D + 200, BH))
   4200 clear (research: 4.0-4.5 comfortable), sitting under the existing porch canopy (x 3500-10500) so cars enter straight into cover.
   Gate type: bi-parting TRACKED slider, two leaves 2250 x 2400 (150 overlap onto each pier), 60 mm frame on the inner face at y 28500-28560. Run-back 2250 per side: west parks 850-3100 (3450 available, 350 spare); east parks 8300-10550, clearing the new axis pier at 10900 by 350. A cantilever slider is not achievable on this frontage - state that rather than draw one.
   Pedestrian leaf: 1200 x 2400 single pivot hung on the west pier.

3. PIERS
   500 x 500, y 28500-29000 (flush with the plot line, 150 proud internally), height 2550 - 150 above the coping so they read as punctuation.
   Gate piers at x 3100-3600, 7800-8300, 10900-11400, 12600-13100.
   Intermediate north piers at 16500-17000 and 20100-20600; corner piers 0-500 and 23500-24000. Resulting bays 2600 / 2600 / 3400 / 3100 / 2900 - all inside the researched 3.0-4.0 m.
   Side and rear walls: piers at 3625 c/c (29 m runs, 8 bays) and 4000 c/c (24 m runs, 6 bays). On the SOUTH wall set the rhythm symmetric about AXIS - either a pier centred on 11750-12250 as a deliberate terminus to the pool axis, or a deliberate gap. Do not let a pier land 250 mm off the axis by accident.

4. WALL SECTION - keep the 2400 datum, add the researched detail
   Change `BW, BH = 350.0, 2400.0` to a 350 x 2250 band plus a 500 x 150 coping (75 overhang each face, 6 x 10 mm drip groove set 20 mm back from both edges), total 2400. Movement joint 20 mm at 7200 c/c, formed inside a pier so it sits in the pier reveal and is invisible.

5. FRONT WALL HEIGHT (the reviewer's point, on the correct wall)
   North wall only: 1650 solid + 150 coping = 1800, then a 600 open stone screen (60 x 60 members at 120 clear) up to the same 2400 datum. Complies with the researched 1.8-2.0 m solid front, keeps one continuous parapet line across all four boundaries, and lets the axis and the rill be glimpsed from the street. Side and rear stay 2400 solid - the rear is what screens the raised pool.

6. RILL TERMINATION (consequence of 1)
   Change the rill north end from PLOT_D - 700 (28300) to 28000, giving a 650 mm stone threshold slab at the gate (28000-28650). Rill then runs 28000 -> 24400 = 3600 exactly on the grid: you step through the gate onto stone, the water starts at your feet and runs to the door reveal.

7. STANDING SPACE - do not fake it
   With a 5.0 m front setback and a 4.0 m deep porch, the researched 5.5-6.0 m is unobtainable. Best available: pull the porch north edge back to 27600 and recess the vehicle gate line to y 27500 with 45 degree splayed returns, giving 1500 mm inside the boundary - enough to clear a car's nose from the carriageway with a fast slider. Note the residual non-compliance explicitly rather than drawing a number that is not there.

### Upheld 5

Confirmed by exhaustive test, not by eye. I rebuilt every `V.append(...)` box in `build()` (C:\Users\asdfv\autocad-mcp\villa_3d.py) and tested each one for intersection with the west wing's west wall volume, x 3000-3400, y 12500-18000, z 900-8700. Result: NONE. The same test on the east wing's east wall (x 20600-21000, same y and z): NONE. For control, the north bar's west wall returns the clerestory, and the west wing's south face returns the two south windows -- so the test is working.

So the facts stand exactly as stated: 9 fins (x 2300-2750, 180 x 450 section, y 12800-17780, z 900-8700) stand in front of 5.5 x 7.8 = 42.9 m2 of wall with zero openings. The clerestory loop at `for xx in (HX0, HX1 - 500)` does span y NB_Y0+800 to NB_Y1-800 = 18800-23200, which is the north bar only. The service entrance is at HX1 +/- 300, y 18700-19800 -- also the north bar, not the east wing. This is not taste: the module docstring claims the fins as a researched move ("West brise-soleil fins - east/west CANNOT be shaded by horizontals"), and VILLA_RESEARCH.md sizes brise-soleil by VSA = arctan(projection / window height). There is no window. The move is internally inconsistent with its own stated basis.

Two details make it worse than the reviewer noticed. The fins start at z=900, floating 900 mm above the garden, so they are not a garden screen either; and they sit 250 mm clear of the wall face, so they read as bolted-on rather than part of the plane. A 7.8 m tall, 180 mm thick blade detached from the wall it shades is also not buildable without ties back at each floor, at which point it is facade, not screen.

Two corrections to the reviewer, neither of which changes the verdict. (1) Every line citation is wrong -- the fins are at lines 260-263 (not 186-189), the clerestory at 245-247 (not 176-178), the service door at 257-258 (not 183). Only the coordinates are right. (2) His proposed fix does not survive arithmetic, so I have not adopted it -- see corrected_fix.

Separately, the check surfaced a corroborating error in the one real clerestory: it is cut at z 7800-8450, but the first-floor ceiling soffit is at RF - SLAB = 8200 (FF 5000 + FF_CH 3200). Its head is buried 250 mm inside the slab/services zone.

**Corrected fix:**

The finding is right; the proposed fix is not. Fix (a), an 1800 deep x 5500 long loggia over two storeys, removes 19.8 m2. GFA falls 407 -> 387 m2 (4,168 sq ft) against a 418 m2 / 4,500 sq ft brief it is already 11 m2 short of, and the west wing drops from 27.5 to 17.6 m2 gross per floor -- that kills both the formal dining room (research: 28-35 m2) and guest 1 (research: 28-35 m2 per guest suite). His "400 mm wall plus 1800 recess gives 2200" also double-counts: glass at x=4800 behind a face at x=3000 is a 1800 reveal, full stop. Fix (b), 3600 x 2400 per storey, is 17.3 m2 of glass on 42.9 m2 = 40% WWR on the WEST wall, against the research's own hot-dry ECBC ceiling of WWR < 30%, and its z levels 1400-3800 / 5600-8000 match neither the scheme's grid nor the 8200 ceiling line, breaking the one-setting-out-grid discipline the design is selling.

The correct answer starts from the fact that the west wall faces a 3.0 m side setback with the boundary wall 2.65 m away. A solid wall there is defensible; the fins are not. So:

A. DELETE the fin loop, lines 260-263. Nothing gets a shading device unless there is glass behind it -- that part of the review is correct and non-negotiable.

B. Cut ONE opening per storey in the west wing's west wall, on the sill and head lines the south elevation already uses, so the grid holds:
   - width 2600 (identical to the south wing windows), centred on the wing: y 13950-16550
   - ground: z 1350-4000 (= GF+450 to GF+3100, the exact south-window sill and head)
   - first:  z 5450-7700 (= FF+450 to FF+2700, likewise)
   - cut x 2700 -> 3900: the 400 wall plus 500 of internal reveal, so the glazing plane sits at x=3900, 900 mm behind the outer face
   Glass 2.6x2.65 + 2.6x2.25 = 12.74 m2 on 42.9 m2 = 29.7% WWR, just inside the 30% cap. Cost is 2.6 m2 of net internal area total (1.3 per storey); GFA measured to the external face is unchanged at 407 m2.
   Code: for z0, z1 in ((GF+450, GF+3100), (FF+450, FF+2700)): V.append(blk(2700, 13950, z0, 3900, 16550, z1))

C. Reinstate the fins ONLY across that glass, inside the reveal, flush with the wall face -- not proud of it: 3 fins, 200 x 900 section, at 700 c/c (centres y 14550 / 15250 / 15950), running x 3000-3900, and stopping at each sill and head (z 1350-4000, 5450-7700) instead of running 900-8700 past the floor slabs. 3x200 + 4x500 = 2600 exactly, symmetric about the wing centreline y=15250.
   Be honest about what this buys: clear 500 over 900 projection closes at HSA arctan(500/900) = 29 deg, barely better than the 31 deg of the fins as drawn. Vertical fins normal to a due-west wall at 25 deg N are weak by physics -- the worst sun (azimuth 250-295, altitude 0-30) sits within ~25 deg of the wall normal and passes straight between them. The fins here are geometry and privacy, not the solar control. The solar control is the 900 reveal plus glass at SHGC 0.27 (research envelope), and if the client will pay for it, one sliding perforated leaf, 2600 wide x storey height, ~40% open, on a top track housed in the reveal head -- the operable-louvre answer the research names for east/west.

D. Do NOT mirror B on the east. That elevation carries the service entrance and faces a 3.0 m service run; the women's majlis (ground) and guest 2 (first) want privacy there. Instead run the clerestory the full length of BOTH side elevations and fix its level. Replace lines 245-247 with:
   for xx in (HX0, HX1 - 500):
       V.append(blk(xx - 100, WG_Y0 + 800, RF - 1150, xx + 600, NB_Y1 - 800, RF - 500))
   That is y 13300-23200 (9.9 m, up from 4.4 m) at z 7550-8200: a 650 mm band (research 450-750), sill 2550 above FFL (research: above 2.1 m), head flush on the 8200 ceiling soffit instead of 250 mm buried in the slab zone. A clerestory at that height throws daylight 4-6 m back, covering the full 5.0 m depth of both wings, and it is the research's own prescription for this exact condition: the top 600 mm of a 7 m elevation sees sky, not the neighbour. Added glass 6.4 m2 per side elevation on 89.7 m2 = 7% WWR.

Net effect on the charge of "two dead elevations": the east becomes an 11.5 m stone wall capped by a continuous sky slot; the west gets the same slot plus one composed 2.6 m opening per storey with a screen that now shades something. GFA unchanged at 407 m2, net internal area -2.6 m2, and neither elevation depends on a device standing in front of nothing.

### Upheld 6

CONFIRMED -- I could not refute it, and the check found a second failure of the same kind.

Arithmetic on villa_3d.py:266-272 (all mm):
- pool shell (line 266): x 9100-14900, y 2600-12900, z -1100..+700
- water void (268): x 9500-14500, y 3000-12500, z -700..+800
- "spill + basin" void (269-270): x 9100-14900, y 1600-2600, z -900..+640

The void's north face is y = POOL_Y0-400 = 2600; the shell's south face is y = POOL_Y0-400 = 2600. Overlap (x,y,z) = (5800, 0.0, 1540) -- exactly the reviewer's figure. I then tested that void against every solid in the file (basement, both shells and slabs, roof, parapet, pavilion, fins, rill, four boundary walls, porch, pool shell, Baja shelf): the list of solids it removes material from is EMPTY. It is an 8.93 m3 cutter that cuts nothing. There is no ground/earth solid anywhere in build(), so it cannot carve a basin out of terrain either.

What is actually built: a closed box, walls 400 thick, continuous flat rim at +700 on all four sides, floor at -700. No crest, no lip, no gutter, no basin, no spill face. Section AA (plane x=12000) cuts the south wall and finds an unbroken 400 mm wall head at +700. So the one move the docstring builds the water design on (lines 17-22) is absent from the geometry. Fatal is the right severity for a scheme whose headline is the waterwall.

Same-cause second defect the reviewer missed: the Baja shelf (line 271-272, x 9500-14500, y 10300-12500, z -700..+400) is strictly inside the water void (y 3000-12500, z -700..+800). Because line 287 unions all solids and then subtracts all voids in one batch, the shelf is annihilated too. Two of the three water elements in the file do not exist in the model.

Two further consequences worth knowing before fixing:
- Even with correct geometry, POOL_EYE (eye 12000,-14000,2600) cannot see the weir. The 2.4 m south boundary wall at y 0-350 occludes everything below z = 2400 - (200/14350)x2250 = 2369 mm at the weir face. The crest at +700 and the whole 1.6 m spill face sit behind the wall.
- The reviewer's own proposed fix does not work. Extending the void to y=2900 cuts the OUTER 300 mm of the wall head and leaves a 100 mm rib of wall at +700 on the pool side, inboard of the 695 crest -- zero head over the rib, so no sheet, plus a 100 mm-wide unbuildable rib. And with no water solid modelled and all three other walls still at +700, a 695 crest means the pool spills on all four sides. The cut must take the full 400 mm wall thickness, and the containment walls must be raised.

**Corrected fix:**

Replace villa_3d.py:266-272 (the "water" block up to and including the Baja shelf). All figures mm; blk(x0,y0,z0,x1,y1,z1).

1. RAISE THE THREE CONTAINMENT WALLS 60 mm ABOVE THE WATER LINE, so a weir can be lower than something.
   S: blk(POOL_X0-400, POOL_Y0-400, POOL_FL-400, POOL_X1+400, POOL_Y1+400, POOL_TW+60)   # rim +760
   Pool now reads as raised 760 with water at 700 -- still inside the researched 450-900 raised-deck band.

2. SPLIT THE WATER VOID so the Baja shelf survives the batched subtraction (nothing left inside a void can ever survive line 287):
   V: blk(POOL_X0, POOL_Y0, POOL_FL, POOL_X1, POOL_Y1-2200, POOL_TW+200)      # y 3000-10300
   V: blk(POOL_X0, POOL_Y1-2201, POOL_TW-300, POOL_X1, POOL_Y1, POOL_TW+200)  # shelf top +400
   Delete the old shelf solid. Residual shell material gives the shelf: 5.0 m wide x 2.2 m front-to-back, top +400 = 300 below water (research: 250-350 deep, 1.8-2.5 m f-t-b). The 1 mm y-overlap avoids a coplanar-cutter sliver.

3. CUT THE WEIR THROUGH THE FULL WALL THICKNESS:
   V: blk(POOL_X0-400, POOL_Y0-400, POOL_TW-5, POOL_X1+400, POOL_Y0+100, POOL_TW+200)
   = x 9100-14900, y 2600-3100, z 695-900. Removes 5800 x 400 x 65 mm of the south wall head. Crest +695, i.e. 5 mm below the water line (research: 2-6 mm) and 65 mm below the containment rim, so the drop is visible in section, not a 5 mm tolerance no drawing can show.

4. GRANITE CAPPING / LEADING ARRIS, 40 x 40 rebate at the outer edge of the crest so the lip reads in section:
   V: blk(POOL_X0-400, POOL_Y0-400, POOL_TW-45, POOL_X1+400, POOL_Y0-360, POOL_TW+200)
   (research: 20-40 mm dense machined granite, 3-6 mm radius on the leading arris; crest wall 200-250 RC.)

5. BUILD THE BASIN ADDITIVELY -- do NOT model an earth solid to cut (a plot-wide ground mass would swamp every derived plan and elevation, and there is no earth in this file). Four boxes, no boolean risk:
   S: blk(POOL_X0-400, POOL_Y0-1600, STREET-BASIN_D-300, POOL_X1+400, POOL_Y0-400, STREET-BASIN_D)  # 300 RC floor, invert -900
   S: blk(POOL_X0-400, POOL_Y0-1600, STREET-BASIN_D, POOL_X1+400, POOL_Y0-1400, STREET)             # 200 upstand to grade
   S: blk(POOL_X0-400, POOL_Y0-1400, STREET-BASIN_D, POOL_X0-200, POOL_Y0-400, STREET)              # west end 200
   S: blk(POOL_X1+200, POOL_Y0-1400, STREET-BASIN_D, POOL_X1+400, POOL_Y0-400, STREET)              # east end 200
   Clear channel 5.40 x 1.00 x 0.90 m deep, open at grade, north face = the pool shell, which is now an exposed 1.595 m spill face from crest +695 down to invert -900.

   Numbers that make it defensible: gross 4,860 L, inside the 1,900-5,700 L residential range; it is the balance tank, one chamber not two, as the research recommends on a small plot. Standing level -600 gives 1,620 L submergence for flooded suction; surge from -600 to -150 gives 2,430 L against the 1,933 L required (47.5 m2 x 40.7 L/m2). Invert 1.60 m below the water line (guide 1.0-1.5 m, deeper only helps gravity fill). Crest 5.8 m long x 40-60 L/min/m = 232-348 L/min on a DEDICATED overflow pump, separate from filtration. 45 deg load-spread: basin face 1.05 m clear of the boundary wall at y 350 and only 300 mm below a 600 mm-deep wall footing -- 300 required, 1,050 available, satisfied.

6. MAKE IT VISIBLE.
   a) POOL_EYE at (12000,-14000,2600) is blind to all of this behind the 2.4 m south wall (occlusion horizon z=2369 at the weir face). Move it inside the plot to a three-quarter view: eye (19000, 1800, 1650), look_at (11000, 8000, 300).
   b) The 65 mm crest step is 0.65 mm at 1:100. Derive a pool detail at 1:20 from the same model -- reuse the AA plane, Plane(origin=(AXIS,0,0), z_dir=(1,0,0), x_dir=(0,1,0)), and crop to y 1000-4000, z -1500..+1200.
   c) If you want the sheet drawn, keep water as a SEPARATE Part added on its own layer (A-WATER), never unioned into the model -- unioned, the section would read the pool as solid. Water plate blk(9500, 3000, 690, 14500, 12500, 700); sheet blk(9100, 2595, -600, 14900, 2600, 695).

7. HOUSEKEEPING: the docstring (lines 19-20) says the pool "overflows one long side". The weir is on the 5.8 m south END, which is correct for section AA and for the camera in 6a -- reword it, or move the weir to the west long face (x 9100-9500) where there is 8.75 m of garden to see it from, and add a section BB. Add a printed check line so this can never silently vanish again, e.g. crest height, spill-face height, sheet width, basin litres vs 40.7 L/m2 -- the current print block reports the pool footprint only, which is why a cutter that removed nothing went unnoticed.

### Upheld 7

CONFIRMED -- I could not refute it. The complete void list in villa_3d.py (lines 238-258, plus the light slots at 174-177 and the interior doors) contains nothing on the x=3000 plane between y=12500 and y=18000:

- 238-241 and 242-244: all at y = WG_Y0 +/- 300 (12200-12800) or the cantilever face -- the SOUTH elevation.
- 245-247 clerestory: x 2900-3600 is indeed in the west plane, but y = NB_Y0+800 to NB_Y1-800 = 18800-23200. That is the north bar, 1,020 mm clear of the northernmost fin. No overlap.
- 248-249 north entrance, 257 east service door.
- The light slot at 174 runs x 8000-9000; it does not cut the wing's own walls, so the wing has no east opening either.

Fins (261-263): x 2300-2750, y 12800-17780, z 900-8700. West wing west face x=3000, y 12500-18000, z 900-8700 = 5.5 x 7.8 = 42.9 m2, zero openings. VILLA_ELEV_W.png confirms it directly: one horizontal clerestory slot at the north-bar end, then the fin comb standing over an unbroken plane. And villa_3d.py's own docstring line 45 states the intent -- "West brise-soleil fins - east/west CANNOT be shaded by horizontals" -- so the file itself declares these as solar-control elements. Geometry and stated intent disagree. That is a defect, not taste.

Two things strengthen it beyond what the reviewer noticed:
(1) The fins would not work even with glass behind them. 180 wide x 450 deep at 600 c/c gives a cutoff of atan(600/450) = 53.1 deg from wall-normal -- they block nothing within 53 deg of due west, i.e. nothing of the actual afternoon sun. So the reviewer's option "put glass behind them" fixes the honesty and leaves the performance failure.
(2) They project 700 mm past the 3.0 m side setback line (x 2300), leaving a 1,950 mm clear side passage to the boundary wall -- worth checking against the local projection limit, commonly 600 mm.

Where I do reject the reviewer: their PROPOSED FIX is worse than the defect. A 4,200 x 2,900 opening is 12.2 m2 of unshaded west glass per level in a hot-arid climate, on the one orientation the design's own research says is unshadeable -- looking at a 2.4 m stone boundary wall 2.65 m away, with a neighbour beyond. It is also badly set out: y 13400-17600 leaves a 400 mm return at the north-bar junction in a 400 mm wall, and a head at GF+3300 (z 4200) leaves only 300 mm to the ground-floor ceiling at 4500 -- no lintel, downstand or blind-pocket zone. Their fix should not be adopted as written.

**Corrected fix:**

Delete the fin array and replace it with a screened west aperture that is orientation-correct. Three edits to villa_3d.py.

1. DELETE lines 260-263 (the 9-fin loop) in full. Nothing in the design depends on them.

2. CUT a west opening in the west wing at both levels, centred on the 5,500 face with equal 1,100 piers (y 13,600-16,900 = 3,300 clear), heads and sills matching the existing south openings so the two elevations share a datum. Insert in the openings block, before the boundary walls:

   # west wing, west face - formal dining below, bedroom 1 above
   V.append(blk(HX0 - 300, 13600, GF + 500,  HX0 + 300, 16900, GF + 3100))
   V.append(blk(HX0 - 300, 13600, FF + 450,  HX0 + 300, 16900, FF + 2700))

   Ground: sill z 1,400 (GF+500), head z 4,000 (GF+3,100), 2,600 high, 8.6 m2 -- leaves a 500 mm lintel/blind-pocket zone to the 4,500 ceiling.
   First: sill z 5,450 (FF+450), head z 7,700 (FF+2,700), 2,250 high, 7.4 m2 -- identical head and sill to the existing first-floor south windows at line 244, so the heads run continuously round the SW corner. Leaves 1,000 mm to the 8,700 ceiling.

3. SET A PERFORATED SCREEN LEAF flush in the outer reveal of each opening -- this is the device that does the work the fins pretended to do, and it is what the fins' material budget should buy. A 100 mm GRC or cut-stone panel at x 2,900-3,000 (flush with the wall face, no setback projection at all), pierced on a 340 mm square grid with 200 x 200 apertures = 34.6% open, so it cuts ~65% of direct beam at EVERY azimuth -- including the 296 deg summer sunset that no reasonable fin depth can catch (a 900 mm slot would need a 1,845 mm fin). It also screens the neighbour 2.0 m away, which fins do not.

   Ground panel: y 13,600-16,900 x z 1,400-4,000, 9 columns x 7 rows of apertures on 340 c/c, margins equalised (~130 mm).
   First panel: y 13,600-16,900 x z 5,450-7,700, 9 columns x 6 rows on 340 c/c.
   Model as one solid minus the aperture grid:
     S.append(blk(HX0 - 100, 13600, GF + 500, HX0, 16900, GF + 3100))
     for r in range(7):
         for c in range(9):
             V.append(blk(HX0 - 150, 13730 + c*340, GF + 630 + r*340,
                          HX0 + 50, 13930 + c*340, GF + 830 + r*340))
   (and the same for the first floor with z base FF + 580 and 6 rows).

   Glazing sits on the inner face of the 400 mm wall, so the screen plus the reveal give a 500 mm deep shadow box -- a real west-facing detail, not applied decoration.

FALLBACK if the client rejects west glass outright on privacy or heat grounds: do step 1 only, leave the wall blind, and delete the words "West brise-soleil fins" from the docstring at line 45 so the stated design basis matches the model. The rooms are already legal and comfortable on their south light alone -- formal dining 22.5 m2 with a 2,600 x 2,650 south window = 31% glazing/floor, bedroom 1 22.5 m2 with 2,600 x 2,250 = 26%. A blind stone flank against a 3.0 m side alley is defensible; a sunscreen over it is not.

RELATED, worth fixing in the same pass: the wing has no opening onto the 1.0 m light slot either (the slot void at line 174 starts at x=8000 and never cuts the wing's east wall at x 7,600-8,000), so both light slots currently light nothing. If they are to earn their place, cut 900 x 2,600 slot windows at x 7,600-8,000, y 15,300-16,200 at both levels -- but note a 1.0 m wide, 9.5 m deep shaft delivers useful light only near midday, so treat it as a spatial device, not a daylight source.

### Upheld 8

The criticism is correct and I could not refute it. I verified the arithmetic directly rather than by eye.

The pool shell (villa_3d.py:266-267) is blk(POOL_X0-400, POOL_Y0-400, POOL_FL-400, ...) = x 9100-14900, y 2600-12900, z -1100 to +700. The "spill + basin" void (269-270) is blk(POOL_X0-400, POOL_Y0-1400, STREET-BASIN_D, POOL_X1+400, POOL_Y0-400, POOL_TW-60) = x 9100-14900, y 1600-2600, z -900 to +640. The void's north face (y = POOL_Y0-400 = 2600) is written with the SAME expression as the shell's outer south face (y = POOL_Y0-400 = 2600), so the two are coincident planes: y-overlap exactly 0 mm, intersection volume 0.000 m3. I then intersected that void against every solid within reach -- pool shell, interior void, south boundary wall (y 0-350), east/west boundary walls (x 0-350 / 23650-24000), the rill solid (y 24400+) -- and got 0.000 m3 in every case. The subtraction is a complete no-op: it removes nothing from anything in the model.

What remains is therefore a sealed 400 mm-walled tank, rim at +700 on all four faces, dead level with the water. No weir, no notch, no crest differential, no basin, no gutter. I confirmed this visually: VILLA_SECTION_AA.png shows a symmetric U at the pool with both legs to identical height and nothing beyond the south leg; VILLA_VIEW_AERIAL_SW.png shows a flat-rimmed tray. Meanwhile villa_sheets.py:72-73 draws a basin rectangle at x 9100-14900, y 1600-2600 and :84-85 letters it "OVERFLOW EDGE + CATCH BASIN" -- geometry that exists only on the sheet. Plan and model disagree on the single element the docstring's design basis (finding 1) is built on, and on the exact failure mode the docstring claims the model eliminates.

I also found a second, related defect in the same block that the reviewer did not mention: the Baja shelf solid at line 271-272 (x 9500-14500, y 10300-12500, z -700 to +400) is entirely contained within the interior void at line 268 (x 9500-14500, y 3000-12500, z -700 to +800). Because the boolean is batched -- model = (Part() + S) - V -- all 12.1 m3 of the shelf is subtracted away. The shelf does not exist either. Two of the three things that distinguish this pool from a rectangular tank are absent from the geometry.

This is not a matter of taste: it is a measurable divergence between the documented design and the built model, and between the model and the drawing derived from it.

**Corrected fix:**

CORRECTED FIX -- villa_3d.py, replace the "water" pool block (lines 266-272). Every dimension below is checked against VILLA_RESEARCH.md §3 and verified by interval arithmetic (no zero-volume booleans, no solid swallowed by a void).

NEW CONSTANTS (replace POOL_TW / POOL_FL / BASIN_D group, lines 96-98):
  POOL_TW  =  700.0   # still-water level = weir crest, 700 above garden
  POOL_OP  =  706.0   # RUNNING surface: 6 mm head over the crest (research 2-6 mm)
  POOL_FL  = -700.0   # 1.40 m constant depth
  COPING   =  800.0   # E + W coping, 100 mm proud of the water -> the rim is NOT level
  WEIR_T   =  200.0   # RC weir wall at the crest (research: 200-250 mm, widening at base)
  SHELF_Y  = 10300.0  # Baja shelf begins (2.2 m long, at the house end)
  SHELF_TW =  400.0   # shelf top -> 300 mm of water over it
  BASIN_CL = 1000.0   # clear north-south width of the catch basin
  BASIN_T  =  200.0   # basin wall / floor thickness
  BASIN_D  =  800.0   # basin invert below terrace -> 1.50 m below the waterline
  BASIN_FL = STREET - BASIN_D                       # -800
  BASIN_X0, BASIN_X1 = POOL_X0 - 100, POOL_X1 + 100 #  9400 .. 14600
  BASIN_Y1 = POOL_Y0 - WEIR_T                       #  2800 (= south face of the weir)
  BASIN_Y0 = BASIN_Y1 - BASIN_CL                    #  1800

GEOMETRY (replace lines 266-272):
  # tank: base slab + walls, everything to the crest. South wall only 200 thick.
  S.append(blk(POOL_X0 - 400, POOL_Y0 - WEIR_T, POOL_FL - 400,
               POOL_X1 + 400, POOL_Y1 + 400,    POOL_TW))
  # E + W coping stand 100 above the water: the crest is a 5.0 m NOTCH between cheeks
  S.append(blk(POOL_X0 - 400, POOL_Y0 - WEIR_T, POOL_TW, POOL_X0,       POOL_Y1, COPING))
  S.append(blk(POOL_X1,       POOL_Y0 - WEIR_T, POOL_TW, POOL_X1 + 400, POOL_Y1, COPING))
  # tank interior cut in TWO so the Baja shelf survives the batched subtraction
  V.append(blk(POOL_X0, POOL_Y0, POOL_FL,  POOL_X1, SHELF_Y, COPING + 100))
  V.append(blk(POOL_X0, SHELF_Y, SHELF_TW, POOL_X1, POOL_Y1, COPING + 100))
  # catch basin: a real chamber - 200 walls, 200 floor, open trough at terrace level
  S.append(blk(BASIN_X0 - BASIN_T, BASIN_Y0 - BASIN_T, BASIN_FL - BASIN_T,
               BASIN_X1 + BASIN_T, BASIN_Y1,           STREET))
  V.append(blk(BASIN_X0, BASIN_Y0, BASIN_FL, BASIN_X1, BASIN_Y1, STREET + 200))
  (delete the old standalone Baja-shelf solid -- it is now the un-excavated tank)

VERIFIED BOOLEAN RESULT (all non-zero where required, zero where required):
  deep interior void  x tank  = 5000 x 7300 x 1400 -> 51.100 m3 removed
  shelf interior void x tank  = 5000 x 2200 x  300 ->  3.300 m3 removed (shelf SURVIVES to +400)
  basin void x basin solid    = 5200 x 1000 x  800 ->  4.160 m3 removed (chamber is hollow)
  basin void x tank           = 0 mm y-overlap     ->  0 m3  (weir wall stays intact: correct)
  interior void x E/W coping  = 0 mm x-overlap     ->  0 m3  (copings stay: correct)
  basin solid x S boundary wall = no overlap, 1.25 m of paving between them

RESULTING SECTION AA PROFILE at x = 12000 (asymmetric, which is the point):
  terrace 0 | basin south wall 200 (y 1600-1800) | trough clear 1000 wide, invert -800
  | weir wall 200 thick rising to crest +700, a 700 mm exposed waterwall face
  | pool floor -700 for 7.3 m | Baja shelf stepping up to +400 for 2.2 m | house.
  E/W copings at +800 do not appear in AA (longitudinal cut) but read in ELEV_S and AERIAL_SW
  as a 5.0 m wide, 100 mm deep notch in the stone rim.

HYDRAULICS (all inside the research bands):
  surface 47.5 m2 (36.5 deep @1.40 + 11.0 shelf @0.30); water volume 54.4 m3
  crest 5.0 m, operating head 6 mm -> Q = 1.84.L.H^1.5 = 4.28 L/s = 257 L/min
    = 51 L/min per metre of weir (research 40-60 L/min/m thin sheet). Dedicated
    overflow pump, separate from filtration (research).
  basin working band -200 (freeboard 200 to paving) to -650 (150 mm low-level cut-out)
    = 5.2 x 1.0 x 0.45 = 2,340 L. Required 40.7 L/m2 x 47.5 = 1,933 L -> 21% margin.
    = 4.3% of pool volume (trade band 3-8%). Serves as balance tank: one chamber, not two.
  invert -800 = 1.50 m below the +700 waterline -> gravity fill and flooded suction (research 1.0-1.5 m).
  Crest flatness spec on the drawing: +-0.8 mm over the full 5.0 m, laser-set at the pour
    and again at tiling; a 25 mm error destroys the effect. 20-40 mm machined granite
    crest stone, 3-6 mm radius on the leading arris.
  DEPARTURE TO DOCUMENT: research wants the basin water 150-300 mm below the crest so
    return water is neither seen nor heard. This scheme deliberately runs a 900 mm fall
    (crest +700 to basin level -200) because the concept is a VISIBLE, AUDIBLE waterwall,
    not a silent vanishing edge. State that on the sheet rather than letting it read as
    a missed rule; a 5.0 m sheet falling 900 mm is roughly 60-65 dBA at 3 m, which is
    why the trough gets a stainless/stone grating flush with the paving (also the
    fall-protection answer for a 1.0 m wide, 800 mm deep open slot beside a pool).

villa_sheets.py -- kill the second source of truth (lines 72-73, 84-85):
  p.box(v3.BASIN_X0, v3.BASIN_Y0, v3.BASIN_X1, v3.BASIN_Y1, "A-FLOR-OTLN")   # catch basin
  p.line(v3.POOL_X0, v3.POOL_Y0, v3.POOL_X1, v3.POOL_Y0, "A-FLOR-OTLN")      # weir crest
  p.text("OVERFLOW WEIR +700 / CATCH BASIN INV -800", (v3.POOL_X0+v3.POOL_X1)/2,
         (v3.BASIN_Y0+v3.BASIN_Y1)/2, 180, "A-ANNO-TEXT", align="MIDDLE_CENTER")
  Drive the rectangle off the model constants, never off re-typed offsets -- that is
  exactly how the plan and the model came apart in the first place.

ORDER OF WORK, per the reviewer: re-run build(), cut Section AA and Elevation S FIRST
and confirm the notch and trough appear, before regenerating any sheet.

DO NOT USE THE REVIEWER'S OWN PROPOSED RANGE. A void of POOL_Y0-1400 -> POOL_Y0+400 at
z -900 -> +640 does bite, but it removes the south wall over y 2600-3000 for the full
z -900 to +640 -- i.e. it opens the tank from below the floor (-700) to 60

### Upheld 9

I could not refute the core of this. The reviewer's geometry checks out, and the defect is not taste -- it is the model contradicting its own written design basis.

VERIFIED FROM villa_3d.py (lines 94-98, 266-272) AND villa_sheets.py (lines 72-73, 84-85):
- Pool water x 9500-14500, y 3000-12500; shell x 9100-14900, y 2600-12900, top +700 (POOL_TW).
- The spill/basin void is blk(POOL_X0-400, POOL_Y0-1400, ..., POOL_X1+400, POOL_Y0-400, ...) = x 9100-14900, y 1600-2600. So the intended weir IS the south face at y=2600, and the basin is the 1,000 mm trough y 1600-2600.
- South boundary wall S.append(blk(0, 0, STREET, PLOT_W, BW=350, BH)) -> inner face y=350. Slot = 2,250 mm; basin 1,000; residual walk 1,250. Reviewer's numbers are exact.
- Every occupied position is north of y=12500: living-volume glazing (WG_Y0=12500), the 3.0 m cantilever soffit (FF_FOOT living rect starts at WG_Y0-CANT=9500), all four bedrooms (FF), the roof pavilion (PV y 19000-24000). A south-facing vertical plane cannot be seen from any point north of it at any height or angle, so no occupant sees the sheet. The 5 m x 700 mm waterwall plays to a 2.25 m slot against a 2.4 m stone wall.

WHY THIS IS A DEFECT AND NOT A JUDGEMENT CALL: the module docstring (lines 18-20) states the design basis as "the pool is RAISED 700 mm above the garden and overflows ONE LONG SIDE as a waterwall into a visible basin," and VILLA_RESEARCH.md section 1(b) buys the 700 mm raise specifically so "the spill face becomes a waterwall into a visible basin." The implementation spills the 5.8 m SHORT END (the void spans the full x width at the y-minimum), not a long side, and into the one face of the pool with no garden in front of it: 2.25 m south, against 8.75 m of open garden east and west. The code does not do what the file says it does, and it picks the worst of the four available faces. Research section 1 also warns that option (a), the perimeter knife-edge, is "the correct answer for a flat walled site"; having spent the +20-40% on a directional overflow instead, aiming it at a wall 2.25 m away lands back in the failure mode the research diagnosed.

WHERE THE REVIEWER IS WRONG (so the fix must be rewritten, and the severity is not "fatal"):
1. The PROPOSED FIX IS UNBUILDABLE. There is no "2,100 mm gap between the pool and the basement." The reviewer used the basement wall (BS_Y0=15000) as the building line, but the ground floor's south face is WG_Y0=12500 (GF_FOOT wings and living volume all span y 12500-18000). The pool shell already runs to y=12900 -- 400 mm PAST the building line and into the house. I confirmed the collision numerically: shell (x 9100-14900, y 2600-12900, z -1100..700) intersects the ground slab (fp_gf extruded z 400..900) over 5,800 x 400 x 300 mm. The gap between pool and house is not 2,100 mm, it is minus 400 mm. Their 37 m2 "unused strip" is under the living-room and wing floor plate. A north weir would discharge into the base of the structural glazing, and making room for it means pushing the pool ~1.5 m south, cutting the boundary-footing clearance from 2,250 to ~750 mm -- below the 0.9-1.5 m the research demands, destroying the second thing the 700 mm raise was bought for.
2. "All of them see the back of the weir: a blank 700 mm rim" is wrong in detail. Water at +700 sits 200 mm BELOW the ground-floor level (GF=900), so from the living room the near rim is under your floor line and the far rim reads as a dead-level knife line, not a blank wall. The composition from the house is fine; what is missing is the waterwall the scheme promised.
3. Their own second-best option ("spill the east long face") is the right answer, and is what the docstring already asked for.

SECONDARY BUG FOUND WHILE CHECKING (neither reviewer nor sheets caught it): the spill/basin void removes nothing. Its y range is 1600-2600 and the shell's south face is y=2600 -- a zero-thickness contact (verified: y-overlap = 0 mm), and no terrain solid exists to cut. So the model has an undifferentiated 400 mm rim at +700 on all four faces; the weir and catch basin exist only as annotation in villa_sheets.py ("OVERFLOW EDGE + CATCH BASIN" plotted at y=2050). The feature is not in the geometry at all.

Verdict: real, but "major" rather than "fatal" -- it is a ~10-line reorientation of one rim, not a re-plan.

**Corrected fix:**

MOVE THE WEIR TO THE WEST LONG FACE. Keep the pool exactly where it is (on the axis, x 9500-14500, y 3000-12500, raised 700). Do NOT move it north as proposed -- the north end already collides with the house.

Why west, not east: the east boundary carries the service entrance (V.append at HX1, y 18700-19800), so the show face should not be the service side; the west face is what the formal dining room's south window (x 4200-6800 at y 12500) looks along; and the plant can then sit in the basement's SW corner, away from the majlis (east, x 15575-20600) and all bedrooms, as the research requires.

1. WEIR WALL (replaces the west rim). Crest line at x=9500, RC 250 mm at the crest (research: 200-250), battering to 400 mm at the base. In code: keep the shell, then void blk(9100, 2600, 400, 9250, 12900, 700) to cut the outer top of the west rim back to a 250 mm crest. Crest length 10.3 m. Granite capping 30 mm, 4 mm radius on the leading arris, crest set 3 mm below the maintained water level (2-6 mm band), laser-set to +/-0.8 mm over the full 10.3 m run.

2. CATCH RILL at the foot of the sheet, echoing the 500 mm entry rill (RILL_W is already 500):
   S.append(blk(8500, 2600, -900, 9100, 12900, 0))
   V.append(blk(8600, 2600, -450, 9100, 12900, 200))
   -> a 500 x 450 mm open rill, 10.3 m long, its east wall being the base of the weir. Water in the rill at -50; the sheet falls 750 mm from crest to rill surface. Dark basalt lining, submerged linear uplight against the wall face.

3. DELETE the south basin void (line 269-270) -- it cuts nothing anyway -- and leave the south rim as plain dead-level coping at +700. Because a one-sided overflow keeps the water at crest level on all four sides, the axial knife line from the family living room down the 9.5 m of water survives intact. The scheme then gets both effects: the vanishing line on the axis from the house, and a 10.3 m x 700 mm waterwall seen and heard from the west lawn, the dining room and the walk from the house to the garden.

4. SOUTH SLOT reverts to what it is actually good for: 2,250 mm of clear ground to the boundary footing (research wants 0.9-1.5 m), plus a 1,250 mm maintenance walk. Delete the "OVERFLOW EDGE + CATCH BASIN" note at villa_sheets.py:84-85 and re-plot it on the west face.

5. HYDRAULICS. Weir 10.3 m x 40-60 L/min/m = 410-620 L/min (25-37 m3/h) on a dedicated vanishing-edge pump, separate from filtration. Balance tank in the basement, not in the visible rill (a fluctuating level must be neither seen nor heard): plant room in the basement SW quadrant, x 3400-8400 / y 15400-19400 = 20 m2 clear at 3.2 m height (research: 12-18 m2, 2.4 m). Tank 2.0 x 1.2 x 1.6 m (3.8 m3) -- the larger of 40.7 L/m2 x 48 m2 = 1,950 L and the honest build-up (bathers 800 + transit ~500 + backwash 1,500 + freeboard). Basement floor at -2800 is 3.5 m below the water line, so gravity fill and flooded suction are automatic. Gravity drain from the rill's north end (x 8850, y 12900) to the plant room's SE corner (8400, 15400) = 2.5 m -- far inside the 15 m pipe-run limit. Floor gully, 1.0 m clear door, mechanical ventilation.

6. GARDEN CHECK after the move: west lawn from the rill edge (x 8500) to the boundary inner face (350) = 8.15 x 12.55 m = 102 m2 clear, so the feature costs the garden nothing.

7. SEPARATELY, FIX THE TWO BUGS THE MOVE EXPOSES:
   (a) The basin void was a no-op (y 1600-2600 abuts the shell face at y=2600, zero overlap) -- the new rill above is a real solid-minus-void, so the geometry finally carries the feature.
   (b) The shell's north face at y=12900 overlaps the ground slab by 5,800 x 400 x 300 mm. Set the shell's north face to POOL_Y1 = 12500 (i.e. shell y 2600-12500, a wet edge tight to the building line with no north rim), or pull the water back to POOL_Y1 = 12100 so the 400 mm rim lands clear of the slab. The former is the better detail: the water then laps the foot of the structural glazing under the 3.0 m cantilever.

### Upheld 10

CONFIRMED -- and the reviewer if anything understates it. Verified against C:\Users\asdfv\autocad-mcp\villa_3d.py and villa_sheets.py.

1. The basement is exactly five lines (villa_3d.py:128-132): a slab, a solid box 3000-21000 x 15000-24000, an interior void inset 400, and the court void. Nothing else in the file references BASE_FL, BS_*, or CT_* except the area printout at :297 and the plan cut at :352. Interior 17.2 x 8.2 = 141.0 m2, less the 20.0 m2 court = 121.0 m2 usable.

2. NO PARTITIONS. PARTS_GF (:187) and PARTS_FF (:205) are built at z=GF and z=FF only. There is no plant room, maid's room, laundry or store anywhere in the model -- and GF and FF are fully allocated to the seven ground rooms and four bedrooms, so "no plant room anywhere" is literally true, not just true of the basement. villa_sheets.py confirms it: SHEETS (:45) contains only A-201 GF and A-202 FF; no basement sheet or schedule exists to compensate. The docstring at :24-27 explicitly claims "staff, laundry, store and all plant go into a SEMI-BASEMENT" and the brief says "Semi-basement for staff and plant." The model asserts this and does not deliver it.

3. NO ACCESS. The stair loop (:232-234) runs GF+0 to GF+16*244 = 4804, i.e. GF to FF. There is no down flight, no ramp, and no door void anywhere in the basement walls. The only thing that breaks the shell is the court void, and that is not access -- it is a 5.0 x 4.0 m hole. Worse: CT_Y0=15400 is coincident with the basement's inner south wall face, and the court is cut to GF+200, so it punches through the ground slab INSIDE the house -- removing 5.0 x 2.6 m of the family living floor and 5.0 x 1.4 m of the entrance hall. The "sunken courtyard lit from outside" cannot exist as sited: apart from the two 1.0 m light slots, every square metre of the basement roof is under the GF footprint.

4. PIPE RUN -- the reviewer's numbers are right and conservative. Basin centre (12000, 2100, -130 by the model's own extents; the reviewer used -450). Orthogonal runs to basement floor -2800: south wall outer face on axis 15.6 m; inner face 16.0 m. But the axis is unusable -- the court sits hard against the south wall across x 9500-14500 -- so the nearest usable basement floor is the west leg corner at 18.5 m, and a real 4 x 5 m room centroid is 23.0 m (west leg) to 28.3 m (NE corner). Even the single most favourable route possible (leave the basin at its NW corner x=9100, run straight north, drop 1.9 m from basin invert) is ~15.1 m before the wall penetration and ~17 m to the filter. Every location breaks the project's own 15 m rule (VILLA_RESEARCH.md:234). Root cause: the overflow weir and basin are at the pool's SOUTH end (y 1600-2600), the far end of the site from the only excavated space, 12.4 m away.

Two corrections to the reviewer's own analysis, which is why the proposed fix must change: (a) the 2.1 x 18 m strip at y 12900-15000 is not garden -- the GF wings and living volume sit on y 12500-18000, so that strip is directly UNDER the house except at the two 1.0 m light slots, so a heat pump there has no outdoor air; (b) 2.1 m gross less two 250 mm walls is ~1.6 m clear, and the research demands 600-800 mm clearance round a 0.9-1.2 m diameter filter plus 1.0 m in front of the panel -- 2.1-2.8 m clear minimum. A plant room does not fit in that strip. And their basement stair at x 13000-14600 lands in the sunken court (court x 9500-14500).

This is a defect against the stated brief and the project's own research, not a matter of taste.

**Corrected fix:**

Three moves. Take the plant to the water rather than the water to the plant, then make the basement a real floor.

A. POOL PLANT VAULT at the south end, beside the balance tank -- not in the basement.
- Clear internal 4.4 x 3.4 m = 15.0 m2 (research 12-18), at x 4200-8600, y 3000-6400. Floor -2000, soffit +400, 2.40 m clear. Sits on the rear setback line (y 3000) and inside the side setback (x > 3000); clear of the pool shell (west face 9100) by 500 mm.
- Roof slab +400 to +700, finished as a raised pool terrace flush with the coping at +700 -- nothing projects above the garden, and it is the research's own "raised deck hides the balance tank and gutter" move rather than a bolt-on.
- Pipe run: basin west wall (9100, 2600, -900) west 0.5 m, north 0.4 m, down 1.1 m = ~2.0 m to the vault wall, ~4 m to the filter. Was 15.6 m to the nearest wall face and 23-28 m to any real room. Suction and return both well inside 15 m; separate overflow pump beside the filtration pump, both in this vault.
- Floor -2000 is 2.70 m below TWL +700 -- flooded suction with ~2.3 m positive head over the basin's operating level (research asks 1.0-1.5 m minimum). Size the return pump for the extra 1.3 m static head.
- Access + air: open areaway x 3200-4200 (1.0 m) x y 3000-6400, grille flush at +700, with a 1.0 m straight flight down, 12 risers @ 166.7 / 280 going = 3.08 m run in the 3.4 m length; 1.0 m clear door. Areaway gives the heat pump outdoor air and acts as the acoustic buffer.
- Floor gully at -2050 to a pumped sump; mechanical ventilation. Nearest habitable room is the formal dining, 7.1 m away and a storey up -- satisfies "never share a wall with a bedroom or the majlis" outright.
- Subdivide the existing basin (5.8 x 1.0 x 1.54 m gross = 8.9 m3, heavily oversized): balance chamber x 9100-11500 sized 2,500-3,500 L per the research build-up, the remainder as weir gutter, autofill solenoid and float on the chamber.

B. BASEMENT ACCESS -- two stairs (121 m2 of occupied basement needs two means of escape).
- Primary service stair, dog-leg, west block under the show kitchen: well x 3400-6000 (2.6 m) x y 19600-23600 (4.0 m); two 1200 mm flights, 22 risers @ 168.2 mm rise / 280 mm going, half-landing at -950 over x 3400-6000 x y 19600-20800. GF slab voided over the whole well and enclosed as a service core with a 900 mm door -- service reaches plant and staff without crossing guest space.
- To hold the kitchen in range, move the kitchen/hall partition east from x 8425/8575 to 10000/10150 and the guest WC to x 10150-12000 x y 18400-20400 (3.7 m2, research 3.5-5). Kitchen becomes 3400-10000 x 18400-23600 = 34.3 m2 less the 10.4 m2 stair = 23.9 m2 (research 20-28). Hall becomes 16.1 m2 -- recover to 18+ by moving the hall/majlis partition east 400 mm, or accept it since the hall is open to the 7.30 m volume.
- Escape stair, east block: straight 1100 mm flight at x 19500-20600 x y 19600-23600, 22 risers, discharging through the existing east service door (x 20700-21300, y 18700-19800) -- which should be relocated anyway, since as modelled it opens directly into the women's majlis.

C. BASEMENT PARTITIONS -- 121 m2 usable: west block 6.1 x 8.2 = 50.0, east block 6.1 x 8.2 = 50.0, north strip x 9500-14500 x y 19400-23600 = 5.0 x 4.2 = 21.0.
- West: service stair 10.4; laundry x 3400-6000 x y 15400-19400 = 10.4 (research 8-12); store x 6150-9500 x y 15400-17600 = 7.4; AHU plant x 6150-9500 x y 17600-19400 = 6.0 (research 6-10) -- under the kitchen, not under the majlis.
- East: maid's room x 14650-17650 x y 20200-23600 = 10.2 (research 9-12) with maid's bath 1.8 x 2.3 = 4.1 (research 3.5-4.5); escape stair 4.4; electrical x 17800-20600 x y 15400-17000 = 4.5 (research 4-6).
- North strip: water tank 5.0 x 2.0 = 10.0 (research 6-10 plus break tank) and general store 5.0 x 2.2 = 11.0.
- 1.1 m corridor round the court linking all of it to both stairs.

D. CONSEQUENT -- the sunken court must be re-sited or renamed. As drawn it is a hole in the family living and entrance hall floors, not an F.LOT pebble court. Either widen the west light slot from 1.0 m to 2.5 m (x 7000-9500, y 15400-18000) and carry it down to -2800 as the real external court, or hold the court where it is and detail it honestly as an internal three-storey light well with a glazed guard at GF -- but then say so, because it stops being what the docstring at :24-27 claims it is.

### Upheld 11

Confirmed against the model, and it is worse than the reviewer states.

1. THE FACE IS BLANK. `FF_FOOT` (villa_3d.py:142) puts the box at x 9000-15000, y 9500-12900 (6.0 x 3.4 m external). Its south wall band is y 9500-9900. No void anywhere in build() intersects that band: the only openings near it are line 238-239 (y 9200-12800, z 1000-4300 -- that is the GROUND floor glazing, entirely below the box soffit at z 4500) and lines 240-241, which are at y 12200-13200 (the reviewer says 12900; the true north edge is WG_Y0+WALL+300 = 13200) -- the box's NORTH wall, opening onto the double-height shaft. So the south face is unbroken from the cantilever soffit (z 4500) to the top of the roof slab (z 9200): 6.0 x 4.7 = 28.2 m2, 34.8 m2 to the parapet top at 10300. The reviewer's 22.2 m2 counts only the wall between slab bands. Visible in VILLA_ELEV_S.png: the two wings each carry two punched openings, the centre bay -- the element over the pool -- is a single empty rectangle.

2. NOTHING OCCUPIES IT, AND NOTHING CAN. The FIRST schedule (villa_sheets.py:36-44) has no room south of y 12900, correct. But the stronger fact is that the box is a DISCONNECTED ISLAND in the first-floor footprint. Adjacency test on the four `FF_FOOT` rects: box vs north bar y-overlap -5100; box vs west wing x-overlap -1000; box vs east wing x-overlap -1000. All disjoint. The 1.0 m light slots (lines 174-177, cut y 12200-18300 through every level) sever it from both wings, and the double-height void separates it from the landing by 5.5 m. There is no bridge, no door, no stair. A-202_FIRST_FLOOR_PLAN.png draws it exactly that way: an unlabelled closed rectangle floating below the plan with no opening in it. It is not an unnamed room, it is a sealed void.

3. YET IT IS COUNTED AS FLOOR AREA. Line 293, `ct = area(LV_X0, WG_Y0-CANT, LV_X1, WG_Y0)` = 18.0 m2, and line 295 folds it into `ff`. So 18 m2 -- 4.4% of the published 407 m2 GFA -- is unreachable sealed space. That is the part that will not survive an area-schedule check.

The available defences fail. "It is a shading canopy" -- a canopy is a slab; this is modelled as a 400 mm-walled enclosure with a floor slab, a ceiling and an internal window, and VILLA_RESEARCH.md:46 asks for the FIRST FLOOR cantilevered over the pool, i.e. inhabited. "The blank plane is deliberate mass" -- a deliberate solid would be modelled solid and would not be counted as GFA. The criticism is not taste; it is a programme, access and area-accounting failure that lands on the most exposed plane in the scheme.

**Corrected fix:**

The reviewer's fix is directionally right but unbuildable as specified, and it skips the real problem (access). Corrections first:

- "Put the master bed head there" is impossible. The master is x 15575-20600 / y 18400-23600 -- on the far side of the 1.0 m light slot at x 15000-16000 and 5.5 m of double-height void. Nothing on the first floor can reach the box without new structure.
- Head at z 8150 is 50 mm below the first-floor ceiling soffit (FF+FF_CH = 8200). No lintel zone, no blind pocket, and it breaks the head datum: the two flanking wing windows on this same elevation (line 244) have heads at FF+2700 = 7700.
- VSA 76 deg is arithmetically right (arctan 2400/600 = 76.0) but it is not shading. At ~25 deg N a south face is self-shaded at midsummer noon (alt 88.5 deg, sun north of the zenith); the hours that matter are equinox (65 deg) and winter (41.5 deg). A 600 mm projection covers 1287 of 2400 mm at equinox noon (54%) and 531 mm in December (22%).
- A 600 mm reveal also eats 600 of the box's 2600 mm internal depth, leaving a 2.0 m room.

CORRECTED FIX (mm, model coordinates in villa_3d.py):

A. ACCESS -- do this first, or the window is decoration on a sealed box. Gallery bridge across the double-height volume, held to one side so the shaft stays a single clear 3.6 x 5.1 m void and the axial view from the entrance hall to the pool glazing is unobstructed:
   - Trim the double-height void (line 162) to x 11000-14600: V.append(blk(11000, WG_Y0, GF+GF_CH, LV_X1-WALL, WG_Y1, FF)).
   - Bridge slab: S.append(blk(9400, 12900, GF+GF_CH, 11000, 18400, FF)) -- 1600 wide, 5500 long, 500 structural zone at z 4500-5000. Its soffit clears the ground-floor glazing head (z 4300) by 200.
   - Guard blades: S.append(blk(9400, 12900, FF, 9500, 18400, FF+1100)) and the mirror at x 10900-11000 -- 1400 clear walking width (research band 1100-1400).
   - Door through the landing's south wall (band y 18000-18400, currently solid across x 8000-16000, so the first floor never sees the double-height volume): V.append(blk(9400, 17900, FF, 11000, 18500, FF+2400)), plus a fixed glazed screen x 11000-14600, z FF+300 to FF+2700 in the same wall so the landing overlooks the shaft.
   - Door into the box: keep lines 240-241 as two flanking internal screens and cut V.append(blk(9400, 12200, FF, 10800, 13200, FF+2400)) on the bridge line.

B. PROGRAMME -- add to FIRST in villa_sheets.py so the area schedule stops lying:
   ("UPPER SITTING", 9400, 9900, 14600, 12500, "habitable") = 5.2 x 2.6 = 13.5 m2
   ("GALLERY BRIDGE", 9500, 12900, 10900, 18400, "circulation") = 1.4 x 5.5 = 7.7 m2
   GFA moves 407 -> 415.8 m2 = 4,476 sq ft, i.e. onto the brief's 418 m2 / 4,500 sq ft rather than away from it.

C. THE FACE -- glaze the south wall wall-to-wall, glass in the wall plane (set back 100 from the outer face, y 9600), so no interior depth is lost:
   V.append(blk(9400, 9000, FF+300, 14600, 10400, FF+2700))
   = 5200 wide x 2400 high, sill z 5300 (300 above FFL), head z 7700 -- the same head datum as the two wing windows, giving one continuous head line across the whole garden elevation, with a 1000 mm wall band above it before the roof slab. NOTE the overshoot: this villa's openings use +/-300 against a 400 mm wall (lines 238, 243, 244, 248, 257), which leaves a 100 mm skin of concrete in every south window and in the front door. Use +/-500 as above.

D. SHADING -- put the device AT the head, not in the reveal. A 200 thick blade at z 7700-7900, full box width x 9000-15000, projecting 900 from the face (y 8600-9500):
   S.append(blk(9000, 8600, 7700, 15000, 9500, 7900))
   Equinox noon (alt 65 deg): 900 x tan 65 = 1930 of 2400 = 80% shaded. Midsummer: face self-shaded. December (41.5 deg): 33%, admitting the low winter sun, which is wanted. Add a 150 x 150 recessed blind pocket at z 7700-7850 behind the glass line for glare off the water.

E. GUARDING AND STRUCTURE -- a 300 sill over a 4.3 m drop to the pool terrace means the glass is the barrier: specify fixed 21.5 mm laminated (10/1.52 PVB/10) designed for 0.74 kN/m at 1100. The reviewer's 750 sill needs the same specification and does not solve guarding on its own. Removing the front wall does not weaken the cantilever -- a wall at a cantilever tip is load, not support; the 3.0 m span is carried by the two 400 side walls acting as downstands off the ground-floor living-volume wall within the 500 slab zone (Eurocode check in VILLA_RESEARCH.md:129-131 needs 215-375 effective depth).

VARIANT if the client will not add GFA: leave the south face open as a 6.0 x 3.4 loggia with a 1100 solid parapet (S.append(blk(9000, 9500, FF, 15000, 9900, FF+1100)) retained, wall above removed to z 8700). Same bridge, same 3.0 m shadow, and the 18 m2 reclassifies as covered terrace instead of sealed GFA.

### Upheld 12

I tried to refute this and could not. The core claim is verifiable in the source and survives.

CONFIRMED against C:\Users\asdfv\autocad-mcp\villa_3d.py:

1. Zero openings face the slots. I traced every void block in build() against the four flank wall bands (x 7600-8000, 9000-9400, 14600-15000, 16000-16400, each y 12500-18000, z 900-8700). Nothing cuts them. The only intersections are a 200 x 300 mm corner wrap where the south structural glazing (lines 238-241, x 9200-14800) runs 200 mm past the LV corners at y 12500-12900 -- a glass corner return, not a window into the slot. The reviewer's "zero openings in any of the four walls facing each slot" is correct.

2. The slot voids cut almost nothing. Because GF_FOOT/FF_FOOT (lines 138-142) already list the wings and the living volume as separate rectangles with 8000/9000 and 15000/16000 gaps, the union footprint and both slabs already exclude the slot. Lines 174-177 therefore only (a) punch two 1.0 x 6.1 m holes in the roof slab and parapet and (b) eat 300 mm into the north bar's south wall. The slots are not a cut through a mass; they are a gap that was already there, plus two holes in a roof plate. That is a stronger version of the reviewer's point than the reviewer made.

3. Cost is real. 2 x 1.0 x 5.5 = 11.0 m2 of footprint per floor (not 12.2 -- the built band is 5.5 m deep, not 6.1), and 4 flanks x 5.5 m x 7.8 m = 172 m2 of extra insulated, stone-clad external envelope in a hot-dry climate, for zero daylight to any room. GFA is currently 407 m2 against a 418 m2 brief, so the area is not spare.

4. The aerial and elevation confirm the reading. In VILLA_VIEW_AERIAL_SW.png the two openings sit in the middle of an otherwise continuous roof plate, stopping short of the front edge. In VILLA_ELEV_S.png the roof-plus-parapet band runs unbroken across the full 18 m, so the three masses do not separate where it counts. The docstring's claim (line 41-42, "AGi Wall House: patios developed three-dimensionally") is not delivered.

5. H/W is 9.9 (z 400 to 10300 over 1000 wide), against the research's ~1.5 courtyard target and its 5-7 m width for H/W 1.1-1.6 on a two-storey villa. At ground level the slot is a dead-end 1.0 m alley reachable from the garden, blind from every window, with no drain modelled.

CORRECTIONS TO THE REVIEWER:
- "Capped by the roof / never open to sky along its length" is FALSE. The void runs z 400-10300, through slab and parapet, so the slot is open to sky over its entire 6.1 m. What is true is that the roof plate continues 2,700 mm south beyond the slot's end (roof y 9500, slot ends y 12200), so the slot never daylights at the roof's front edge -- which is why the aerial reads as punched holes. Same defect, wrong mechanism.
- 12.2 m2/floor is 11.0 m2/floor.
- The proposed fix's own numbers do not hold: x 7800-9600 (centre 8700) and x 15400-17200 (centre 16300) are not symmetric about AXIS = 12000, so they would break the rill/entrance/hall/pool axis the whole scheme is built on; and 15400 leaves a 400 mm orphan strip east of LV_X1 = 15000.

BONUS DEFECT the reviewer missed, same lines: the void runs to WG_Y1 + 300 = 18300, 300 mm into the north bar's 400 mm south wall, leaving a 100 mm-thick, 1.0 m-wide sliver of external wall over the full 9.9 m height at the head of each slot. And the two roof openings are unguarded 4-9 m drops in a walkable roof terrace that otherwise has a 1,100 mm parapet.

**Corrected fix:**

Do not widen the slots inside an 18.0 m band -- there is no room (dining 22.5 and family living 28.6 are already below the research's 28-35 and 35-45). Instead LIFT THE SLOTS OFF THE GROUND, close the ground floor up, and cut the roof through to the front edge. Six edits, all on the existing grid and symmetric about AXIS = 12000.

1. GROUND FLOOR BECOMES ONE CONTINUOUS BAND. In GF_FOOT (line 138) replace the three south rectangles (WW/EW/LV) with one: (HX0, WG_Y0, HX1, WG_Y1) = (3000, 12500, 21000, 18000). Recovers the 11.0 m2. Ground 196 -> 207 m2; GFA 407 -> 418 m2 = 4,500 sq ft, exactly the brief. Coverage 28% -> 30%.

2. CARRY THE SLOT CENTRELINES DOWN AS WALLS. Add to PARTS_GF two 200 mm RC cross walls on the slot centrelines, x 8400-8600 and x 15400-15600, y 12900-18400 -- continuous with the existing kitchen|hall (8425-8575) and hall|majlis (15425-15575) partitions above them, so wall line and slot line are the same line for the full 10.7 m depth. They carry the slot edge and the roof plate, so RC not the 150 mm stud. Resulting ground rooms: formal dining 3400-8400 x 12900-18250 = 26.8 m2 (was 22.5), family living 8600-15400 x 12900-18400 = 37.4 m2 (was 28.6, now inside the 35-45 band and 6.8 m wide against 7.3 m tall, so the double-height volume stops reading as a shaft), study 15600-20600 x 12900-18250 = 26.8 m2 (was 22.5).

3. FIRST-FLOOR SLAB MUST NOW COVER THE GROUND FLOOR. Line 160 extrudes fp_ff; change it to extrude the union of fp_gf and the cantilever rectangle (LV_X0, WG_Y0-CANT, LV_X1, WG_Y0+WALL), otherwise the newly enclosed ground rooms at x 8000-9000 and 15000-16000 are left open to the sky. Keep the double-height void (line 162) at x 9400-14600, leaving a 0.8 m single-height fringe each side -- the research's 60/40 best practice.

4. SLOTS START AT THE FIRST FLOOR AND DIE CLEANLY. Lines 174-177: change z0 from GF - SLAB (400) to GF + GF_CH (4500), and change the north extent from WG_Y1 + 300 (18300) to WG_Y1 (18000) so the north bar keeps its full 400 mm wall instead of a 100 mm sliver. Keep width 1,000 (x 8000-9000, 15000-16000) -- it holds the grid and lands GFA on 418 m2 exactly. Slot floor now at z 5,000, roof soffit 8,700: flank height 3.7 m, H/W 3.7 (was 9.9). Use 1,200 (x 7900-9100 and 14900-16100, still symmetric, still on a 100 module) only if the glass must be cleaned from both faces; that costs 1 m2 of GFA.

5. GLAZE THE TWO FLANKS THAT CAN DELIVER, LEAVE THE OTHER TWO STONE. Clear fixed glazing in the living-volume flanks only: planes at x 9000 and x 15000, y 13300-17600, z 5,300-8,200 (2.9 m high, head 500 below the roof soffit). That drops east and west sky light into the top of the 7.30 m double-height volume from two sides -- the floor-void-linking-storeys move the docstring is after. Bedroom 1 and 2 flanks stay solid stone with a 20 mm shadow gap at the roof junction; they already have 2.6 m south windows, and clear glass 1.0 m from a bedroom window is a privacy failure.

6. CUT THE ROOF TO THE FRONT EDGE AND GUARD IT. Add a roof-only void at each slot: blk(8000, WG_Y0-CANT, RF, 9000, WG_Y0-300, RF+SLAB+PARAPET) and its mirror at 15000-16000 -- i.e. extend the roof cut from y 12200 south to y 9500. Each roof slot then runs 8.5 m to the roof's front edge and breaks the front parapet twice, so the aerial reads as three masses under one stepped roof and the south elevation's roof band is no longer a single unbroken 18 m plate. Frameless 12 mm laminated glass guard, 1,100 mm high, on both long edges of each roof opening (research: roof terrace guarding min 1,100). Slot floor: waterproofing turned up 150 mm at the flanks, 1:80 fall to a 100 mm outlet at the north end, white pebble finish over the membrane per F.LOT, access by roof hatch.

Finally, correct the docstring (line 41-42): at H/W 3.7 these are clerestory light slots and a mass joint, not patios. The scheme's one genuine three-dimensional patio is the 5.0 x 4.0 m sunken court at H/W 0.8 -- claim that one and stop claiming these.

### Upheld 13

REAL -- confirmed by boolean probe of the actual model (built villa_3d.build(), intersected the solid with probe boxes and measured volumes), not by reading the source. The core claim survives; two of the reviewer's sub-numbers are wrong, and both wrong in the design's favour -- the truth is worse.

WHAT THE MODEL ACTUALLY CONTAINS
villa_3d.py:132 subtracts blk(9500, 15400, -2800, 14500, 19400, +1100) after every solid is unioned (villa_3d.py:287, `model = (Part() + S) - V`), so it cuts the ground slab built at villa_3d.py:155 (z 400-900). Measured slab remaining inside the 20.00 m² court footprint: **0.00 m²**. The whole 20 m² of ground floor is gone.

Per scheduled room (schedule from villa_sheets.py:27-35; measured as slab volume ÷ 500 mm):
  FAMILY LIVING  scheduled 28.6 → present **13.6**, missing **15.0** (not 13.0; the schedule rectangle runs to y 18400, so the court eats 5.0 × 3.0 m, 52% of the room)
  GUEST WC       scheduled  3.6 → present **2.7**, missing **0.9** (reviewer correct -- a 900 × 1000 hole in the WC floor)
  ENTRANCE HALL  scheduled 20.9 → present **20.9**, missing **0.0** -- the reviewer's "7.0 m² out of the entrance hall" is WRONG. The hall rectangle is y 20550-23600, north of the court.
  Balance 4.1 m² comes out of unlabelled circulation: x 10550-14500 × y 18400-19400.

THAT BALANCE IS THE WORSE FINDING. That strip is the only route from the entrance hall/stair foot into the family living room (the living volume is walled x 9000-9400 and 14600-15000, glazed south). Measured slab on the 3.95 m wide direct route: **0.00 m²**. The sole surviving connection is a **925 mm wide ledge at x 14500-15425 (0.93 m² of slab)**, unguarded, beside a 3.7 m drop. Stair treads 0-3 (villa_3d.py:232-234, y 18700-19380) have 0.009 m³ of support each -- a 100 mm sliver; four treads float over the hole.

DAYLIGHT: confirmed zero. Roof slab (villa_3d.py:165, x 3000-21000 × y 9500-24000 × z 8700-9200) sits over the court footprint with **10.00 m³** of solid = 100% coverage. Nothing cuts it there (the light slots at villa_3d.py:174-177 are x 8000-9000 and 15000-16000). The reviewer's z for the first-floor slab is wrong (it is 4500-5000, not 3600-4100) but the conclusion holds: 2.98 m³ of it covers the north 1.4 m strip. The court sees no sky.

IT IS NOT EVEN A COURT. Probed the perimeter at basement level: west face 0.000 m³, east face 0.000 m³, north face 0.000 m³. There is no enclosing wall and no glazing -- the "court" is simply the basement's open interior extended up through the ground slab. The family living room opens directly, without separation, into the staff/plant volume.

AND: the whole 142 m² basement interior contains **0.000 m³** of solid -- no stair, no lift, no partitions, no plant-room walls. As modelled the hole in the living room floor is the *only* access to the semi-basement.

KNOCK-ON TO THE HEADLINE FIGURES: villa_3d.py:289-295 sums gross rectangles for `gf`, so the printed "ground 196.0 / GFA 407 m² / 4,381 sq ft" does not deduct the hole. True GFA is **387 m² / 4,166 sq ft**, 31 m² under the 418 m² brief. A-201 prints "FAMILY LIVING 28.6 m2" over a floor that is half absent, because derive() cuts plans at GF+1200 = z 2100, above the void top of 1100.

WHAT SURVIVES REFUTATION IN THE DESIGN'S FAVOUR: excavation depth 2.80 m garden-to-invert is correctly inside the research's 2.7-3.3 m; basement clear height is a generous 3.20 m; and the reviewer's storm-water narrative is overstated -- the court is internal and fully roofed, 2.9 m from the pool's north edge, not "12 m downhill", so rain does not fall into it. The sump requirement is still right, but for the reason that the basement is 3.5 m below the pool water line, not for the reason given.

I cannot refute this. The living room and the route to it have no floor; the one move that was supposed to make the basement a served space delivers zero daylight; and the drawings assert a floor the model does not have.

**Corrected fix:**

Six moves. The reviewer's "make it an atrium with a roof opening" half should be rejected -- a sky-to-basement shaft here is z 10300 → -2800 = 13.1 m deep, H/W 3.3 at 4 m wide: a solar chimney into a hot-dry basement that still eats the living room. The daylight must come from outside the two-storey mass, where the depth is only 2.80 m.

1. STOP THE VOID AT THE SLAB SOFFIT. villa_3d.py:132, change the void top from `GF + 200` (z 1100) to `GF - SLAB` (z 400). Restores FAMILY LIVING to 28.6 m², GUEST WC to 3.65 m², the 3.95 m wide hall→living route, and bearing under stair treads 0-3. Nothing else in the model needs to move for this.

2. PUT THE DAYLIGHT IN THE LIGHT SLOTS -- the design's own AGi Wall House move, already cut through every level and already uncapped over the basement (probed: 0.000 m³ of slab under both slots). Widen each from 1,000 to 2,400 mm:
   WEST WELL  x 6600-9000, y 15400-20000  = 2.4 × 4.6 = 11.04 m²
   EAST WELL  x 15000-17400, y 15400-18300 = 2.4 × 2.9 =  6.96 m²
   Total 18.0 m². H/W at grade = 2800/2400 = 1.17 (research 1.0-1.5 hot-dry); excavation 2.80 m (research 2.7-3.3). The east well stops at y 18300 deliberately -- extending it north would take 3.24 m² off the 6.48 m² master dressing.
   Replace villa_3d.py:104-105 with these two rectangles and cut them, in place of the single court void, from BASE_FL to RF + SLAB + PARAPET (z -2800 → 10300) so they stay open to sky through every level.
   Area cost: FORMAL DINING 22.5 → 19.7; STUDY 22.5 → 19.7; SHOW KITCHEN 26.1 → 23.2 (all inside their research bands); BEDROOM 1 22.5 → 19.7; BEDROOM 2 22.5 → 19.7; BEDROOM 3 26.1 → 23.2. GFA lands at ~390 m² -- better than the model's true 387 m², and honest this time.

3. GLAZE AND FINISH. Basement clear height is 3.20 m (floor -2800, slab soffit +400). Full-height glazing to each well: 3,000 mm high on a 150 mm upstand, thermally broken, set back 100 mm behind the retaining face, with a 250 × 3,000 mm slot channel drain in front. Well walls in white pebble or light limestone (F.LOT) to bounce diffused light; no direct sun needed at H/W 1.17.

4. GUARDING. 1,100 mm to every open edge at grade (research §6), frameless 21.5 mm laminated glass in a 150 mm recessed channel so the guard is invisible from the rooms -- the wells are the manufactured view.

5. PUMPED SUMP, ONE PER WELL. 450 × 450 × 600 mm deep, twin submersible pumps duty/standby at 3 L/s / 6 m head, high-level float alarm to the panel, 63 mm rising main with non-return valve, discharge invert above +900 so the pool's catch basin (water line +640) cannot back-feed it. Design inflow for 1-in-100 on 18 m² of open well at 150 mm/h × 1.4 climate factor = 1.05 L/s, so duty capacity is ~3× cover. Plus a 100 mm floor gully in the pool plant room (research: the room will flood) and a drained cavity with leak detection under the pool, whose water sits 3.50 m above the basement floor.

6. ADD THE BASEMENT STAIR -- mandatory, because closing the hole seals a basement that the probe shows has no stair, lift or partition of any kind. Put it inside the widened WEST well as an external service stair, so staff arrive from the garden and enter through the glazed wall without crossing guest or family space (the Gulf three-entrance discipline the research demands): dogleg, 3,700 mm floor-to-floor, 22 risers @ 168 mm, going 280 mm, two 1,100 mm flights with a 1,100 mm half-landing -- footprint 2,300 × 3,900 mm, which fits the 2,400 × 4,600 mm well with 100 mm to spare. It costs no habitable ground-floor area, and it leaves the east well as a pure 6.96 m² light court facing the staff room.

FINALLY, FIX THE ARITHMETIC AND THE DRAWING. villa_3d.py:289-295 must deduct any void from `gf` before printing GFA, and derive() should cut the ground plan at GF + 1200 as now but add the void outline as a hatched hole -- a plan cut above a hole in the floor it is describing is how this got through in the first place.

### Upheld 14

CONFIRMED, and the model is worse than the reviewer claims.

FACADE AREAS AND OPENINGS -- verified against villa_3d.py

North face: north bar y 23600-24000, x 3000-21000 = 18.0 m wide; grade 0 to parapet top RF+SLAB+PARAPET = 8700+500+1100 = 10.30 m. 185.4 m2. The roof pavilion PV=(9000,19000,15000,24000) is FLUSH with that face (y1 = NB_Y1 = 24000) and rises to 12.20 m, adding 6.0 x 1.9 = another ~18 m2 of blank wall. Total composed north face ~203 m2. Openings in it: one -- line 248, blk(11250, 23700, 900, 12750, 24300, 3300) = 1.5 x 2.4 = 3.6 m2. That is 1.8%. VILLA_ELEV_N.png is a literally empty rectangle.

West face: x 3000, y 12500-24000 = 11.5 x 10.30 = 118.5 m2. One opening -- the clerestory at line 245-247 for xx=HX0: x 2900-3600, y 18800-23200, z 7800-8450 = 4.4 x 0.65 = 2.86 m2 = 2.4%. And it is at first-floor head height, so it lights Bedroom 3, not the ground floor.

East face: 118.5 m2; clerestory 2.86 + "service entrance" 1.1 x 2.4 = 2.64 → 5.5 m2 = 4.6%. All four of the reviewer's arithmetic figures reproduce exactly.

THE TWO ROOMS

Show kitchen 26.1 m2 (x 3400-8425, y 18400-23600). Exterior walls: west (x 3000-3400, 5.2 m long) and north (y 23600-24000, 5.0 m long). Neither carries an opening -- the west clerestory is 4.9 m above the kitchen ceiling and the entry door is in the hall. Its only light paths are DOORS_GF (8425,21500,8575,22700) 1.2 m from the hall and (5000,18250,6200,18400) 1.2 m from the dining room. Zero daylight of its own.

Women's majlis 26.1 m2 (x 15575-20600, y 18400-23600). Exterior walls: north and east. Only nominal opening is the "service entrance", and two things are wrong with it: (a) at x 20700-21300 against a wall body of 20600-21000 it leaves a 100 mm skin, so it is a blind 300 mm recess, not a hole; (b) if the skin were removed it would be a service door opening DIRECTLY INTO THE WOMEN'S MAJLIS -- the exact inversion of the docstring's stated "service on the east boundary reaching the dirty kitchen without crossing guest or family space", and the worst possible room to land it in. So the reviewer's "zero external openings" is right in effect. The majlis is lit only by borrowed light through a 1.2 m door from the hall and a 1.2 m door from the study.

THREE FACTS THE REVIEWER MISSED, ALL AGGRAVATING

1. THE OPENINGS DO NOT PENETRATE. Walls are 400 thick; six of the eight openings are cut with a void spanning only the outer 300 mm (pattern `NB_Y1-300 → NB_Y1+300` etc.), leaving a 100 mm skin. Measured: guest entrance skin 100, service entrance 100, living-room structural glazing 100, both wing windows GF 100, both wing windows FF 100. Only the FF cantilever glazing (which uses `+WALL+300`) and the two clerestories cut through. Confirmed in _crop_gf_north.png: the north wall runs unbroken across all 18 m, with the front door reading as a thin line. So the front door, the 5.6 x 3.3 m living-room glazing and four bedroom/reception windows are all blind recesses. The real south void is 0%, not 23.8%.

2. NOTHING OPENS ONTO THE TWO LIGHT SLOTS. Lines 174-177 cut two 1.0 x 6.1 m slots (x 8000-9000 and x 15000-16000, y 12200-18300) through all three storeys and out through the roof slab and parapet -- the "AGi Wall House patios developed three-dimensionally". Five rooms have walls on them (dining, family living x2, study, bedroom 1, bedroom 2) and not one window is cut into any of those six wall faces. The scheme's own daylight device is unused.

3. NINE BRISE-SOLEIL FINS SHADE A BLANK WALL. Lines 261-263 put 9 fins at x 2300-2750, y 12800-17780, running the full 7.8 m height -- precisely in front of the west wing, whose west wall has no opening at all. Visible in VILLA_ELEV_W.png: the fin array floats on an empty plane. The docstring justifies them ("east/west CANNOT be shaded by horizontals") for glazing that was never cut.

Also: the roof pavilion is 30 m2 counted in the 407 m2 GFA, has 250 mm walls, no opening of any kind, and no stair reaching it (the stair void stops at FF).

WHY THIS IS FATAL, NOT TASTE. A 26 m2 principal reception room with no window is not a stylistic preference -- in most jurisdictions a habitable room needs glazing of roughly 1/10 of floor area, here 2.6 m2 against zero, and the majlis is the room the client's guests actually sit in. 1.8% and 2.4% void on two of four elevations is an order of magnitude below anything that reads as a designed facade; the research file's own "WWR <30%" is an upper bound for heat, not a target. Nothing here is a matter of taste.

WHERE THE REVIEWER'S PROPOSED FIX IS WRONG (hence the corrected version). (a) Their majlis court at x 15600-20600, y 24000-26500 sits on top of the pedestrian gate, which line 285 puts at x 15400-16600 -- guests would enter the street gate directly into the private women's court. (b) A women's majlis is the most privacy-sensitive room in the brief; glazing it 2.5 m from the guest arrival forecourt across a wall that in the FRONT setback is typically capped at 1.8-2.0 m (the 2.4 m limit is side/rear) is the wrong side of the house. (c) Their kitchen court dimensions contradict themselves -- "4.0 x 2.5 m" but "x 0-3000, y 19000-23000" is 3.0 x 4.0, and x 0-350 is the boundary wall, leaving 2.65 m. (d) Most importantly, cut in the style of the existing code their new openings would be blind recesses like the other six.

**Corrected fix:**

All coordinates in mm on the existing setting-out grid; WALL=400, GF=900, FF=5000.

STEP 0 -- PREREQUISITE: MAKE OPENINGS PENETRATE. Nothing below works until this is fixed. Rule: an opening void must overshoot BOTH wall faces by 100. Edit villa_3d.py:
 L238-239 living-room glazing: y1 12800 → WG_Y0+WALL+100 = 13000
 L243 wing glazing GF and L244 wing glazing FF: y1 12800 → 13000
 L248-249 guest entrance: y span 23700-24300 → NB_Y1-WALL-100 = 23500 to NB_Y1+100 = 24100
 L257-258 service entrance: DELETE ENTIRELY (see step 2).
Standard spans for new work: north wall y 23500→24100; west wall x 2900→3500; east wall x 20500→21100; south wing wall y 12400→13000.

STEP 1 -- MAJLIS: WALLED NORTH COURT, SUNK 750, OFF THE ARRIVAL AXIS.
Court clear 4.60 x 4.65 m = 21.4 m2 -- x 16000-20600, y 24000-28650 (runs to the inner face of the north boundary wall, so no dead strip). Meets the research minimum for a court with a tree (4x4 m, 1.0-1.2 m soil).
 Paving at +150, i.e. 750 BELOW the majlis floor at +900 -- take the drop as a 750 mm stone plinth/seat at the glass with 5 risers 150 x 300 going at the west end. Sinking the court is what lets a 2.0 m screen wall do the privacy work, so the design does not depend on being allowed a 2.4 m wall in the front setback.
 Screen walls, 400 stone, top z 2000 (2.0 m above street, 1.85 m above the court -- inside the typical front-setback cap; take them to 2400 if the authority allows):
  S.append(blk(15600, 24000, 0, 16000, 28650, 2000))   # west screen, separates court from the guest forecourt
  S.append(blk(20600, 24000, 0, 21000, 28650, 2000))   # east screen
 Glazing in the majlis north wall, 4.00 x 2.70 full height, head aligned with the 2.7 m door head:
  V.append(blk(16100, 23500, 900, 20100, 24100, 3600))   # 10.8 m2
 600 mm hood/drip over it: S.append(blk(16100, 23600, 3600, 20100, 24200, 3800)).
 RELOCATE THE PEDESTRIAN GATE -- mandatory, it currently lands inside this court. L285: x 15400-16600 → x 13400-14600 (1.2 m clear), which puts arrival 900 mm clear of the rill surround (x 11500-12500) and walks the visitor down the length of the water to the door on axis -- the Casa Merida move the docstring already claims.
 FALLBACK if the authority caps front-setback walls at 1.2-1.5 m: put the court in the EAST side setback instead -- x 21000-23650 (2.65 m) by y 18400-23600 (5.20 m) = 13.8 m2, where the 2.4 m side/rear limit applies; glaze the majlis east wall 3.60 x 2.70 at y 19400-23000, cut x 20500→21100. Morning sun below 42° altitude is blocked by the 2.4 m boundary wall at 2.65 m.

STEP 2 -- KITCHEN: WEST SERVICE COURT, AND GET THE SERVICE DOOR OFF THE MAJLIS.
The kitchen is on the WEST side of the north bar, so the service entrance belongs on the west boundary, not the east. Delete L257-258 and build:
 Service court clear 2.65 x 4.60 m = 12.2 m2 -- x 350-3000, y 19000-23600 (x 0-350 is the boundary wall).
 Screen from the garden: S.append(blk(350, 18600, 0, 3000, 19000, 2400))  # side setback, 2.4 m permitted
 Screen from the guest forecourt: S.append(blk(3000, 24000, 0, 3400, 27000, 2000))
 1.0 m service gate in the north boundary wall, clear of the 4.5 m vehicle gate at x 3800-8300:
  V.append(blk(1350, PLOT_D-BW-200, 0, 2350, PLOT_D+200, 2200))
 Kitchen window over the worktop, 2.40 x 1.60, sill +2000 (1.10 above FFL), head +3600 on the door-head line:
  V.append(blk(2900, 20400, 2000, 3500, 22800, 3600))   # 3.84 m2
 Service door into the kitchen, 1.10 x 2.40:
  V.append(blk(2900, 18900, 900, 3500, 20000, 3300))   # 2.64 m2
 This makes the docstring's "three entrances" claim true for the first time: guest on axis, family via the porch, service on the west boundary straight into the kitchen without crossing guest or family space.

STEP 3 -- WEST WING: PUT GLAZING BEHIND THE FINS THAT ALREADY EXIST, AND EXTEND THE SCREEN.
 Formal dining west opening 3.00 x 2.70: V.append(blk(2900, 13800, 900, 3500, 16800, 3600))  # 8.10 m2
 Bedroom 1 west window 2.40 x 1.20: V.append(blk(2900, 14400, 5900, 3500, 16800, 7100))  # 2.88 m2
 Extend the fin array north to shade the new kitchen openings and turn a floating fragment into a facade -- 8 more fins, same section (180 x 450 at 600 centres), ground storey only:
  for i in range(8): yy = 18900 + i*600; S.append(blk(2300, yy, 900, 2750, yy+180, 4500))
 Fixed vertical fins 450 deep at 420 clear give a 43° cut-off, so late-afternoon west sun still enters -- rotate the blades 30° toward north, or deepen to 600 at 600 centres for a 45° cut-off.

STEP 4 -- FREE FIX, NO NEW BUILD: GLAZE THE TWO LIGHT SLOTS THAT ARE ALREADY CUT.
 Formal dining onto slot 1:  V.append(blk(7500, 14400, 900, 8100, 16800, 3600))    # 6.48 m2
 Family living onto slot 1:  V.append(blk(8900, 14200, 900, 9500, 17200, 6300))    # 3.0 x 5.4 in the double-height volume
 Family living onto slot 2:  V.append(blk(14500, 14200, 900, 15100, 17200, 6300))
 Study onto slot 2:          V.append(blk(15900, 14400, 900, 16500, 16800, 3600))
 Study east window 2.40 x 2.70: V.append(blk(20500, 14800, 900, 21100, 17200, 3600))  # 6.48 m2

RESULTING NUMBERS
 North  3.6 (entry, now a real opening) + 10.8 (majlis) = 14.4 / 185.4 = 7.8%, plus a 4.65 m deep stone screen projecting from the eastern third -- the flat plane is gone.
 West   2.86 + 3.84 + 2.64 + 8.10 + 2.88 = 20.3 / 118.5 = 17.1%, all of it behind a continuous 11.5 m fin screen.
 East   2.86 + 6.48 = 9.3 / 118.5 = 7.9%.
 South  unchanged at 23.8% and, after step 0, actually open.
 Majlis glazing 10.8 m2 to a 26.1 m2 floor = 41%, north-facing into a court in permanent shade -- combine with the research envelope (SHGC 0.27, U 3.0) and it stays inside the hot-dry budget.
 Kitchen glazing 6.5 m2 to 26.1 m2 = 25%, west, fully fin-shaded.
 GFA, footprint and coverage unchanged: both courts are unroofed and sit in setback land that cannot be built on.

CAVEATS TO VERIFY WITH THE AUTHORITY (same class as the two the research file already flags): front-setback wall height (assumed 2.0 m, hence the sunken court);

### Upheld 15

I could not refute this. Every load-bearing number verifies against the source, and the daylight claim verifies against a full enumeration of the void list.

AREAS (computed from villa_sheets.py:36-44, which are themselves derived from PARTS_FF in villa_3d.py:205-212, so they cannot have drifted):
- MASTER BEDROOM 17750,18400 -> 20600,21600 = 2.850 x 3.200 = 9.12 m2
- DRESSING 15575,18400 -> 17600,21600 = 2.025 x 3.200 = 6.48 m2
- MASTER ENSUITE 15575,21750 -> 20600,23600 = 5.025 x 1.850 = 9.30 m2
- Suite net 24.90 m2; gross box (15575,18400)-(20600,23600) = 26.13 m2
VILLA_RESEARCH.md:317 sets master suite 55-75 (bed 28-35, dressing 14-20, en-suite 14-20), and the project's OWN target schedule at VILLA_RESEARCH.md:335 allocates "master suite 65 (bed 30 / dressing 16 / en-suite 19)". So 24.90 m2 is 45% of the design's own stated minimum, and the 9.12 m2 bedroom is 33% of the 28 m2 bed minimum. 9.12 m2 also fails the UK Nationally Described Space Standard for a double bedroom (11.5 m2 / 2.75 m min width) -- this is not a luxury-standard quibble, it is below a basic habitable double bedroom. Even the whole east limb (26.13 + BEDROOM 2's 22.47) is 47.4 m2, still short of 55.

DAYLIGHT: I enumerated every void in villa_3d.py:237-258 and intersected each against the master bedroom volume extended through its only external wall (the east wall, x 20600-21000). Exactly one hit: the clerestory at villa_3d.py:245-247, blk(20400, 18800, 7800, 21100, 23200, 8450). With FF = 5000 that is sill 2800 / head 3450 above FFL, against a 3200 ceiling (FF + FF_CH), so only 7800-8200 is actually inside the room -- a 400 mm visible slot with a 2.80 m sill. No window, no view, no opening at eye level, nothing openable within reach. BEDROOM 3 (26.13 m2) is served identically by the mirrored west clerestory. The LANDING (6.850 x 5.200 = 35.62 m2) has no wall opening at all; its only aperture is the stair void at villa_3d.py:235, which cuts only the 500 mm slab thickness. The claim is accurate on all three.

I also found the defect is WORSE than stated. Tracing DOORS_FF (villa_3d.py:213-220) against the room rectangles:
- "landing->master" at (15425,20200,15575,21400) actually opens LANDING <-> DRESSING, not the bedroom.
- "master->en-suite" at (16200,21600,17400,21750) actually opens DRESSING <-> ENSUITE.
- "master->guest2" at (17800,18250,19000,18400) makes BEDROOM 2 (22.47 m2) reachable ONLY by walking through the 9.12 m2 master bedroom.
- "guest3->guest1" at (5000,18250,6200,18400) makes BEDROOM 1 (22.47 m2) reachable ONLY through BEDROOM 3.
So the brief's "4 bedrooms" is really two usable bedrooms and two pass-through rooms, and the master is a windowless 9 m2 box that doubles as Bedroom 2's corridor.

Two rhetorical sub-claims in the criticism are wrong, but neither changes the verdict. (1) "smaller than the guest WC" -- the guest WC is 1.825 x 2.000 = 3.65 m2, so the master is 2.5x it, not smaller. (2) "1.85 m deep cannot take a 1.7 m bath plus a walkway" -- a 1700 x 750 bath set along the en-suite's 5.025 m wall leaves 1.10 m clear, which works fine; the en-suite's real problem is its 9.30 m2 area, not its depth. The proposed fix is also partly wrong: it says to open the east wall onto "a private screened terrace", but x 21000 is already the 3.0 m side setback line, so there is only 2.65 m of unbuildable setback to the boundary wall there -- a terrace cannot go there, and an east-facing full-height opening is the one orientation VILLA_RESEARCH.md says horizontals cannot shade (it is why the west fins exist). The window has to go north or south instead.

**Corrected fix:**

The suite cannot be fixed by moving partitions alone: the first floor has 134.4 m2 of connected net area (north bar 17.2 x 5.2 = 89.4 + two wings at 4.2 x 5.35 = 22.47 each), while a compliant master 55-75 plus three guest suites at 28-35 plus stair and landing needs 165-205 m2. It is ~35 m2 short, so one bedroom must leave the floor. All dimensions below are in the model's own setting-out coordinates.

1. MOVE BEDROOM 2 TO THE ROOF PAVILION. Change PV from (9000, 19000, 15000, 24000) to (8500, 18800, 15500, 24000): 7.0 x 5.2 = 36.4 m2 gross, 6.5 x 4.7 = 30.55 m2 internal at 250 mm walls -- a real guest suite (bed 21 + en-suite 7 + wardrobe), inside the roof slab extent (x 3000-21000, y 9500-24000). Roof GFA 30 -> 36.4, so total GFA 407 -> 413.4 m2, still under the 418 m2 / 4,500 sq ft brief.

2. GIVE THE MASTER THE EAST LIMB PLUS 3.1 M OF THE NORTH BAR. Replace PARTS_FF entries 2, 3 and 4 with:
   (12150, 18400, 12300, 23600)   landing | master dressing
   (15000, 18400, 15150, 23600)   dressing | master bedroom
   (16400, 14750, 20600, 14900)   en-suite | south loggia (in the east wing)
   and delete the old (15425,...), (17600,...) and (15575, 21600, 20600, 21750) partitions. Resulting suite:
   - MASTER BEDROOM  15150,18400 -> 20600,23600 = 5.45 x 5.20 = 28.34 m2   (target 28-35)
   - DRESSING        12300,18400 -> 15000,23600 = 2.70 x 5.20 = 14.04 m2   (target 14-20)
   - MASTER ENSUITE  16400,14900 -> 20600,18250 = 4.20 x 3.35 = 14.07 m2   (target 14-20)
   - suite total 56.45 m2 (target 55-75), plus a 4.20 x 1.85 = 7.77 m2 private loggia at 16400,12900 -> 20600,14750 facing SOUTH over the pool, screened, reusing the existing wing opening at x 17200-19800.
   The new partition at x 12150-12300 no longer stacks on a ground wall (it lands over the entrance hall), so add a 400 mm downstand in the first-floor slab on that line, y 18400-23600 -- a 5.2 m RC span, trivial.

3. GIVE EVERY BEDROOM A REAL WINDOW. The north bar's north wall (y 23600-24000) faces the entrance court and porch, is the only elevation with no solar problem in the Gulf, and is currently blank. Add, alongside the retained clerestories (keep them -- they now do cross-ventilation and evening light, which is what a 2.8 m clerestory is actually for):
   for x0, x1 in ((4400, 7400), (16200, 20200)):
       V.append(blk(x0, NB_Y1 - 300, FF + 450, x1, NB_Y1 + 300, FF + 2850))
   That is a 3.0 m window to Bedroom 3 and a 4.0 m window to the master, both sill 450 / head 2850 above FFL -- 2.4 m of glass at eye level, under the 3.2 m ceiling. Add a 250 mm mashrabiya screen plane 400 mm outboard for street privacy.

4. LIGHT THE LANDING AND MAKE THE DOUBLE HEIGHT READ FROM ABOVE. Cut a gallery opening in the landing's south wall over the void:
   V.append(blk(9200, NB_Y0 - 400, FF + 1000, 12100, NB_Y0 + 500, FF + 2200))
   -- 2.9 m wide, sill 1.0 m for a glass balustrade, head 2.2 m. It borrows light from the ground structural glazing and is the only thing that makes a 7.30 m volume worth having on the upper floor.

5. FIX THE PASS-THROUGH ROOMS, which the replan forces anyway. Move the stair out of the master zone to a dogleg at x 8725-12150, y 18700-22000 (two 1.6 m flights, 22 risers at 186 mm over the 4100 mm rise, 10 goings at 250 mm per flight, 800 mm half-landing) -- the existing flight at villa_3d.py:232-234 is broken regardless (16 x 244 = 3904 against a 4100 rise, and a 170 mm going against a 250 mm minimum). Then give Bedroom 1 its own door off a 1.1 m spur: partition (6100, 19500, 8425, 19650) and door (6300, 18250, 7500, 18400), leaving BEDROOM 3 as 3400,19500 -> 8425,23600 (20.60 m2) plus the 2.70 x 1.10 pocket = 23.57 m2. Delete the door at (17800, 18250, 19000, 18400) entirely -- with Bedroom 2 on the roof, the east wing is master en-suite and loggia only.

Resulting first floor: master suite 56.45, Bedroom 1 (west wing) 22.47, Bedroom 3 23.57, stair 11.3, landing 8.1 -- 4 bedrooms, every one with a window at eye level and its own door off circulation.

### Upheld 16

CONFIRMED by direct solid probing, not inference. shell() (villa_3d.py:144-151) builds ring = fp - offset(fp, -WALL) with WALL=400, so every external wall runs 400 mm inward from its footprint edge: north bar outer y=24000/inner y=23600; wing+LV south outer y=12500/inner y=12900; east wall outer x=21000/inner x=20600. Every envelope void is dimensioned +/-300 about the OUTER face, removing only 300 of the 400 and leaving a 100 mm skin.

Verified three independent ways:

(1) Derived DXF. In VILLA_PLAN_GF.dxf the outer face breaks but the inner face runs straight through: front door - outer y=24000 broken 11250-12750, inner y=23600 UNBROKEN 8575-15425; LV garden glazing - outer y=12500 broken 9200-14800, inner y=12900 unbroken 9400-14600; west band - outer broken 4200-6800, inner unbroken 3400-7600; east band - outer broken 17200-19800, inner unbroken 16400-20600; service door - outer x=21000 broken 18700-19800, inner x=20600 unbroken 18400-23600. VILLA_PLAN_FF.dxf shows the same signature at both first-floor wing bands.

(2) Solid probe (decisive). I rebuilt the model and intersected a 200x100x200 mm box placed exactly in the alleged skin at each opening. All seven returned 100.0% solid. Controls - the two clerestories (line 245-247) and the FF cantilever glazing (line 240-241) - returned 0.0%.

(3) Patched rebuild. Applying the five-line fix returned 0.0% solid at all seven probes, and the re-cut GF plan now breaks the inner face at every opening (y=23600 becomes 8575-11250 / 12750-15425, etc.). Model volume drops 835 -> 830 m3: 5 m3 of masonry that should not be there.

So the front door on the axis is a 300 mm blind niche, the living volume has no opening to the pool, and the gate-rill-door-hall-pool perspective that is the entire concept is not built. Fatal for a scheme whose subject is that axis, and it contaminates every derived drawing.

Two corrections to the reviewer, neither of which rescues the design. First, it is 7 blocked openings from 5 code lines, not 6: they read only the GF plan and missed line 244, the first-floor wing bands, which has the identical defect. Second, their NUMBERS line "0 openings currently through" is wrong - 3 of the 10 envelope voids do cut through: both clerestories, and the FF cantilever glazing at line 241, which uses WG_Y0 + WALL + 300. That is the correct formula, present exactly once; the bug is that it was not used at the other five sites. Their elevation inference ("this is why ELEV_S reads as punched squares") is also not evidence - Drawing(with_hidden=False) renders a 300 mm niche and a through opening identically - but the conclusion stands on the probe.

**Corrected fix:**

Five edits in C:\Users\asdfv\autocad-mcp\villa_3d.py. Each void must straddle the full 400 mm wall: keep the -300 outward overshoot, and replace the +300 inward figure with +(WALL+100), measured outward-face to past-the-inner-face. Verified: all seven probes go from 100.0% solid to 0.0%.

Line 238-239 (GF structural glazing, LV south wall 12500-12900):
    V.append(blk(LV_X0 + 200, WG_Y0 - CANT - 300, GF + 100,
                 LV_X1 - 200, WG_Y0 + WALL + 100, GF + 3400))
  y-extent 9200 -> 13000 (was 9200 -> 12800). Opening 5.6 m wide x 3.3 m.

Line 243 (GF wing window bands, x 4200-6800 and 17200-19800):
        V.append(blk(x0, WG_Y0 - 300, GF + 450, x1, WG_Y0 + WALL + 100, GF + 3100))
  y-extent 12200 -> 13000 (was 12800). Two openings 2.6 m x 2.65 m.

Line 244 (FF wing window bands - MISSED BY THE REVIEWER, same defect):
        V.append(blk(x0, WG_Y0 - 300, FF + 450, x1, WG_Y0 + WALL + 100, FF + 2700))
  y-extent 12200 -> 13000. Two openings 2.6 m x 2.25 m.

Line 248-249 (guest entrance on the axis, north bar wall 23600-24000):
    V.append(blk(AXIS - 750, NB_Y1 - WALL - 100, GF, AXIS + 750,
                 NB_Y1 + 300, GF + 2400))
  y-extent 23500 -> 24300 (was 23700 -> 24300). Door 1.5 m x 2.4 m, now through.

Line 257-258 (service entrance, east wall 20600-21000):
    V.append(blk(HX1 - WALL - 100, NB_Y0 + 700, GF, HX1 + 300,
                 NB_Y0 + 1800, GF + 2400))
  x-extent 20500 -> 21300 (was 20700 -> 21300). Door 1.1 m x 2.4 m, now through.

Leave line 240-241 alone: it already uses WG_Y0 + WALL + 300 and cuts through. Leave 245-247 alone: the clerestories at x 2900-3600 and 20400-21100 already straddle walls at 3000-3400 and 20600-21000.

Use WALL+100, not WALL exactly: a void face coincident with the inner wall plane produces zero-thickness sliver faces in the OCC boolean. The 100 mm overshoot is the same guard line 241 already applies with 300. None of the five extended voids clip anything else - the extra 100 mm lands in already-empty interior at every site (checked against PARTS_GF, the stair at x 13000-14600, and the boundary wall at y 28650-29000).

Add a regression guard so this cannot recur silently: after building, intersect the model with a probe box in each opening's inner 100 mm and assert zero volume. Without it, an elevation cut with with_hidden=False will keep showing these as if they were real openings.

Follow-on the fix exposes, worth resolving in the same pass: with the LV south wall genuinely removed for 5.6 m x 3.3 m, the only structure over it is the 200 mm head band at z 4300-4500, and the 3.0 m first-floor cantilever bears on that wall over just 400 mm (y 12500-12900). Model an explicit portal frame / transfer beam there rather than leaving the cantilever bearing on a header that thin.

### Upheld 17

CONFIRMED -- and the model is actually worse than the reviewer states.

VERIFIED TOPOLOGY (villa_3d.py:205-220 against the schedule in villa_sheets.py:36-44). I tested every door rectangle in DOORS_FF against every first-floor room rectangle, and every void in the model that intersects the storey z=5000..8700:

  BEDROOM 3  22.5->26.1 m2  doors: landing, bedroom 1
  LANDING    35.6 m2        doors: bedroom 3, dressing
  DRESSING    6.5 m2        doors: landing, master, en-suite
  MASTER      9.1 m2        doors: dressing, bedroom 2
  BEDROOM 1  22.5 m2        doors: bedroom 3          <- ONE door, into another bedroom
  BEDROOM 2  22.5 m2        doors: master             <- ONE door, into the master

Door (5000,18250,6200,18400) sits in partition (3400,18250,7600,18400). North of y=18400 in that x-band is BEDROOM 3; south of y=18250 is BEDROOM 1. Correct as claimed.

Door (17800,18250,19000,18400) sits in partition (16400,18250,20600,18400). The master runs x 17750-20600, the dressing only to x 17600, so the door at x 17800-19000 lands wholly inside the MASTER BEDROOM. Correct as claimed.

No other opening rescues either room. The only first-floor voids touching BEDROOM 1 and BEDROOM 2 are their south windows (4200-6800 and 17200-19800 at y 12200-12800, sill FF+450) -- glazing, not access. The two 1.0 m light slots (x 8000-9000 and 15000-16000, cut y 12200-18300 through every level) sever the wings from the central volume entirely, so a wing can only ever be reached across the y=18000 line, i.e. through the north-bar end zone above it. There is no alternative path in the geometry.

The reviewer understated the chain on the east. Door (15425,20200,15575,21400) -- commented "landing -> master" -- actually opens into the DRESSING room (x 15575-17600), not the master. So the real escape route from BEDROOM 2 is: bedroom 2 -> master bedroom -> dressing room -> landing. Two intervening private rooms, one of them the principal bedroom and one a dressing room, both of which get locked. The master bedroom itself is also an inner room, entered only through the dressing.

This is a planning defect, not a matter of taste. These are not nurseries or dressing rooms borrowed from a suite -- they are 22.5 m2 rooms labelled BEDROOM 1 and BEDROOM 2 in the issued schedule (villa_sheets.py:42-43) and counted toward the "4 BEDROOM" title block (villa_sheets.py:119). Two of the four cannot be occupied independently, let alone by a guest or an adult child. IBC 1006.2.1 permits egress through an intervening room only where the two are accessory to one another; a bedroom is not accessory to another bedroom, and Gulf municipal villa regulations generally require each habitable room to open onto a lobby or corridor.

WHERE THE REVIEWER IS WRONG, and it matters for the fix: "the 35.6 m2 landing has the area to become a proper corridor spine reaching all four rooms" is geometrically impossible. The landing spans x 8575-15425; the wings attach at x 3000-8000 and 16000-21000, and the light slots block everything between. Any link to a wing must be carved out of the BEDROOM 3 zone and the master zone, not out of the landing. The fix costs bedroom area, which is why it has to be cut as tightly as possible.

The stair sub-claim is overstated and I would not carry it. A single open stair discharging into a double-height hall is normal and permitted in a two-storey single-family dwelling (IRC; NFPA 101 ch.24, one exit plus emergency escape openings in each sleeping room). But the check turned up the real version of that concern: BEDROOM 3 and the MASTER have no openable window at all. Their only glazing is the clerestory band (villa_3d.py:245-247) at sill FF+2800, 650 mm high, 2.8 m above the finished floor -- no escape opening, no view, and effectively no daylight for a 26.1 m2 bedroom. Fix that in the same move.

**Corrected fix:**

TWO GALLERY ARMS OFF THE LANDING -- 5.8 m2 of new circulation (3.2% of the 181 m2 first floor), against the reviewer's ~9 m2. Cut as L-shaped stubs rather than full-width corridors so the end bedrooms keep their area. All coordinates in the villa_3d.py setting-out frame, mm.

PARTS_FF -- replace the list with:
  (8425, 19800,  8575, 23600)   landing | bedroom 3   [was y0=18400: shortened 1400 so the landing opens straight into the west arm]
  (15425, 19800, 15575, 23600)  landing | master zone [was y0=18400: same, east arm]
  (6300, 19800,  8425, 19950)   west arm, north side
  (6150, 18400,  6300, 19950)   west arm, west end
  (15575, 19800, 17600, 19950)  east arm, north side
  (17600, 18400, 17750, 21600)  UNCHANGED - now also forms the east arm's east end
  (15575, 21600, 20600, 21750)  UNCHANGED en-suite wall
  (3400, 18250,  7600, 18400)   UNCHANGED neck wall - now arm | bedroom 1
  (16400, 18250, 20600, 18400)  UNCHANGED neck wall - now arm | bedroom 2, solid under the master

DOORS_FF -- replace the list with:
  (7000, 19800,  8000, 19950)   west arm -> BEDROOM 3        1.0 m
  (6400, 18250,  7400, 18400)   west arm -> BEDROOM 1        1.0 m  [replaces (5000,18250,6200,18400)]
  (17600, 18500, 17750, 19400)  east arm -> MASTER BEDROOM   0.9 m
  (16500, 18250, 17500, 18400)  east arm -> BEDROOM 2        1.0 m  [replaces (17800,18250,19000,18400)]
  (17600, 20300, 17750, 21200)  master -> dressing           0.9 m  [replaces (17600,19600,17750,20500), which would now straddle the arm wall]
  (16200, 21600, 17400, 21750)  dressing -> en-suite         UNCHANGED
  DELETE (15425, 20200, 15575, 21400) - the wall it sat in is now the open arm mouth.

GEOMETRY AND AREAS
  West arm  x 6300-8425, y 18400-19800: 2.125 x 1.400 m clear = 2.98 m2, open to the landing across its full 1.4 m mouth.
  East arm  x 15575-17600, y 18400-19800: 2.025 x 1.400 = 2.84 m2, likewise open.
  BEDROOM 3  26.1 -> 22.6 m2 (5.025 x 3.65 main + a 2.75 x 1.55 alcove west of the arm - take that alcove as the built-in wardrobe run).
  Master zone 26.1 -> 22.9 m2; the master bedroom stays 2.85 x 5.2 because the arm stops at x 17600 and never crosses it; the dressing takes the 3.3 m2 loss.
  BEDROOM 1 and BEDROOM 2 unchanged at 22.5 m2 each. LANDING unchanged at 35.6 m2.

ACCESS AFTER THE FIX -- four independent bedroom doors, no bedroom on anyone's escape route:
  landing -> west arm -> BEDROOM 3 | BEDROOM 1
  landing -> east arm -> BEDROOM 2 | MASTER -> dressing -> en-suite
The suite hierarchy is now correct as well (the master is entered directly, not through its own dressing room).

TWO DETAILS THAT MUST GO WITH IT
1. Close the arm ends over the light slots. The slot voids stop at WG_Y1+300 = 18300, leaving a 100 mm full-height sliver of wall at y 18300-18400 spanning each 1.0 m slot - structurally absurd and it is currently all that separates the north bar from a void. Extend both slot voids to y 18400 (WG_Y1+400) and add a proper 150 mm screen: (8000, 18250, 8575, 18400) west and (15425, 18250, 16000, 18400) east, glazed full height. The two arms then terminate in glass onto the light slots and read as daylit galleries rather than dead-end passages - the move pays for itself.
2. Give BEDROOM 3 and the MASTER a real window. Add to the openings block:
     blk(4200, 23700, FF+450, 6800, 24300, FF+2700)    bedroom 3, north wall to the entry court, 2.6 m wide, sill 450
     blk(20300, 19000, FF+450, 20900, 21400, FF+2700)  master, east wall, 2.4 m wide
   Mirror the west brise-soleil fins (villa_3d.py:261-263) onto the east elevation for the second one - east glazing cannot be shaded by horizontals, which the design basis already states.

SAME FAULT ON THE GROUND FLOOR. DOORS_GF carries the identical pair: (5000,18250,6200,18400) makes the 22.5 m2 FORMAL DINING reachable only through the show kitchen, and (17800,18250,19000,18400) makes the 22.5 m2 STUDY reachable only through the WOMEN'S MAJLIS. Serving a formal dining room through the kitchen, and routing every study user across the women's majlis, is worse in a Gulf villa than the bedroom case. The same two arms cut off the entrance hall (x 8425-8575 and 15425-15575 shortened to y0=19800, arms at y 18400-19800) fix it for another ~5.8 m2, taken from the kitchen and the majlis.

### Upheld 18

CONFIRMED -- every number in the criticism reproduces exactly, and the model contains three harder defects the reviewer did not even name.

ARITHMETIC (recomputed from villa_sheets.py:36-44):
  BEDROOM 3      5.03 x 5.20 = 26.13
  LANDING        6.85 x 5.20 = 35.62  (circulation)
  MASTER BEDROOM 2.85 x 3.20 =  9.12
  DRESSING       2.02 x 3.20 =  6.48
  MASTER ENSUITE 5.03 x 1.85 =  9.30
  BEDROOM 1      4.20 x 5.35 = 22.47
  BEDROOM 2      4.20 x 5.35 = 22.47
  net 131.59 / habitable excl. landing 95.97 -> the 96.0 m2 the A-202 title block prints.
VILLA_RESEARCH.md:317-318 sets master suite 55-75 and guest suite 28-35 each, so the floor minimum is 55 + 3x28 = 139 m2. Deficit 43.0 m2 = 31%. Correct.

THE PLATE CANNOT BE REPLANNED OUT OF IT. FF gross 181 = north bar 108 + wings 27.5 x2 + cantilever 18. The cantilever rect in FF_FOOT (villa_3d.py:142) is (9000, 9500, 15000, 12900) -- disjoint from every other FF rectangle (the wings stop at x 8000 / restart at 16000, and the light slots at villa_3d.py:174-177 cut those gaps anyway), and it is 5.5 m across the double-height void from the north bar with no bridge modelled. It is a sealed, unreachable 20.4 m2 box. Usable gross is therefore 163 m2, exactly as claimed. Net available, measured off the actual wall lines rather than a ratio: bar 3400-20600 x 18400-23600 = 89.44 + two wings 3400-7600 x 12900-18250 = 22.47 each = 134.38 m2 net, before a single partition, stair or landing. 134.38 < 139. Four suites at the bottom of the researched band do not fit even with zero circulation. The claim is not refutable.

WHAT THE REVIEWER MISSED -- these are worse:
1. The master bedroom is 2.85 x 3.20 m = 9.12 m2 (villa_3d.py PARTS_FF x 15575/17600/17750/20600). Research wants a master bed of 28-35. 9.12 m2 is below a UK-standard double bedroom (11.5 m2); a 2.85 m clear width cannot take a 1.8 m king with circulation to both sides. A-202 prints "MASTER BEDROOM 9.1 m2" on the sheet. The whole master suite is 26.1 m2 gross against a 55 m2 minimum -- less than half.
2. There is ONE bathroom on the entire floor. MASTER ENSUITE 9.3 m2 is the only wet room in FIRST; bedrooms 1, 2 and 3 have no en-suite and no shared bath anywhere on the level. Four bedrooms, one WC.
3. Two bedrooms are inner rooms entered through other bedrooms. DOORS_FF (villa_3d.py:218-219) gives bedroom 1 exactly one door -- (5000, 18250, 6200, 18400) from bedroom 3 -- and bedroom 2 exactly one door -- (17800, 18250, 19000, 18400) from the master bedroom. The partitions at PARTS_FF:210 and :211 span the full interior width of each wing junction, so there is no alternative route. That is a fatal planning defect independent of any area benchmark.
Corroborating, the ground floor has no slack to donate: villa_3d.py:132 voids the sunken court (9500, 15400)-(14500, 19400) from BASE_FL up to GF+200, punching a 20 m2 hole clean through the ground slab -- 15.0 m2 of it inside the scheduled FAMILY LIVING rectangle and 5.0 m2 inside the entrance hall band. Family living is scheduled at 28.6 m2 but built as 13.6.

This is not a matter of taste. A sheet issued at 1:100 labelling a 9.1 m2 room "MASTER BEDROOM", with three bedrooms sharing no bathroom and two of them reached through someone else's bedroom, would be returned by any reviewer, let alone one appraising a US$5M villa.

**Corrected fix:**

Both of the reviewer's remedies break something worse, so the fix below differs.

Why not their (a): a 60 m2 roof master exceeds the researched Gulf roof-enclosure allowance (VILLA_RESEARCH.md:272 -- "roof enclosure 30-45") and separates the parents from all three children by a full storey. Why not their (b): deepening the bar to 7.5 and the wings to 7.0 puts the building face at y=9500, leaving a pool of 3000-9500 = 6.5 m -- below the 8.0 m plunge-pool threshold at VILLA_RESEARCH.md:188 -- and rotating the pool east-west destroys the only parti the scheme has (the Alhambra long axis, gate -> rill -> hall -> volume -> pool, villa_3d.py:28-32).

SIX EDITS, all in villa_3d.py unless noted.

1. Take the extra depth from the north bar, where the plate is 18 m wide, not from the wings, where it is 5 m:
     NB_Y0   18000 -> 17000   (bar 6.0 -> 7.0 m)
     WG_Y1   18000 -> 17000   (wings + living volume meet the new bar line)
     WG_Y0   12500 -> 11500   (wings stay 5.5 m deep, slide 1.0 m south)
     POOL_Y1 12500 -> 11500   (pool head follows the face; the 3.0 m cantilever now runs y 8500-11500)
     POOL_X0, POOL_X1  9500, 14500 -> 9000, 15000
   Also shift the slot voids (lines 174-177) and the glazing voids (lines 238-244) with WG_Y0/WG_Y1: -300 becomes 11200, +300 becomes 17300.
   Result: FF usable gross 163 -> 181 m2 (research band 170-190); ground 196 -> 214 (band 200-220); coverage 28% -> 31% (limit 35-45%); FF net available 134.4 -> 151.6 m2; pool 5.0 x 9.5 = 48 -> 6.0 x 8.5 = 51 m2, 7.3% of plot (up from 6.8%), 500 mm clear of the 8.0 m swim threshold, basin south face still 1.25 m off the wall footing (rule 0.9-1.5, line 242), and the pool now aligns exactly with the living-volume glazing instead of floating inside it.

2. Move ONE bedroom off the plate -- the guest suite, not the master:
     PV (9000, 19000, 15000, 24000) -> (8000.0, 18400.0, 16000.0, 24000.0)
   8.0 x 5.6 = 44.8 m2 enclosed, at the top of the 30-45 band: stair head 8 + guest bedroom 21 + en-suite 9 = 38 m2 net, opening onto ~70 m2 of pergola-shaded roof terrace (BUA-excluded in Dubai, line 274). A self-contained roof guest suite is a Gulf norm and partly recovers the absent dewaniya, without exiling the parents.

3. Replan the remaining floor as master + 2 guest suites against the 151.6 m2 net:
     corridor 1.20 x 17.2 m = 20.6 along the bar's south edge, y 17400-18600 (trim to 1.10 m if it binds)
     stair + landing 16.0
     master suite ~50: bedroom in the bar east end 5.0 x 5.6 = 28.0 (band 28-35), dressing 4.2 x 2.6 = 10.9, en-suite 4.2 x 2.75 = 11.6 -- east wing plus the bar east of x 15600
     2 guest suites @ 30-32: each = west/centre wing 4.2 x 5.35 = 22.5 plus a 5.0 x 2.0 bar strip, each with a 6-8 m2 en-suite
   Master lands at ~50 against a 55 minimum (9% under, versus 26 as modelled); every bedroom gets its own bathroom.

4. Delete both bedroom-through-bedroom doors, lines 218-219: (5000, 18250, 6200, 18400) and (17800, 18250, 19000, 18400). Every suite doors off the new corridor. This is non-negotiable regardless of area.

5. Stop modelling the cantilever as a sealed room. Remove (LV_X0, WG_Y0 - CANT, LV_X1, WG_Y0 + WALL) from FF_FOOT (line 142); replace with slab + 1100 parapet only, and reach it with a 1.5 m gallery down the west side of the void -- add (LV_X0, WG_Y0, LV_X0 + 1900, WG_Y1) = x 9000-10900, y 11500-17000 to FF_FOOT. The 20.4 m2 becomes a first-floor terrace over the pool head; its soffit still shades the water and the glazing, so the design intent at lines 37-38 survives; the void narrows 6.0 -> 3.7 m clear and is still a true double-height room, now read from a gallery -- which is what makes a double-height volume work from above.

6. Rewrite villa_sheets.py:36-44 to the new plan, and correct villa_sheets.py:27-34 to subtract the sunken court from FAMILY LIVING (-15.0) and the entrance hall (-5.0). Areas that are printed on a title block must be the areas that are built.

Resulting GFA: ground 214 + first 181 + roof 45 = 440 m2, inside the research's own 400-455 envelope for the 418 m2 brief (line 272), plus ~20 m2 of pool terrace and ~70 m2 of roof terrace excluded.

### Upheld 19

See above.

**Corrected fix:**

Make it a slab, not a room -- but four edits, not one. All in `C:\Users\asdfv\autocad-mcp\villa_3d.py`.

**(a) Line 140-142 -- drop the fourth rect from FF_FOOT:**
```python
FF_FOOT = ((HX0, NB_Y0, HX1, NB_Y1), (WW_X0, WG_Y0, WW_X1, WG_Y1),
           (EW_X0, WG_Y0, EW_X1, WG_Y1))
```

**(b) Line 162 -- stop the double-height void eating the junction band.** Start it at y=12900, not 12500, so the 400 × 5200 mm slab band that ties the cantilever to the ground-floor wall head survives:
```python
V.append(blk(LV_X0 + WALL, WG_Y0 + WALL, GF + GF_CH, LV_X1 - WALL, WG_Y1, FF))
```

**(c) After line 160 -- add the cantilever as bare slab at the FIRST-FLOOR datum (4500→5000, not 5000→5500):**
```python
S.append(blk(LV_X0, WG_Y0 - CANT, GF + GF_CH, LV_X1, WG_Y0 + WALL, FF))
V.append(blk(LV_X0, WG_Y0 - CANT + 40, GF + GF_CH,
             LV_X1, WG_Y0 - CANT + 60, GF + GF_CH + 20))   # 20x20 drip, 40 back from the tip
V.append(blk(LV_X0 + 200, WG_Y0 - 20, GF + GF_CH,
             LV_X1 - 200, WG_Y0, GF + GF_CH + 20))          # 20 mm shadow gap at the glazing head
```
6000 × 3400 × 500 mm plate, root at y=12900, tip at y=9500. Soffit z=4500 → **3.80 m above the water, 4.50 m above the garden**. Span/effective depth 3000/430 ≈ 7.0, inside the Eurocode basic 8 in VILLA_RESEARCH.md.

**(d) Replace the structure the box was silently providing.** Two 400 mm living-volume side walls, FF→RF, and a south frame band:
```python
S.append(blk(LV_X0, WG_Y0, FF, LV_X0 + WALL, WG_Y1, RF))   # pier x 9000-9400,  y 12500-18000
S.append(blk(LV_X1 - WALL, WG_Y0, FF, LV_X1, WG_Y1, RF))   # pier x 14600-15000
S.append(blk(LV_X0, WG_Y0, FF, LV_X1, WG_Y0 + WALL, RF))   # south frame y 12500-12900
V.append(blk(LV_X0 + WALL, WG_Y0 - 100, FF + 100,
             LV_X1 - WALL, WG_Y0 + WALL + 100, RF - 400))   # upper glass 5200 x 3200 at z 5100-8300
```
and **delete the old line 240-241 void** (x 9200-14800, y 12200-13200, z 5300-7900) -- it was the box's north opening and would now notch the new piers. Optionally raise the ground glazing head at line 238 from `GF + 3400` to `GF + 3500` so the two lights read as one plane broken by a single 600 mm band.

Effect: the roof over the double-height volume now spans 5.2 m clear between the piers instead of cantilevering 8.5 m; the volume is enclosed against both light slots instead of open to sky above 4.5 m; and from the pool you read a 3.0 m soffit at 4.50 m with glass running 900 → 8300 behind it, broken only by the 500 mm floor band. That is the shading move the design basis claims and currently does not deliver.

**(e) Line 293 -- stop counting an open soffit as floor area:**
```python
ct = 0.0    # 3.0 m cantilever is an open soffit over the pool, not GFA
```
First floor 181.0 → **163.0 m²**, GFA 407 → **389 m² (4,187 sq ft)**. If that 18 m² is wanted back, take it in the roof pavilion (PV 6.0 × 5.0 → 6.0 × 8.0 = 48 m²) or by deepening a wing -- not in a box over the water.

**Do not pursue the reviewer's alternative** of extending a wing south to y=9500 and cantilevering from there. The wings are x 3000-8000 and 16000-21000; the pool is x 9500-14500. Nothing extended from a wing lands over the pool without either bridging a 1.0 m light slot at first floor (which destroys the slot, one of the scheme's four stated moves) or decking over the double-height volume. The slab is the correct answer here.

### Upheld 20

CONFIRMED, and understated. I could not refute it on any reading of the geometry.

WHAT THE MODEL ACTUALLY CONTAINS
villa_sheets.py:36-44 is not a label list -- the comment at :25-26 says the extents are taken from the partition layout in villa_3d.py, and the partitions confirm it. PARTS_FF (villa_3d.py:205-212) contains exactly six walls, so the enclosed first-floor spaces are exactly the seven scheduled rooms. Computed from the source rectangles:
  BEDROOM 3      5.025 x 5.200 = 26.13
  LANDING        6.850 x 5.200 = 35.62  (circulation)
  MASTER BEDROOM 2.850 x 3.200 =  9.12
  DRESSING       2.025 x 3.200 =  6.48
  MASTER ENSUITE 5.025 x 1.850 =  9.30  (the only "wet" room)
  BEDROOM 1      4.200 x 5.350 = 22.47
  BEDROOM 2      4.200 x 5.350 = 22.47
Net internal on the first floor = 135.64 m2 (the printed "first 181.0 m2" is gross, and 18 m2 of that is the cantilever strip at FF_FOOT[3], x 9000-15000 y 9500-12900, which is a disconnected island touching no other first-floor rectangle -- it is a canopy, not floor). One wet room, 9.30 m2, for four bedrooms. The basement is a single undivided hollow (villa_3d.py:128-132, no partitions) so it adds nothing.

THE ACCESS GRAPH IS WORSE THAN CLAIMED
I resolved every DOORS_FF opening against the rooms on each side of the wall it pierces:
  LANDING <-> BEDROOM 3          (8425,21500)
  LANDING <-> DRESSING           (15425,20200)
  DRESSING <-> MASTER BEDROOM    (17600,19600)
  DRESSING <-> MASTER ENSUITE    (16200,21600)
  BEDROOM 1 <-> BEDROOM 3        (5000,18250)
  BEDROOM 2 <-> MASTER BEDROOM   (17800,18250)
Three corrections to the finding, all against the design:
1. The door at (16200,21600) is labelled "master -> en-suite" but its x-range 16200-17400 lies inside the DRESSING (15575-17600), not the master bedroom (17750-20600). The en-suite opens off the dressing.
2. The door at (15425,20200) labelled "landing -> master" also lands in the dressing. So the master bedroom is itself a dead-end room entered through its own dressing.
3. There is no corridor on this floor at all. Bedroom 1 is entered only through Bedroom 3; Bedroom 2 is entered only through the master bedroom. So Bedroom 2's route to the only bathroom crosses the master's bed, and Bedroom 1's route is Bed 1 -> Bed 3 -> landing -> dressing -> en-suite: four doors through two other people's rooms. Bedroom-through-bedroom access is the plan's substitute for the corridor it never draws.

Also note the "master suite" barely exists: bed 9.12 + dressing 6.48 + en-suite 9.30 = 24.9 m2 against VILLA_RESEARCH.md:317 (55-75; bed 28-35, dressing 14-20, en-suite 14-20). The master bedroom at 2.85 x 3.20 m is smaller than the guest WC standard allows for a dressing room.

THE REVIEWER'S ARITHMETIC IS THE WRONG NUMBER
Their 36 m2 (3 x 7 en-suite + 3 x 5 wardrobe) omits the corridor and takes no credit for the 35.62 m2 landing (26% of the floor). Corrected two ways:
  Against the project's own first-floor schedule (VILLA_RESEARCH.md:335 -- master suite 65 + 3 guest suites @30 + landing 12 + circulation 13 = 180): demand 180 m2 net against 135.64 supplied. Deficit 44.4 m2, not 36.
  At bare minimum standard (3 en-suites @5.0 + 3 wardrobes @3.5 + two 1.2 x 2.0 corridor spurs = 30.3 m2 needed, against ~15.6 m2 reclaimable by cutting the landing to a proper 20 m2): still ~15 m2 short.
Either way the reviewer's conclusion -- the bedroom floor must grow or lose a room -- is right; the number is not. Not a matter of taste: four bedrooms with no sanitary provision on their floor fails habitability, not preference.

**Corrected fix:**

Do not just add the deficit to a tally. The fix is one structural move plus a replan, and the move is already in the design's own vocabulary.

1. CANTILEVER BOTH WINGS 3.0 m SOUTH -- first floor only
In FF_FOOT (villa_3d.py:140-142) change the wing rectangles to (WW_X0, WG_Y0-CANT, WW_X1, WG_Y1) and (EW_X0, WG_Y0-CANT, EW_X1, WG_Y1), i.e. south face from y=12500 to y=9500. This is the identical 3.0 m projection and the identical line already used for the central volume (CANT=3000, villa_3d.py:100, "Eurocode 2 sweet spot 2.5-3.5 m"), so no new structural type, no props, nothing in the pool deck. It lands the whole first-floor south face on one line at y=9500 instead of a single lonely overhang, and it closes the pool court on three sides -- which is the Court of the Myrtles the scheme cites at villa_3d.py:28-32.
  Gross +2 x (5.0 x 3.0) = +30 m2 -> first floor 181 -> 211 m2, GFA 407 -> 437 m2 (4,704 sq ft).
  Net internal +2 x (4.2 x 3.0) = +25.2 m2 -> 135.64 -> 160.84 m2.
  Ground footprint, site coverage (28%), pool, setbacks and rear/side clearances all unchanged; the pool water (x 9500-14500) is not further overhung, and the 1.5 m surround at x 8000-9500 meets the research minimum.
  Two consequentials: extend the light-slot voids (villa_3d.py:174-177) south from WG_Y0-300 to WG_Y0-CANT-300 = 9200 so the slots still read; relocate the wing windows at (4200-6800) and (17200-19800) from y 12200-12800 to the new south face at y 9200-9800.

2. REPLAN THE FIRST FLOOR -- clear internal rectangles, replacing PARTS_FF/DOORS_FF and villa_sheets.FIRST
Wing interiors become x 3400-7600 / 16400-20600, y 9900-18250 (8.35 m deep).
  BEDROOM 1  3400, 9900 -> 7600,14400   4.20 x 4.50 = 18.90
  EN-SUITE 1 5150,14550 -> 7600,17050   2.45 x 2.50 =  6.13
  WARDROBE 1 3400,14550 -> 5000,17050   1.60 x 2.50 =  4.00
  LOBBY 1    3400,17200 -> 7600,18250   4.20 x 1.05 =  4.41   suite 33.4 m2
  BEDROOM 2 / EN-SUITE 2 / WARDROBE 2 / LOBBY 2: mirror about x = 12000. Suite 33.4 m2.
Both suites now sit inside the research band of 28-35 with bed 18.9, wardrobe 4.0, en-suite 6.1 (VILLA_RESEARCH.md:318).
  MASTER SUITE -- north-bar east bay (15575-20600 x 18400-23600) plus 12 m2 taken off the landing by moving the landing/master partition west from x 15425 to x 13000: bed 20.0, dressing 8.0, en-suite 9.0, lobby 1.0 = 38 m2, entered once from the landing, with the en-suite off the bedroom and the dressing off the bedroom -- not the reverse.
  BEDROOM 3 SUITE -- north-bar west bay less the corridor spur: bed 15.1, en-suite 1900 x 2600 = 4.94, wardrobe 1900 x 1250 = 2.38 = 22.4 m2. This is the one room that lands under the 28-35 band; it is the compromise the bay's 5.2 m depth forces.
  CORRIDOR -- 1200 mm clear along the south edge of the bar, y 18400-19600, x 6400-17600, open over the double-height volume between x 9400-14600 with a glass balustrade (keeps the compression-release move), with doors into each wing lobby at x 6400-7600 and 16400-17600. No bedroom is entered through another bedroom.
  STAIR -- rebuild in a 2575 x 3850 well at x 12850-15425, y 19750-23600: 17 risers @ 241 mm (floor to floor is FF-GF = 4100), 280 mm going, two 1200 mm flights about a 1200 mm half-landing. The modelled stair (villa_3d.py:232-234) is 16 x 244 = 3904 mm -- 196 mm short of the floor it serves -- on a 170 mm going, so it has to be replaced by this fix in any case.

3. RESULT
Four en-suites; first-floor wet area 26.3 m2 against 9.30 now; no bedroom reached through another bedroom; the ground-floor guest WC reverts to serving the majlis, which is its job (research 3.5-5 m2 -- the modelled 3.65 is correct for that role and only wrong as the house's sole upper-level facility).

4. IF THE CLIENT WILL NOT GROW THE ENVELOPE
Then the reviewer's second branch applies and should be stated plainly: hold 135.64 m2 net and every room drops to roughly 22 m2 with a master no larger than a guest room, which will not read as US$5M. The alternative is three bedrooms above ground at full research size and the fourth as a ground-floor guest suite in the 22.5 m2 STUDY, which already has its own external aspect and sits next to the guest WC -- but that costs the study and still needs the corridor and the three en-suites drawn.

### Upheld 21

CONFIRMED -- this is a geometric fact, not taste, and the code contradicts its own stated intent.

Verified in C:\Users\asdfv\autocad-mcp\villa_3d.py:
- Line 257-258: `V.append(blk(HX1 - 300, NB_Y0 + 700, GF, HX1 + 300, NB_Y0 + 1800, GF + 2400))  # service entrance` with HX1=21000, NB_Y0=18000 gives a void at x 20700-21300, y 18700-19800, z 900-3300. The north bar's east external wall is x 20600-21000 (footprint x 3000-21000 offset inward by WALL=400), so the void is in that wall and its inboard face is x=20600.
- villa_sheets.py line 31: `("WOMEN'S MAJLIS", 15575, 18400, 20600, 23600, "habitable")` -- the majlis interior runs x 15575-20600, y 18400-23600 = 26.1 m2, and its east wall face is exactly x=20600. The door's y range 18700-19800 sits inside the majlis y range 18400-23600. So the sole service entrance lands in the women's majlis, 300 mm off the corner, and the majlis is undivided -- no lobby, no screen, nothing between the outside door and the guests.
- Kitchen is x 3400-8425; 20600 - 8425 = 12,175 mm. The 12.2 m figure is right.
- The docstring, lines 46-48, states "service on the east boundary reaching the dirty kitchen without crossing guest or family space." There is no dirty kitchen and no pantry: GROUND in villa_sheets.py lists only show kitchen, hall, guest WC, majlis, dining, family living, study, and the semi-basement is modelled as a bare shell with no partitions at all. The docstring asserts the exact opposite of the geometry.
- The majlis's other door is (15425, 20500, 15575, 21700) from the entrance hall, so the coffee route really is kitchen -> hall -> majlis, crossing the axial front door void at x 11250-12750.

The finding is real and severe: in a Gulf villa the women's majlis is the single most privacy-critical room, and staff, caterers and deliveries enter it directly from the side yard.

Two things the reviewer got wrong, which change the fix:
1. As modelled the void cuts only 300 mm of the 400 mm wall, leaving a 100 mm skin at x 20600-20700 -- so it is a blind recess, not an opening. This is not a defence: the guest entrance (void y 23700-24300 vs wall 23600-24000) and the pool glazing have the identical 100 mm skin, so it is a systematic convention error in the external voids, and the design intent is unambiguous from the comment and the docstring.
2. Their proposed fix is wrong. "That also fixes the dining adjacency below" is backwards. The FORMAL DINING is in the WEST wing (x 3400-7600, y 12900-18250) and, because the 1.0 m light slot at x 8000-9000 severs it from the living volume, it is reachable only through the west bay of the north bar. Swapping the bar alone puts the kitchen 12,175 mm and one entrance hall away from the dining -- the same defect transposed onto the food route -- and opens the women's majlis straight into the family's formal dining through the existing door at x 5000-6200, y 18250-18400. Their corridor scheme also does not close the breach: a 900 mm leaf from a service corridor into the majlis is still a service door into the majlis, and 1.2 m x 5.2 m of corridor (6.2 m2) plus a 12-18 m2 dirty kitchen inside the 26.1 m2 end bay leaves 6-8 m2 for the majlis itself.

**Corrected fix:**

Swap the end bays AND the wing uses together -- the bar alone is not swappable -- then split the kitchen bay for back-of-house. All dimensions land on the existing setting-out grid, and because PARTS_GF and PARTS_FF carry identical partitions at x 8425/8575 and 15425/15575, nothing structural moves: walls still stack, and only labels and five door voids change.

1. WOMEN'S MAJLIS to the west bay: x 3400-8425, y 18400-23600 = 26.1 m2, area unchanged. Entered from the hall through the existing 1.2 m opening at x 8425-8575, y 21500-22700. The existing guest WC (x 8575-10400, y 18400-20400, 3.6 m2) now sits beside the majlis door instead of at the kitchen end. The west bay also backs onto the car porch (x 3500-10500), so women guests can be set down under cover and reach the majlis in one turn.

2. WEST WING to majlis annex / women's dining: x 3400-7600, y 12900-18250 = 22.5 m2, off the majlis through the existing door at x 5000-6200, y 18250-18400. A wing hanging off an end bay is always a through-room, so only a guest-side room belongs there. Move the study to the semi-basement beside the sunken court (x 9500-14500, y 15400-19400); the brief never asked for a ground-floor study.

3. Split the east bay (x 15575-20600, y 18400-23600) with a 150 mm partition at (15575, 20950, 20600, 21100):
   - SHOW KITCHEN north: x 15575-20600, y 21100-23600 = 5.025 x 2.50 = 12.6 m². Move the hall door from (15425, 20500, 15575, 21700) to (15425, 21500, 15575, 22700) -- the exact mirror of the majlis door about the axis x = 12000.
   - DIRTY KITCHEN / SERVICE PANTRY south: x 15575-20600, y 18400-20950 = 5.025 x 2.55 = 12.8 m², meeting the 12-18 m2 requirement. Link them with a 1.2 m opening at (17800, 20950, 19000, 21100).

4. Keep the service entrance on the east boundary -- it now lands in the dirty kitchen, not the majlis -- and cut it through: change line 257 from (HX1 - 300 ... HX1 + 300) to x 20500-21300, i.e. `V.append(blk(HX1 - 500, NB_Y0 + 700, GF, HX1 + 300, NB_Y0 + 1800, GF + 2400))`. Apply the same correction to the guest entrance (y 23300-24300) and to the glazing voids, all of which currently stop 100 mm short of the inner face.

5. Give it an approach that never crosses the garden or the axis: a 1.2 m service gate in the north boundary wall hard against the east boundary -- void x 19000-20200, y 28450-29200, z 0-2400 -- feeding the east side yard, which is 2,650 mm clear (house face x 21000 to boundary wall inner face x 23650) and runs 8.7 m south to the dirty-kitchen door. The existing pedestrian gate at x 15400-16600 stays for guests.

6. FORMAL DINING to the east wing: x 16400-20600, y 12900-18250 = 22.5 m2, entered from the pantry through the existing door at x 17800-19000, y 18250-18400, which becomes the servery door. Kitchen to dining is now 5-6 m instead of 12.2 m, and the dining keeps the south glazing at x 17200-19800 onto the pool.

7. Fix the coffee route with a pantry, not a longer walk. No arrangement shortens kitchen-to-majlis below ~12 m while the bar is linear and the front door is on the centre axis, so decouple it: move the majlis/hall partition east from x 8425/8575 to x 10400/10550 (an existing grid line -- the guest WC's east wall) and take a MAJLIS PANTRY of x 8575-10400, y 20550-23600 = 1.825 x 3.05 = 5.6 m2 out of the hall's north-west corner. Concealed 900 mm leaf into the majlis at (8425, 21600, 8575, 22500); 900 mm door from the hall at (10400, 21600, 10550, 22500). The hall goes from 20.9 to 15.3 m2 and still holds 4,875 mm clear width (x 10550-15425) with the front door on axis at x 11250-12750. Staff pre-stage in the pantry, and the only crossing is a concealed leaf out of the guests' sightline from the front door.

Finally, update the docstring at lines 46-48 -- and note a related gap this exposes: there is no stair to the semi-basement anywhere in the model (the only stair is hall-to-landing at x 13000-14600), so the staff and plant level the brief calls for is currently unreachable. The service-stair down belongs in the new dirty kitchen, 1000 x 3500 mm at x 19600-20600, y 18400-21900, which trims the dirty kitchen to about 9.3 m2 and argues for taking the pantry's lost area back off the east wing instead.

### Upheld 22

CONFIRMED, and understated. I checked every line of C:\Users\asdfv\autocad-mcp\villa_3d.py.

1. THE STAIR GEOMETRY (villa_3d.py lines 231-235). The loop is:
   for i in range(16): blk(13000, 18700 + i*170, GF + i*244, 14600, 18870 + i*170, GF + (i+1)*244)
Each block is 170 mm deep in y and the next starts exactly 170 mm on, so going = 170 mm with zero nosing overlap; rise = 244 mm. Pitch = atan(244/170) = 55.13 deg. Blondel 2R+G = 658 (600-660 nominally, but only because a 244 riser and a 170 going cancel each other - both are individually out of range). VILLA_RESEARCH.md line 156 (the design's OWN sourced basis) says: "Going >= 280 mm (luxury 300-320); riser 100-180 (luxury 170) ... max 30 deg." So the stair violates its own research on all three parameters, and it violates every residential code I know of (IBC 7.75 in / 197 max riser, 10 in / 254 min tread; UK Part K 42 deg max private pitch). At 55 deg with a 170 mm going, an adult foot has no bearing - this is a ship's ladder, and it is the only way to the four bedrooms.

2. IT IS WORSE THAN 196 mm SHORT. The reviewer's arithmetic (16 x 244 = 3904 vs FF-GF = 4100) is right as far as it goes, but line 235 then cuts V = blk(13000, 18700, GF+GF_CH, 14600, 21900, FF), i.e. z 4500-5000 over the whole stair plan area, and the model is assembled as (Part() + S) - V. Step 15 (z 4560-4804) lies entirely inside that void and is DELETED; step 14 (z 4316-4560) is truncated to 4500. So in the model as built the top walking surface is z = 4500 and the first floor is z = 5000 - a 500 mm step, not 196. There is also a horizontal gap: the run ends at y = 21420 while the slab opening runs to y = 21900, so 480 mm of open shaft separates the last tread from the landing edge, over a 3.9 m drop.

3. THE BOTTOM IS ALSO UNSUPPORTED. The sunken court void (line 132) is blk(9500, 15400, -2800, 14500, 19400, GF+200), which removes the ground slab under x 13000-14500, y 18700-19400. That is the stair foot. Step 0 (z 900-1144) is cut from below to a 44 mm thick lip cantilevering 1500 of its 1600 mm width over a 3.7 m open shaft, and the floor it should start from is not there.

4. NO BASEMENT ACCESS. BS spans x 3000-21000, y 15000-24000, floor -2800, 142 m2 net. The ground slab is Pos(0,0,GF-SLAB) * extrude(fp_gf, SLAB) (line 155) - a solid plate over the entire footprint. The only things piercing it are the sunken court and the two 1.0 m light slots (lines 174-177). There is no descending flight anywhere in the file, no ramp, no vehicle access, no hatch. The single stair loop starts at GF and goes up.

5. NO ROOF ACCESS. The roof slab (line 165) blk(HX0, WG_Y0-CANT, RF, HX1, NB_Y1, RF+SLAB) is solid; the only voids at that level are the light slots at x 8000-9000 and 15000-16000, y 12200-18300, which lie in the wings and nowhere near the pavilion PV = (9000, 19000, 15000, 24000). The pavilion's floor is unbroken roof slab. The stairwell void stops at FF = 5000. The 30 m2 pavilion and the whole roof terrace are sealed.

6. NO LIFT. No shaft, no pit, no overrun anywhere in the file - on a four-level house (-2800 / +900 / +5000 / +9200). The research explicitly budgets one: line 327 "Stair per floor 14-18; lift shaft 1.6 x 1.7 m internal, 1.5 m pit, 3.6 m overrun", and line 337 puts "stair head + lift overrun 16" on the roof.

7. THE DRAWINGS CORROBORATE IT. villa_sheets.py schedules no stair and no lift in either GROUND or FIRST, and SHEETS contains only A-201 and A-202 - there is no basement or roof plan, because there would be nothing to draw. On A-201 the ground plan cut at z = GF+1200 = 2100 shows a single 1600 x 170 tick in the hall (the one tread crossing the plane) and no stairwell, no lift, no court opening at all.

This is not taste. A stair that is 25 deg steeper than the design's own stated maximum, that does not reach the floor it serves, and 172 m2 of enclosed accommodation with no means of access, is a scheme-level failure. Any reviewer with 20 years' experience opens the section, looks for the core, and stops there.

WHERE THE REVIEWER'S PROPOSED FIX IS ITSELF WRONG (hence the corrected_fix): (a) 24 x 171 = 4104, not 4100 - their own proposed assert(risers x rise == floor-to-floor) would fail on their own numbers; the rise must be derived as ftf/n, giving 170.833. (b) The footprint does not fit. A flight of 12 risers has 11 goings = 3300 mm at 300 going (not 3600), and a half-landing must be at least the stair width, ~1400, so a dog-leg needs about 4700 mm in the run direction - against the 3200 mm they say it fits into. (c) A second full stair in the north bar's west end would take ~12 m2 out of the 26.1 m2 show kitchen, leaving ~10 m2 - unbuildable; and a single-family dwelling does not need two stairs. One properly sized core serving all four levels, plus a lift, is the correct answer.

**Corrected fix:**

ONE core serving all four levels (-2800 / +900 / +5000 / +9200), plus a three-stop lift. All numbers below are checked against the model's existing grid and levels.

A. STAIR GEOMETRY - derive the rise, never type it.
Going G = 300 mm throughout (research: >= 280, luxury 300-320). Clear flight width 1400 mm (research 1100-1400). Well 125 mm. Guard 1100 mm (reuse PARAPET).
  Basement -2800 -> Ground +900:  dz 3700, n = 22, rise = 3700/22 = 168.18 mm, flights 11 + 11, run 10 x 300 = 3000
  Ground   +900 -> First  +5000:  dz 4100, n = 24, rise = 4100/24 = 170.83 mm, flights 12 + 12, run 11 x 300 = 3300
  First   +5000 -> Roof   +9200:  dz 4200, n = 25, rise = 4200/25 = 168.00 mm, flights 13 + 12, run 12 x 300 = 3600
Checks: pitch 29.25 / 29.66 / 29.25 deg (all <= 30); 2R+G = 636.4 / 641.7 / 636.0 (Blondel 600-660); max 13 risers per flight; no flight exceeds the floor-to-floor by construction.

B. CORE FOOTPRINT.
Governing length = longest run 3600 + landing 1400 = 5000 mm. Width = 1400 + 1400 + 125 = 2925 mm.
Place it in the east bay of the entrance hall, flights running north-south:
  core x 12750 - 15675, y 18400 - 23400  (2925 x 5000 = 14.6 m2 per floor; research 14-18)
The north bar's clear depth y 18400-23600 is 5200, so it fits with 200 mm to spare. To clear the 1500 mm guest door on the axis (x 11250-12750) move the majlis partition east by 250: PARTS_GF/PARTS_FF entries (15425, 18400, 15575, 23600) -> (15675, 18400, 15825, 23600). Knock-on areas: women's majlis 26.1 -> 25.0 m2 (research 25-35, ok); entrance hall 21.7 - 3.65 (WC) = 18.1 m2 (research 18-30, ok); first-floor landing 20.9 - 10.2 (well) = 10.7 m2.

C. SLAB OPENINGS (each = core footprint less the 1400 mm arrival lane at the arrival end).
  Ground slab  (z 400-900):   open x 12750-15675, y 18400-21800  - for the descending basement flight
  First slab   (z 4500-5000): open x 12750-15675, y 19800-23400  - replaces the existing line 235 void
  Roof slab    (z 8700-9200): open x 12750-15675, y 18400-21800  - stair head into the pavilion
Guard every open edge at 1100 mm.

D. ROOF PAVILION becomes the stair head. Move PV = (9000, 19000, 15000, 24000) -> PV = (10000, 18400, 16000, 23400). Still 6.0 x 5.0 = 30 m2, GFA unchanged at 407 m2, but it now covers the core and gives the roof terrace an enclosed head - exactly the "stair head + lift overrun" the research schedules on the roof.

E. LIFT - three stops (-2800 / +900 / +5000), not four, so it never breaks the roof.
  Shaft 2000 x 2100 external (1600 x 1700 internal per research, 200 walls), at x 6425-8425, y 18400-20500.
  Pit 1500 -> pit floor -4300; deepen the raft locally from -3200 to -4700.
  Overrun 3600 above the top stop -> head at +8600, which clears under the roof slab soffit at +8700 by 100 mm. No roof penetration, no overrun box.
  Knock-on: show kitchen 26.1 -> 21.9 m2 (research 20-28, ok); bedroom 3 above 26.1 -> 21.9 m2 (ok). It lands mid-basement, which is what a lift is actually for here - laundry, stores and plant.

F. FIX THE SUNKEN COURT CLASH. CT = (9500, 15400, 14500, 19400) currently holes the ground slab under the old stair foot and must not overlap the new core (x >= 12750). Separately - and this is a defect in its own right - as written it puts an unguarded 20 m2 hole through the family living room and hall floor that villa_sheets.py still counts as floor area (FAMILY LIVING 28.6 m2). Reposition it clear of the core, guard it, and subtract it from the room schedule.

G. ASSERTS IN build() so this cannot regress:
  for (z0, z1, n) in ((BASE_FL, GF, 22), (GF, FF, 24), (FF, RF + SLAB, 25)):
      rise = (z1 - z0) / n
      assert abs(n * rise - (z1 - z0)) < 1e-9, "flight does not reach the floor it serves"
      assert 100 <= rise <= 180, rise
      assert GOING >= 280, GOING
      assert math.degrees(math.atan2(rise, GOING)) <= 30.0
      assert LANDING >= FLIGHT_WIDTH
Add one more that would have caught the deleted top tread: assert the topmost tread's z-range is not intersected by any stairwell void.

### Upheld 23

Real, and verified line by line against the model -- this is a programme defect, not taste, and the file contradicts its own stated design basis.

CONFIRMED BY GEOMETRY:
1. villa_3d.py:46-48 claims "service on the east boundary reaching the dirty kitchen without crossing guest or family space." There is no dirty kitchen and no pantry anywhere: villa_sheets.py GROUND (lines 27-35) lists only show kitchen 26.1, hall 20.9, guest WC 3.6, majlis 26.1, dining 22.5, family living 28.6, study 22.5; FIRST is all bedrooms; and the basement is a bare shell (villa_3d.py:128-132 -- one offset void plus the court, no partitions, no rooms, no schedule, and no basement sheet in villa_sheets.SHEETS). A grep for dirty/pantry/laundry/maid/staff across the .py files hits only the docstring. VILLA_RESEARCH.md:323 requires dirty kitchen 12-18 m² with its own external door + pantry 4-6; :348-354 requires the coffee route to the majlis not to cross family space.
2. Kitchen door centre (8500, 22100); majlis door centre (15500, 21100); separation 7,071 mm -- computed, matches. The two 1.0 m light slots (x 8000-9000 and 15000-16000, y 12200-18300) sever both wings from the centre at ground level, so the only ground-floor circulation is the linear chain west wing - NW zone - HALL - NE zone - east wing. There is literally no second route: every tray must cross the entrance hall, at y ≈ 21,600 -- 2.0-2.4 m inside the front door and across the open north edge of the double-height living volume.
3. The service opening (villa_3d.py:257-258) is x 20700-21300, y 18700-19800 -- squarely inside the majlis (x 15575-20600, y 18400-23600). Confirmed.
4. The study is 4,200 × 5,350 = 22.47 m², is in neither the brief nor the research's 418 m² schedule, and occupies the one zone adjacent to the majlis where a service annex could go.

REVIEWER'S ERRORS (they do not rescue the design):
- It punches the house's east external wall at the 3 m setback, not the stone boundary wall (that wall, x 23650-24000, is unbroken; both gates are on the north).
- Worse than stated: the void is cut ±300 about the footprint edge while WALL = 400, so 100 mm of wall is left standing across the opening -- as modelled the "service entrance" is a blind recess that connects to nothing. The same arithmetic leaves a 100 mm skin across the guest entrance at y 23700-24300.
- The proposed fix is internally inconsistent and would break the plan: with the majlis west and the pantry in the east wing, the promised "service door from the pantry" into the majlis is 12 m away with the hall between -- the same defect mirrored. And because the wings hang off the north-bar zone above them, a west majlis strands the formal dining (west wing, 22.5 m²): its only door would be through the majlis. Deleting the study also leaves nowhere for the formal dining once the east wing becomes dirty kitchen + pantry + lobby.

"Fatal" overstates it -- it is fixable inside the existing envelope with no change to massing, footprint (196 m²), coverage (28%), GFA (407 m²), the axis, the cantilever or the pool. But the defect is real.

**Corrected fix:**

Keep the majlis east (guests turn once off the axis and are contained -- that part is right) and keep the kitchen/dining pair west. Fix the three actual faults: give the majlis its own service annex, put the dirty kitchen where this scheme's own design basis (villa_3d.py:24-26) already says service goes, and stop routing anything through the hall. All dimensions land on the existing grid; no external wall moves.

1. DELETE the opening at villa_3d.py:257-258. Also fix the cut arithmetic on every external door: write voids from (footprint edge − WALL − 60) to (edge + 60), not ±300, or 100 mm of wall stays across the front door too.

2. EAST WING (delete the 22.5 m² unbriefed STUDY) becomes the MAJLIS SERVICE SUITE, interior 16,400-20,600 × 12,900-18,250, 150 mm studs:
   - MAJLIS PANTRY 4,200 × 2,250 = 9.5 m² at y 16,000-18,250 -- coffee/tea station, sink, warming drawer, trolley park.
   - SERVICE LOBBY 2,600 × 2,600 = 6.8 m² at x 18,000-20,600, y 13,400-16,000.
   - STAFF WC 1,600 × 2,000 = 3.2 m² at x 16,400-18,000, y 13,000-15,000.
   - NEW EAST SERVICE DOOR 1,200 × 2,400 clear through the full 400 wall at x 20,600-21,000, y 14,200-15,400, into the lobby -- never into a habitable room. Reached from the 2,650 mm clear east side strip via a new 1.0 m service gate in the north boundary wall at x 21,600-22,600 (the strip is otherwise empty).
   - DISCREET SERVICE DOOR 900 × 2,400 from the pantry into the majlis, in the existing partition at y 18,250-18,400, placed at x 19,300-20,200 -- the majlis's far south-east corner, behind the seating and off the entry sightline. This replaces the majlis→study door at 17,800-19,000. Coffee route: pantry to majlis, ~1 m, zero shared floor with guests.
   - DUMBWAITER 900 × 900 at x 19,700-20,600, y 16,000-16,900, dropping into the basement dirty kitchen directly below.

3. SEMI-BASEMENT: schedule the 142 m² that is currently undivided, unreachable (no stair, no door) and unused --
   - DIRTY/WET KITCHEN 4,200 × 3,000 = 12.6 m² at x 16,400-20,600, y 15,400-18,400, taking the dumbwaiter (kept clear of the majlis slab above).
   - LAUNDRY 10.1, MAID'S ROOM 12.2 + BATH 3.6, STORE 8.0, PLANT (electrical/AHU/tanks) 16.
   - POOL PLANT 4,200 × 2,900 = 12.2 m² at x 3,400-7,600, y 15,400-18,300 -- under the formal dining, sharing no wall with a bedroom or the majlis (VILLA_RESEARCH.md:237), pipe run ~6 m to the pool, well under the 15 m limit.
   - Service corridor and both rooms daylit by the existing 5.0 × 4.0 m sunken court (9,500-14,500 × 15,400-19,400).

4. BASEMENT STAIR -- the model has none. Put it in the show kitchen's west end: dog-leg 1,600 × 3,150 at x 3,400-5,000, y 18,400-21,550; rise 3,700 (GF +900 to −2,800) = 22 risers @ 168 mm, going 260, two 750 mm flights of 2,600 run + 550 landing; 3,200 mm clear below the ground slab. Show kitchen 26.1 → 21.1 m², still inside the researched 20-28.
   - NEW WEST SERVICE DOOR 1,000 × 2,400 at x 3,000-3,400, y 19,000-20,000, opening onto a vestibule at the stair head so deliveries go straight down to the dirty kitchen without entering the show kitchen. Clear of the brise-soleil fins (y 12,800-18,200). Reached by a 1.0 m gate in the north boundary wall at x 1,200-2,200.

RESULT: every service route avoids the hall. Deliveries/staff west gate → west door → stair → basement. Majlis food dirty kitchen → dumbwaiter → pantry → discreet door. Majlis staff east gate → east door → lobby → pantry. Guests front door → hall → one majlis door. Ground habitable falls only by the deleted study; GFA 407 m², footprint 196 m², coverage 28%, the axis, the 3.0 m cantilever, the 7.30 m volume, both wings and the pool are all untouched.

Finally, rewrite villa_3d.py:46-48 to describe what is built: "three entrances -- guest on the axis, family via the porch, service on both side boundaries: west into the basement service stair serving the dirty kitchen, east into the majlis pantry."

### Upheld 24

CONFIRMED -- and it is worse than the reviewer states.

Geometry check (villa_3d.py):
- offset(fp, -400) gives the west wing a clear interior of x 3400-7600 (4200 mm) and the east wing x 16400-20600 (4200 mm). Partition (3400,18250,7600,18400) and partition (16400,18250,20600,18400) each span EXACTLY the full 4200 mm neck. Nothing else closes or opens those necks.
- Each carries exactly one 1200 mm door: (5000,18250,6200,18400) and (17800,18250,19000,18400).
- North of the west door is SHOW KITCHEN (3400-8425 x 18400-23600). North of the east door is WOMEN'S MAJLIS (15575-20600 x 18400-23600). Both confirmed against the villa_sheets.py schedule and the rendered A-201.
- No alternative route exists. The light slots (x 8000-9000 and x 15000-16000, cut from z=400 to the parapet, y 12200-18300) physically sever both wings from the double-height FAMILY LIVING volume at every level. The slot void's faces land exactly on x=8000 and x=9000, i.e. on the OUTER faces of the wing's east wall (7600-8000) and the LV's west wall (9000-9400) -- neither wall is pierced.
- The wings' only other opening is blk(x0, 12200, GF+450, x1, 12800, GF+3100): a 2600 mm window with a 450 mm sill. Not a door. So the FORMAL DINING ROOM (22.5 m2) has ONE 1200 mm opening in total, and it leads into the kitchen. Same for the STUDY, into the majlis.

So all three of the reviewer's numbers are right: dining 1 door (to kitchen), study 1 door (to majlis), 0 doors from either to the hall. This is not taste. A 22.5 m2 formal dining room whose only route from the front door runs diagonally across a 26 m2 enclosed kitchen is a circulation failure at any budget; and in a house whose brief is "women's majlis only", making the study a captive inner room off the women's reception breaks the very programme the scheme is organised around -- the study is dead whenever the majlis has guests, and the majlis is compromised whenever anyone uses the study.

Two things the reviewer missed, both of which harden the verdict:
1. The identical defect repeats on the FIRST FLOOR. PARTS_FF/DOORS_FF lines 210-211 and 218-219 are the same two lines of code: BEDROOM 1 is an inner room reachable only through BEDROOM 3, and BEDROOM 2 only through the MASTER BEDROOM. Two of the four bedrooms in a 4-bedroom villa are walk-through rooms.
2. The reviewer's PROPOSED FIX does not work. Extending the hall south into the y 18400-20550 band buys nothing, because that band never touches either neck. Its west end is stopped by the guest WC (8575-10400) and then by the kitchen/hall partition at x 8425-8575, while the west neck is at x 3400-7600 -- the hall would have to eat the show kitchen to reach it. Its east end is stopped by the hall/majlis partition at x 15425-15575, while the east neck is at x 16400-20600 -- every point of the east neck lies inside the majlis footprint, so a door "off the hall" lands in the majlis, which is the problem restated. Also, ~2.9 m2 of the claimed 10.4 m2 is occupied by the stair (13000-14600 from y 18700). And the north bar is only 5200 mm deep internally, so any cross-corridor cut through it drives the kitchen and the majlis to ~19 m2, below the researched minima (show kitchen 20-28, women's majlis 25-35).

The correct fix is not in the north bar at all. It is to occupy the two 1.0 m light slots -- currently voids that can only be looked at, never entered -- with glazed links off the double-height living volume.

**Corrected fix:**

FIX: bridge the two light slots with glazed links off the FAMILY LIVING volume. Zero area taken from the kitchen, majlis, hall, dining or study; the entrance axis and the 2.40 -> 7.30 m compression-release are untouched; the slots stop being decorative and become the best moment in the house.

All edits in villa_3d.py, ground floor only. Coordinates in mm; GF=900, DH=2700, SLAB=500.

1. WEST SLOT (x 8000-9000) -- split the void so a link can exist. Replace
     V.append(blk(WW_X1, WG_Y0-300, GF-SLAB, LV_X0, WG_Y1+300, RF+SLAB+PARAPET))
   with
     V.append(blk(8000, 12200, GF-SLAB, 9000, 16400, RF+SLAB+PARAPET))       # slot stays full-height, floor to sky, over 4.2 m
     V.append(blk(8000, 16400, GF+DH+150, 9000, 18300, RF+SLAB+PARAPET))     # shaft continues above the link roof

2. WEST LINK -- add
     S.append(blk(8000, 16400, GF-SLAB, 9000, 18000, GF))                    # link floor, 1.0 x 1.6 m, top at FFL
     S.append(blk(8000, 16400, GF+DH,   9000, 18000, GF+DH+150))             # 150 mm structural head at +3.600; glass infill
     V.append(blk(7500, 16600, GF, 8100, 17800, GF+DH))                      # 1200 x 2700 door through wing east wall (7600-8000)
     V.append(blk(8900, 16600, GF, 9500, 17800, GF+DH))                      # 1200 x 2700 door through LV west wall (9000-9400)

3. EAST SLOT + LINK -- mirror about AXIS=12000. Replace the second slot void with
     V.append(blk(15000, 12200, GF-SLAB, 16000, 16400, RF+SLAB+PARAPET))
     V.append(blk(15000, 16400, GF+DH+150, 16000, 18300, RF+SLAB+PARAPET))
   and add
     S.append(blk(15000, 16400, GF-SLAB, 16000, 18000, GF))
     S.append(blk(15000, 16400, GF+DH,   16000, 18000, GF+DH+150))
     V.append(blk(14500, 16600, GF, 15100, 17800, GF+DH))                    # LV east wall (14600-15000)
     V.append(blk(15900, 16600, GF, 16500, 17800, GF+DH))                    # wing west wall (16000-16400)

4. DEMOTE THE TWO EXISTING DOORS.
   - Kitchen -> dining becomes a servery door only: (5000,18250,6200,18400) -> (5300,18250,6200,18400), 900 mm.
   - Majlis -> study: keep, but widen to a concealed 1600 mm pair, (17600,18250,19200,18400). Once the study has its own route it is no longer hostage to the majlis, and the pair becomes an asset -- the majlis can annex the study for a large gathering (26.1 + 22.5 = 48.6 m2). Delete it instead if the client wants the study absolutely separate.

5. GIVE BOTH WINGS A GARDEN DOOR. Drop the wing south sills to FFL so dining and study open onto the terrace:
     for x0, x1 in ((4200.0, 6800.0), (17200.0, 19800.0)):
         V.append(blk(x0, WG_Y0-300, GF, x1, WG_Y0+300, GF+3100))            # was GF+450
   2600 x 2200 sliding doors. The 450 sill is right for a street elevation, wrong for the private garden face of a dining room.

RESULT
  Formal dining: 3 openings -- 1.2 m glazed link from family living, 0.9 m servery from the kitchen, 2.6 m garden door. Area unchanged at 22.5 m2.
  Study: 2-3 openings -- 1.2 m glazed link, 2.6 m garden door, optional 1.6 m majlis pair. Area unchanged at 22.5 m2.
  Show kitchen 26.1 m2 and women's majlis 26.1 m2 both unchanged; no guest ever crosses either.
  Light slots: 4.2 m of the 6.1 m run stays open basement-to-sky; the remaining 1.6 m keeps its full shaft above +3.750, glazed over at 2.70 m clear. Structurally the links also tie the wings to the central volume at ground level, which the scheme currently does only at the north bar.
  Arrival sequence becomes: gate -> rill -> 2.40 m entry soffit -> hall -> 7.30 m family living -> 1.0 m glazed slot with the lightwell dropping to the basement and open sky overhead -> formal dining. villa_sheets.py needs no schedule change; optionally add ("LINK", 8000, 16400, 9000, 18000, "circulation") and its mirror at 1.6 m2 each.

STILL OUTSTANDING (same defect, first floor, not fixable by links because the LV is a void at that level): PARTS_FF/DOORS_FF make BEDROOM 1 an inner room off BEDROOM 3 and BEDROOM 2 an inner room off the MASTER. That needs a 1200-1400 mm gallery along y 18400-19800 across the full north bar (x 3400-20600), which drives the bedrooms to 3.8 m depth and forces the stair to be re-set (it currently rises northward from y 18700 straight through the line of that gallery). The master suite has to be re-planned regardless -- MASTER BEDROOM as scheduled is 17750-20600 x 18400-21600 = 9.1 m2, the smallest bedroom in the house.

### Upheld 25

CONFIRMED by measuring the built solid, not by reading the source. I built the model and intersected it with a 100 mm slice at z=650 (mid ground slab, which spans 400-900):

  FAMILY LIVING   rect 28.60 m2   actual solid floor 13.60 m2   MISSING 15.00 m2
  GUEST WC        rect  3.65 m2   actual solid floor  2.75 m2   MISSING  0.90 m2
  hall->living route (x 10550-13000, y 18400-20400) 4.90 m2 -> 2.45 m2 of floor
  ENTRANCE HALL / KITCHEN / STUDY: intact (0.00 missing) - the damage is local

The reviewer's arithmetic is exact. Line 132 cuts blk(9500, 15400, BASE_FL, 14500, 19400, GF+200), i.e. from -2800 up to +1100, straight through the ground slab (400-900). Every claimed number checks out: 15.0 m2 of the living room (52%), 0.9 m2 of the guest WC, 3.7 m unguarded drop (GF 900 to BASE_FL -2800), invisible on A-201 because derive() cuts the GF plan at GF+1200 = 2100 while the court rim is at 1100 and 'beyond' projection is disabled (line 349). The rendered A-201 confirms it: FAMILY LIVING is labelled 28.6 m2 over a floor that is 13.6 m2.

Two things the reviewer MISSED that make it worse:

1. THE COURT IS 100% ROOFED. It receives no daylight at all. Probing solid material above each quadrant: south half has the 500 mm roof slab over it (the double-height volume is roofed at z=8700); north half has 1.85 m of solid (first-floor slab at 4500-5000 plus roof). Sky test from the court floor: blocked at every point. So it is not a sunken courtyard in any sense - it is an unlit, unroofed-nowhere shaft. The module docstring's whole justification ("staff, laundry, store and all plant go into a SEMI-BASEMENT lit by a sunken courtyard, which is what makes a basement a served space not a cellar") is unmet by the model. The court subtracts 15 m2 of piano nobile and delivers zero lux.

2. THE STAIR'S FIRST FLIGHT IS UNSUPPORTED. Tread 0 (y 18700-18870, z 900-1144) is 82% cut away (solid fraction 0.18); treads 1-3 are intact but sit over the void with nothing under them, above a 3.7 m drop.

Also found while checking: the two 1.0 m light slots (x 8000-9000 and x 15000-16000) ALREADY run open from the basement floor at -2800 all the way to the sky - I verified the vertical column is clear at (8500, 16000), (8500, 17800) and (15500, 16000). So the basement's only real daylight today comes from the slots, not the court, which further confirms the court is pure subtraction. And the printed "basement 142 m2" is itself wrong: line 297 computes gross (162) minus the court (20). True net internal today is 17.2 x 8.2 minus the 20 m2 court = 121.0 m2.

This is not taste. It is a hole through the primary floor plate of the house, concealed by a plan cut taken above it and a schedule that multiplies a rectangle. The severity label "fatal" is arguable (the remedy moves 20 m2 on a 696 m2 plot, it does not force a re-plan), but the defect is unambiguous.

ONE CORRECTION TO THE REVIEWER: their own proposed fix is broken. "Slide it to y 19000-23000 under the entrance hall" puts the hole under the ENTRANCE HALL, whose interior is y 20550-23600 - still occupied floor, and now the arrival space and the stair. I measured that move: it would remove (x 9500-14500) x (y 20550-23000) = 12.25 m2 of the hall's currently-intact 20.89 m2. It trades a hole in the living room for a hole in the entry. My fix puts the court outside the building envelope entirely.

**Corrected fix:**

MOVE THE COURT OUT OF THE BUILDING ENVELOPE ALTOGETHER, INTO THE FRONT SETBACK, AGAINST THE BASEMENT'S NORTH WALL.

The basement (x 3000-21000, y 15000-24000) sits entirely under the house footprint - there is no open ground over it anywhere except the two 1.0 m light slots. So no relocation *inside* the footprint works. The 5.0 m front setback (y 24000-29000) is the only open area large enough, and its east half (east of the entry axis, clear of the car porch at x 3500-10500) is empty paving today.

1. DELETE the internal court. Remove line 132 entirely. The ground slab becomes whole: FAMILY LIVING is then genuinely 28.6 m2, the guest WC 3.6 m2, the hall-to-living threshold full 2.45 m width, the stair's first flight supported. The basement gains the 20 m2 back: net internal rises from 121.0 to 141.0 m2 (17.2 x 8.2).

2. NEW SUNKEN COURT, front setback, east of the axis:
   Clear opening   x 15600 to 20600 (5.000 m) by y 24000 to 26500 (2.500 m) = 12.5 m2
                   west edge aligns with the majlis internal face (15575), east edge
                   with the basement internal east face (20600)
   Floor level     -2.800 (= BASE_FL, flush with the basement FFL)
   Depth           2.80 m below garden level 0.000 (not 3.7 - it starts at garden,
                   not at the raised GF), aspect width/depth = 0.89
   South face      y 24000 is the OUTER face of the basement/north-bar north wall.
                   Glaze that wall: void x 15600-20600, y 23600-24000, z -2700 to -400,
                   giving a 2.30 m high glazed basement elevation onto the court.
   Retaining       300 mm RC to north, east and west: structure x 15300-20900,
                   y 24000-26800, from -3.200 to +0.150 (150 mm upstand kerb).
   Guard           1.100 m frameless glass on the kerb to the three open sides,
                   or 900 mm planted kerb + 600 mm glass. Non-negotiable: this is
                   now in the arrival forecourt.
   Clearances      2.85 m east of the front door reveal (door x 11250-12750);
                   3.35 m east of the rill (x 11750-12250);
                   1.85 m from the north boundary wall inner face (28650).
   Boundary wall   locally deepen the boundary-wall strip footing to -1.400 over
                   x 15000-21400, so the 45-degree load-spread line from the footing
                   base to the court excavation at -3.200 (1.8 m vertical, 1.8 m
                   horizontal needed) lands inside the court's north retaining wall
                   at 1.85 m. Same discipline the pool already applies.
   Drainage        100 mm channel along the glazed face to a 300x300x600 sump with
                   duty/standby pumps. A sunken court in the front setback is the
                   site's low point and has no gravity outfall.

3. KNOCK-ON, and an improvement in its own right: the pedestrian gate in the north
   boundary wall (villa_3d.py line 285, x 15400-16600) currently discharges straight
   at the new court's rim, 1.85 m away. Move it onto the water axis:
       V.append(blk(AXIS - 600, PLOT_D - BW - 200, STREET, AXIS + 600, PLOT_D + 200, 2200))
   i.e. x 11400-12600, at the head of the rill. The guest gate belongs on the axis
   the whole scheme is composed around; arrival then reads gate -> rill -> door, with
   the planted court dropping away behind glass to the east.

4. BASEMENT ZONING follows: staff rooms along the north wall (y 19400-23600) facing
   the new court; laundry, store, tank and plant in the southern strip
   (y 15400-19400), which borrows light and cross-ventilation from the two existing
   full-height slots. Daylight from a 2.5 m deep court penetrates roughly 5-6 m of
   plan depth, so the 8.2 m depth is correctly served by putting the habitable rooms
   north and the served rooms south. Guard the slots at garden level over the
   basement (y 15400-18300) with walk-on glass or a 25 mm bar grille - they are
   currently open 3.2 m drops too.

5. CODE CHANGES, villa_3d.py:
       CT_X0, CT_X1 = 15600.0, 20600.0     # sunken court 5.0 x 2.5, FRONT setback
       CT_Y0, CT_Y1 = 24000.0, 26500.0     # against the basement's north wall
       CT_RW = 300.0
   replacing line 132 with:
       S.append(blk(CT_X0 - CT_RW, CT_Y0, BASE_FL - 400,
                    CT_X1 + CT_RW, CT_Y1 + CT_RW, 150))          # retaining + kerb
       V.append(blk(CT_X0, CT_Y0, BASE_FL, CT_X1, CT_Y1, 400))   # the open well
       V.append(blk(CT_X0, BS_Y1 - WALL, BASE_FL + 100,
                    CT_X1, BS_Y1, BASE_FL + 2400))               # glazed north wall
   and line 297 corrected to report NET, not gross-minus-court:
       base = area(BS_X0 + WALL, BS_Y0 + WALL, BS_X1 - WALL, BS_Y1 - WALL)   # 141 m2

6. MAKE A HOLE IN A FLOOR IMPOSSIBLE TO HIDE - both drawing fixes, because the
   geometry fix alone leaves the same trap for the next void:
   (a) In derive(), keep the GF cut at 2100 (dropping it to 1100 would put the plan
       below window heads and door heads) and ADD a below-cut projection: take a
       second section at z = GF - 250 = 650, mid-slab, and export it to a dashed
       layer A-FLOR-BELW at 0.18 lineweight. Any discontinuity in the slab plate then
       prints as a dashed outline on A-201. This is the general fix - it catches
       stair wells, duct risers and future voids, not just this one.
   (b) In villa_sheets.py, stop trusting the rectangle. The file's docstring already
       claims "Room areas are computed... never typed in"; a rectangle area is the
       same untruth one step removed. Measure it from the model:
           def floor_area(model, x1, y1, x2, y2, z=v3.GF - 300, t=100):
               probe = v3.blk(x1, y1, z, x2, y2, z + t)
               return (model & probe).volume / t / 1e6
       and assert it matches the schedule rectangle within, say, 0.05 m2, failing the
       sheet build if it does not. That single assertion would have caught this defect
       at build time: it reports 13.60 against a claimed 28.60.
  

### Upheld 26

CONFIRMED by measurement, not by reading. I built the model and probed it (`model.intersect()` volume tests in the slab band z=400-900, which is the ground floor plate).

Ground-floor slab actually present under each scheduled room:
  SHOW KITCHEN    26.1 nominal / 26.1 actual
  ENTRANCE HALL   20.9 / 20.9
  GUEST WC         3.6 / 2.7   -> 0.9 m2 missing
  WOMEN'S MAJLIS  26.1 / 26.1
  FORMAL DINING   22.5 / 22.5
  FAMILY LIVING   28.6 / 13.6  -> 15.0 m2 missing
  STUDY           22.5 / 22.5
  COURT FOOTPRINT 20.0 / 0.0   -> the court removes 20.0 m2 of ground plate

The reviewer's headline numbers are exactly right. `model = (Part() + S) - V` applies every void last and globally, so nothing whatever survives inside x 9500-14500, y 15400-19400, z < 1100. The 15.0 m2 figure is right against the SCHEDULED rectangle (9400,12900-14600,18400); against the structural LV rectangle (y to 18000) it is 13.0 m2. The schedule is the thing that lies, so 15.0 is the correct number to quote. A-201 prints "FAMILY LIVING 28.6 m2" over 13.6 m2 of floor.

It is WORSE than described. I probed the walkable floor width across the 5.2 m central spine:
  y=13500 -> 5200 mm    y=15500 -> 200 mm    y=18300 -> 200 mm
  y=15000 -> 5200 mm    y=17000 -> 200 mm    y=19300 -> 200 mm
  y=19800 -> 5200 mm
The hole is 5.0 m wide in a 5.2 m wide interior. What remains is two 100 mm ledges, not a walkable margin. The entrance hall and the family living room are not connected at all -- the scheme's own axis is severed by an unguarded 3.7 m pit (GF +900 to BASE_FL -2800), 4.0 m long, with no balustrade solid anywhere in the model and no bridge. Nothing spans it: only stair treads (x 13000-14600, from y 18700) hover over part of it. The court also eats 0.9 m2 of the guest WC and cuts 200 mm off the bottom of the WC's east partition.

The plan is confirmed blind to it. I parsed VILLA_PLAN_GF.dxf: 142 entities, ZERO vertices at y=15400 or y=19400. The plan cut is at z=2100 and the court tops out at 1100, so the hole cannot appear.

THREE OF THE REVIEWER'S SUB-CLAIMS ARE WRONG (they do not change the verdict, but the fix must not be built on them):
1. "No opening of any kind" is false. Line 238 cuts x 9200-14800, z 1000-4300 through the LV south wall -- a 5.6 x 3.3 m structural-glazing opening onto the pool, under the cantilever. I probed it: solid fraction 0.00 at y=12500/12600/12700, 1.00 at y=12800. The residual 100 mm leaf is this file's CONSISTENT glazing convention -- the wing windows, the guest entrance (NB_Y1±300 in a 23600-24000 wall) and the service door all leave exactly 100 mm. It is the glass pane in a 400 mm wall with a deep reveal, which is what line 80 says the wall is for. The room is not windowless.
2. "Sealed shaft" is false in the opposite and more alarming direction. I probed the LV side wall at x 9000-9400, y=15500: solid 1.00 at z=900/2000/3500, 0.00 at z=4500/5000/6000/7000/8000. The side walls STOP at the top of the ground storey. Above 4.5 m the double-height volume is open on both flanks, for 3.7 m of height, into the two 1.0 m light slots -- which are themselves cut open through the roof slab to the sky. The volume is not sealed, it is unweathertight.
3. "A void below cut height is invisible to section()" is wrong about the section. Section AA is taken on Plane(origin=(AXIS=12000,...)) and the court spans x 9500-14500, so the section plane passes straight through the void and does draw it. Only the PLAN is blind. The header's "plan, section and elevation cannot disagree" survives; what fails is the SCHEDULE, which is typed rectangles in villa_sheets.py that are never checked against the solid.

THE PROPOSED FIX MUST BE REJECTED -- IT REPRODUCES THE DEFECT. Relocating the court to x 16400-20600 x y 19000-23000 lands inside WOMEN'S MAJLIS (15575,18400-20600,23600). Overlap = 4.2 x 4.0 = 16.8 m2 punched out of a 26.1 m2 room, i.e. a bigger hole in a smaller room than the one being cured. The south-opening proposal is also wrong: "6.0 m, LV_X0+400 to LV_X1-400" is 5.2 m not 6.0; and cutting the full 400 mm thickness from GF to RF removes the bearing under the first-floor cantilever bar (FF_FOOT y 9500-12900), which lands on that wall. And the check as specified would not work -- a section at GF+50 (z=950) is ABOVE the 400-900 slab band and shows walls, not floor plate.

Also found while verifying (separate defects, same root cause -- nothing tests the solid): the basement interior probes to 0.00 m3 of solid, i.e. there is no stair to the semi-basement at all, and the first-floor cantilever bar (x 9000-15000, y 9500-12900, 18 m2 counted in the GFA) is a sealed box with no route from the landing. Useful context: the two light slots already run open from BASE_FL to the sky (I probed both at y=16500 from z=-2000 to 9000: solid 0.00 throughout), so the basement already has 5.2 m2 of sky opening without the on-axis court -- 25.8 m2 of the 141 m2 basement roof is currently open. The court is therefore not the only daylight source, which is what makes a zero-area-cost fix possible.

**Corrected fix:**

The court is not wrong in principle -- a sky-lit court is what makes the semi-basement a served space. It is wrong in POSITION: it is the only sky opening placed inside the building plate, and it sits on the axis. Move it into the two light slots, which are already open from -2800 to the sky and cost no floor area.

1. DELETE THE ON-AXIS COURT (villa_3d.py)
   Remove line 132: V.append(blk(CT_X0, CT_Y0, BASE_FL, CT_X1, CT_Y1, GF + 200))
   Remove CT_X0/CT_X1/CT_Y0/CT_Y1 (lines 104-105) and the `- area(CT_...)` term in the `base` calculation (line 297).
   FAMILY LIVING returns to 5.2 x 5.5 = 28.6 m2 of real floor, GUEST WC to 3.6 m2, and the hall-to-living route is 5.2 m wide again.

2. WIDEN THE TWO LIGHT SLOTS FROM 1.0 m TO 1.6 m -- they become the sunken courts
   WW_X0, WW_X1 = 3000.0, 7400.0      (was 8000.0)
   EW_X0, EW_X1 = 16600.0, 21000.0    (was 16000.0)
   The slot voids (lines 174-177) are already expressed as WW_X1->LV_X0 and LV_X1->EW_X0, so they widen automatically. Each well over the basement is 1.6 x 2.6 = 4.2 m2; 8.3 m2 total sky opening, well index 2.8 m deep / 1.6 m wide = 1.75, which carries a real window. Follow-on coordinate edits:
   PARTS_GF/PARTS_FF: (3400,18250,7600,18400) -> (3400,18250,7000,18400); (16400,18250,20600,18400) -> (17000,18250,20600,18400)
   villa_sheets.py: FORMAL DINING and BEDROOM 1 -> 3400,12900,7000,18250 = 19.3 m2; STUDY and BEDROOM 2 -> 17000,12900,20600,18250 = 19.3 m2
   Cost: 2 x 3.2 = 6.4 m2 of ground floor, against 15.0 m2 of living-room floor recovered.

3. MAKE EACH WELL A REAL COURT (three pieces the model currently lacks)
   a. Separating screen so rain does not fall into the basement: a 200 mm line at y 18000-18200 across each bay (x 7400-9000 and x 15000-16600), BASE_FL to GF-SLAB, with a 1200 x 2100 glazed door in each -- light plus a second means of escape for the staff rooms.
   b. Escape stair in the WEST well: 1000 mm wide, y 15400-17600, garden level 0 down to -2800, 14 risers @ 200 / 250 going. Basement plan puts the two staff bedrooms on the south edge, x 3400-7400 and 16600-20600, each with its window onto its own court; plant, store and laundry take the windowless north strip.
   c. 1100 mm guard at the well head on the y=15400 line of each slot, or step the garden down to it.
   d. ADD THE MISSING BASEMENT STAIR under the existing GF-FF flight: x 13000-14600, y 18700-21900, GF down to BASE_FL, 15 risers @ 246 / 250 going -- the model currently has no access to the basement at all.

4. FIX THE DOUBLE-HEIGHT ENVELOPE (real, and not what the reviewer diagnosed)
   a. Build the missing side walls -- they stop dead at z=4500:
      S.append(blk(9000, 12900, GF + GF_CH, 9400, 18000, RF))
      S.append(blk(14600, 12900, GF + GF_CH, 15000, 18000, RF))
   b. Then glaze them ONTO the widened courts, cutting 300 of the 400 mm to keep the file's glazing convention:
      V.append(blk(9000, 13400, FF + 300, 9300, 17800, FF + 2700))
      V.append(blk(14700, 13400, FF + 300, 15000, 17800, FF + 2700))
      4.4 m x 2.4 m each = 21.1 m2 of high-level glazing, which is what the slots were always for.
   c. Top light: do NOT cut horizontal glass into a flat roof in this climate. Raise the roof 900 mm over x 9400-14600, y 12900-15400 and glaze the 900 mm NORTH-facing riser at y=15400 -> 5.2 x 0.9 = 4.7 m2 of north light down the full 7.8 m.
   d. Leave the existing 5.6 x 3.3 m south glazing (line 238) as it is. Do not open GF-to-RF: the y 12500-12900 wall carries the first-floor cantilever bar.

5. THE GUARD, WRITTEN SO IT ACTUALLY CATCHES THIS
   Probe the slab band, not a section at GF+50 (that plane is above the 400-900 plate and sees only walls). In build(), before returning:

   def floor_check(model, rooms, z0, z1, label):
       bad = []
       for name, x0, y0, x1, y1 in rooms:
           got = model.intersect(blk(x0, y0, z0 + 50, x1, y1, z1 - 50))
           vol = sum(s.volume for s in got) if got else 0.0
           have = vol / (z1 - z0 - 100) / 1e6
           want = area(x0, y0, x1, y1)
           if want - have > 0.05:
               bad.append((name, want, have))
               print(f"  !! {label} {name}: schedule {want:.1f} m2, "
                     f"floor plate {have:.1f} m2, missing {want-have:.1f} m2")
       return bad

   Call it with (GF - SLAB, GF) against villa_sheets.GROUND and (FF - SLAB, FF) against villa_sheets.FIRST, and raise SystemExit if either returns non-empty. Run the same probe over the whole footprint to report total unguarded void area at each level, so a hole outside a scheduled room (the 0.9 m2 in the guest WC, the 4.1 m2 in the stair lobby) is reported too. Import the schedule from villa_sheets rather than retyping it, so the geometry and the labels can never drift apart again.

### Upheld 27

REAL, though the reviewer's numbers need correcting in three places and one sub-claim is false.

WHAT I VERIFIED IN villa_3d.py

Geometry (lines 86-89, 173-177). WW_X1=8000, LV_X0=9000, LV_X1=15000, EW_X0=16000, so the slots are exactly 1000 mm wide. The voids run y 12200-18300 (6.1 m) and z 400-10300. Confirmed.

Depth is 8.30 m, not 9.40. The reviewer took the aperture at parapet top (10300). It isn't: the parapet is a 250 mm PERIMETER ring (solid blk x3000-21000/y9500-24000 minus void x3250-20750/y9750-23750, lines 166-168), and the slots sit inside that ring, so nothing bounds them above the roof deck at z=9200. True H/W is 8.3, and projected sky view factor at the ground floor is ~2.8%, not 2.05% (~1.35% at basement floor, from 12.0 m down, not 1.09%). This is a 13% error in the reviewer's favour and it changes nothing -- 2.8% SVF is still a dark shaft.

Zero glazing faces them -- CONFIRMED, and this is the finding that matters. I enumerated all eight opening voids (lines 238-258). Every one lands on the south face y=12500, the outer walls x=3000/21000, the north face y=24000, or the east face x=21000. Not one has an edge at x=8000, 9000, 15000 or 16000. The walls bounding the slots are blank on all four faces at both storeys. The design basis at line 42 calls them "light slots"; they light nothing. That is an internal contradiction between the stated intent and the model, not a matter of taste.

The room they starve fails the research's own test. LV interior is x 9400-14600 by y 12900-18400 = 5.20 x 5.50 = 28.6 m2, against the researched family-living band of 35-45 (VILLA_RESEARCH.md §5). Worse, the double-height rule in §2 says "plan it at least as wide as it is tall in one direction; below ~5 x 5 m it reads as a shaft." Clear height is 7.30 m and BOTH plan dimensions (5.20, 5.50) are smaller. By the design's own sourced rule the principal volume reads as a shaft. That is the strongest verifiable defect here and it is caused directly by the 6.0 m LV grid the slots force.

The frontage cost is UNDERSTATED, not overstated. The reviewer says 2.0 m of 18.0 m (11%). Each slot actually consumes 400 (wing outer wall) + 1000 (slot) + 400 (LV outer wall) = 1800 mm where a merged plan needs only a 200 mm partition. Net recoverable width is 2 x 1600 = 3200 mm = 17.8% of the buildable frontage. The reviewer missed the four external wall thicknesses that the slots make necessary.

Two consequences the reviewer missed entirely. (1) The slot void cuts the roof slab from y 12200-18300, and because the parapet is only a perimeter ring, the occupied roof deck is left with two unguarded 1.0 x 6.1 m openings over an 8.3 m fall -- against §6's "roof terrace guarding min 1,100 mm". (2) fp_gf excludes the notch, so the ground slab never covers it, and the basement (interior x 3400-20600, y 15400-23600) is open to the sky at x 8000-9000 and 15000-16000, y 15400-18000: 5.2 m2 of unroofed basement with no glazing and no drainage.

WHAT IS WRONG IN THE CRITICISM

The "free-standing fins, slenderness 99" claim is false. There is a 100 mm residual sliver at y 18300-18400 (the void's arbitrary +300 stops 100 mm short of the north-bar inner face at 18400), but it is not free-standing: it is restrained on both vertical edges by the 400 mm piers at x 7600-8000 and 9000-9400, which run to y=18400, and by the ground slab, first-floor slab and roof slab at three levels. It is a 100 mm panel spanning 1.0 m between piers -- a sloppy modelling leftover and a real detailing defect, but not a slenderness-99 structural element. Drop that argument.

"They disconnect the first floor" is misattributed to lines 174-177. The first-floor gap is in FF_FOOT itself (line 140-142): the west wing ends at x=8000 and the LV strip begins at x=9000, so the footprint is already discontinuous before the void is cut. Same design decision, different line of code. Note also that the FF LV strip is only y 9500-12900 (over the pool), so it is an isolated island regardless of the slots -- deleting them does NOT fix that, and it needs its own fix.

VERDICT: real, major. The slots are a plan-grid decision that costs 17.8% of the frontage, delivers zero daylight to zero openings, leaves the principal volume 28.6 m2 against a 35-45 band and shaft-proportioned by the design's own rule, punches two unguarded holes in the roof deck and leaves the basement open to weather. The reviewer's proposed 4.5/9.0/4.5 fix is directionally right but arithmetically wasteful -- it robs the wings to 3.7 m clear because it forgets the wall thicknesses recovered by merging. See corrected_fix.

**Corrected fix:**

DELETE BOTH SLOTS AND RE-GRID -- but recover the wall thicknesses, so the wings lose nothing.

The reviewer's 4.5 + 9.0 + 4.5 gets the living room right and pays for it by cutting the wings from 4.20 to 3.70 m clear, dropping formal dining and study to 19.8 m2 (formal dining band is 28-35) and the first-floor guest bedrooms to 3.70 m wide. That trade is unnecessary. Merging the footprint replaces four 400 mm external walls with two 200 mm partitions, which hands back 3.2 m rather than 2.0 m -- enough for the same 45.1 m2 living room with the wings slightly LARGER than they are now.

1. villa_3d.py lines 173-177 -- delete both slot voids outright.

2. villa_3d.py lines 86-89 -- collapse the grid so the south band is one continuous footprint:
     WW_X0, WW_X1 = 3000.0, 7800.0     # west wing
     LV_X0, LV_X1 = 7800.0, 16200.0    # living volume, 8.4 m grid
     EW_X0, EW_X1 = 16200.0, 21000.0   # east wing
   GF_FOOT/FF_FOOT then merge into a single mass and shell() gives external walls at the perimeter only.

3. Add the two internal partitions to PARTS_GF (line 187), 200 mm, centred on the new grid lines, running from the south glass plane to the north-bar face:
     (7700, 12500, 7900, 18400),    # formal dining | family living
     (16100, 12500, 16300, 18400),  # family living | study

4. Line 162, double-height void -- set it to the new clear dimension explicitly, since LV_X0 + WALL no longer lands on the partition face:
     V.append(blk(7900, WG_Y0, GF + GF_CH, 16100, WG_Y1, FF))

RESULTING SETTING-OUT ACROSS THE 18.0 m FRONTAGE
  400 + 4300 + 200 + 8200 + 200 + 4300 + 400 = 18000 exactly
  family living   clear x 7900-16100 = 8.20 x 5.50 = 45.1 m2   (band 35-45, top of band)
  formal dining   clear x 3400-7700  = 4.30 x 5.35 = 23.0 m2   (was 22.5 -- slightly better)
  study           clear x 16300-20600 = 4.30 x 5.35 = 23.0 m2  (was 22.5)
  double-height   8.20 m wide vs 7.30 m clear height -- width now exceeds height, so it stops
                  reading as a shaft under VILLA_RESEARCH.md §2
  ground 207.0 / first 186.0 / roof 30.0 -> GFA 423 m2 = 4,553 sq ft (brief 418 / 4,500;
                  was 407 / 4,381, i.e. 2.6% under -- now 1.2% over, closer either way)
  site coverage 29.7% (research target 27-32%)

WHAT THE DELETION ALSO FIXES, FREE
  - The two unguarded 1.0 x 6.1 m openings in the occupied roof deck disappear; the slab is
    continuous and the perimeter parapet is then the only edge condition, as intended.
  - The 5.2 m2 of basement open to the sky at x 8000-9000 / 15000-16000, y 15400-18000 is
    closed by the now-continuous fp_gf ground slab.
  - The 100 mm residual sliver at y 18300-18400 goes with it. Separate lesson worth applying
    across the file: size voids to wall FACES (y=18400), never to a grid line plus an
    arbitrary +/-300.

KEEPING THE THREE-PART PARTI AT ZERO PLAN COST
The reviewer is right that the slots are invisible from the ground in VILLA_VIEW_AERIAL_SW, so
nothing is lost architecturally. If the three-finger reading is still wanted, buy it in section
and silhouette rather than in plan: step the wing parapets 400 mm below the central volume's,
and run a 150 mm x 300 mm deep vertical reveal up the south elevation on the new grid lines
x=7800 and x=16200 where the face is solid. That reads from the street at 1/500th the cost.

DO NOT WIDEN A SLOT INSTEAD. The reviewer's fallback (one slot at 3.0 m, glazed both sides) does
not survive the arithmetic: 4.3 + 3.0 + 6.2 + 4.3 plus walls exceeds 18.0 m, and even at 3.0 m
wide by 8.3 m deep the H/W is 2.8 against the researched hot-dry courtyard target of ~1.5, which
on a two-storey villa needs 5-7 m. There is no room on an 18.0 m frontage for a real court. The
sunken courtyard at 5.0 x 4.0 m already does that job for the basement; leave it as the only one.

OUT OF SCOPE BUT COORDINATE: this fix does not reconnect the first floor. The FF strip over the
pool (FF_FOOT line 142, y 9500-12900) is an isolated island whether or not the slots exist -- it
touches the wings only edge-to-edge. It should either become an open roof terrace (slab plus
1100 mm parapet, no enclosing walls, which is what a 3.0 m cantilever over a pool wants to be)
or be reached by a bridge across the double-height void. Fix that under its own finding.

### Upheld 28

CONFIRMED by direct measurement of the built solid, not just by reading source.

WALL = 400.0 (line 80). `shell()` builds walls as `ring = fp - offset(fp, -WALL, Kind.INTERSECTION)`, so every external wall band is exactly 400 mm measured inward from the footprint line. Every opening void except three is written against a hard-coded 300.

I built the model and intersected a probe box spanning the FULL 400 mm wall band across each opening's clear width and height. A working opening returns 0% solid; a blocked one returns >0%. Result -- every one of the seven returned exactly 25.0% filled, i.e. a 100 mm slab of wall standing across 100% of the opening's width and height:

  GF living-volume glazing (x 9200-14800, z 1000-4300)  1.848 m3 solid, 100% of the 100 mm slice
  GF west wing window                                   0.689 m3, 100%
  GF east wing window                                   0.689 m3, 100%
  FF west wing window                                   0.585 m3, 100%
  FF east wing window                                   0.585 m3, 100%
  GUEST ENTRANCE DOOR                                   0.360 m3, 100%
  SERVICE ENTRANCE DOOR                                 0.264 m3, 100%

Controls behave correctly: the FF cantilever-island window (line 241, written `WG_Y0 + WALL + 300`), both clerestory bands (line 246, the void spans x 2900-3600 across a 3000-3400 band), both boundary-wall gates (lines 284-285) and every interior partition door all return 0.0% -- so the probe method is sound and the difference is exactly the `+ WALL` term.

Band-vs-void arithmetic, each measured against the actual ring:
  L238 GF living glazing   band 12500-12900, void 9200-12800   -> 100 mm left
  L243 GF wing windows     band 12500-12900, void 12200-12800  -> 100 mm left
  L244 FF wing windows     band 12500-12900, void 12200-12800  -> 100 mm left
  L248 guest door          band 23600-24000, void 23700-24300  -> 100 mm left (inner side)
  L257 service door        band 20600-21000, void 20700-21300  -> 100 mm left (inner side)
  L240 FF island window    band 12500-12900, void 12200-13200  -> 0 mm, correct
  L246 clerestories        band 3000-3400,   void 2900-3600    -> 0 mm, correct

A depth sweep of the GF living-volume glazing in 100 mm slices returns 0% for y 12200 through 12800 and 100% at y 12800-12900 -- a 300 mm deep blind recess with a solid wall behind it, exactly as the reviewer describes. VILLA_SECTION_AA.png confirms it visually: the perimeter envelope is an unbroken outline with no opening breaking it anywhere.

TWO SITES THE REVIEWER MISSED, same bug shape: the light slots at lines 174-177 run to `WG_Y1 + 300` = 18300 against the north bar's south wall band at 18000-18400. They gouge a 300 mm deep, 1.0 m wide, full-height notch out of a 400 mm structural wall and leave a 100 mm fin (probed: 0.360 m3, 100% filled, at each slot). That one needs the void SHORTENED to `WG_Y1` = 18000, not lengthened -- which is why a blanket search-and-replace of the literal is wrong and why the helper the reviewer proposes is the right answer.

WHERE THE REVIEWER IS SLIGHTLY OFF (does not change the verdict):
- "8 of 11 external openings blocked" -- it is 7 of 10 as written in the file (10 opening voids: 1 GF living glazing, 1 FF island window, 2 GF wing, 2 FF wing, 2 clerestory, guest door, service door). With the two light slots it is 9 defective cuts.
- "60.1 m2 of glazing and doors" -- the measured clear area of the blocked openings is 48.5 m2 (18.5 + 6.9 + 6.9 + 5.9 + 5.9 + 3.6 + 2.6).
- Their `WALL + 100` produces a 100 mm over-cut; line 241, the one that works, uses `WALL + 300`. Either functions; 300 is the consistent one and gives more boolean tolerance.

CLASSIFICATION: this is a modelling defect, not a design defect. The parti, the section, the compression ratio and the room schedule are all unaffected -- but the model, and therefore every drawing derived from it (plans, elevations, sections, the STEP file), currently depicts an unenterable sealed box. Fatal to the deliverable, one symbol to fix.

VERIFIED FIX: I applied the correction to an in-memory copy of villa_3d.py and rebuilt. All seven openings go 25.0% -> 0.0% (clear); both light-slot fins go to a continuous 100% solid 400 mm wall; face count drops 424 -> 416 as the seven membranes and two fins disappear. Model volume prints unchanged at 835 m3 only by coincidence -- the ~5.0 m3 of membrane removed is offset by ~5 m3 of north-bar wall restored where the slots had gouged it.

RIDER THE FIX EXPOSES: once line 257 actually penetrates, the service door works -- and lands, measured against the room schedule, in the WOMEN'S MAJLIS (door x 20500-21000 at y 18700-19800; majlis is x 15575-20600, y 18400-23600). That is a street door opening directly into the one room the brief makes most privacy-critical, and it contradicts the design note at lines 47-48 ("service ... reaching the dirty kitchen without crossing guest or family space") since the kitchen is on the opposite, west side of the plan. The fix must move that door, not merely un-block it.

**Corrected fix:**

REAL -- fatal to the model as it stands, trivial to correct. All numbers below are verified against a rebuilt model.

=== 1. THE SIX OPENING CALL SITES (villa_3d.py) ===

Every void must span the whole 400 mm band, so it must be written against WALL. Use a 300 mm over-cut past both faces, matching line 241, the one opening that already works.

Line 238-239 -- GF living-volume structural glazing
  from: LV_X1 - 200, WG_Y0 + 300, GF + 3400
  to:   LV_X1 - 200, WG_Y0 + WALL + 300, GF + 3400
  inner edge 12800 -> 13200; band 12500-12900 fully crossed. Clear opening unchanged at 5.6 x 3.3 m.

Line 243 -- GF wing windows (both, inside the for-loop)
  from: blk(x0, WG_Y0 - 300, GF + 450, x1, WG_Y0 + 300, GF + 3100)
  to:   blk(x0, WG_Y0 - 300, GF + 450, x1, WG_Y0 + WALL + 300, GF + 3100)
  inner edge 12800 -> 13200. Clear 2.6 x 2.65 m, sill 1350, head 4000.

Line 244 -- FF wing windows (both)
  from: blk(x0, WG_Y0 - 300, FF + 450, x1, WG_Y0 + 300, FF + 2700)
  to:   blk(x0, WG_Y0 - 300, FF + 450, x1, WG_Y0 + WALL + 300, FF + 2700)
  inner edge 12800 -> 13200. Clear 2.6 x 2.25 m.

Line 248 -- guest entrance door (north face of the north bar; the inner side is the low-numbered one here, so the correction subtracts)
  from: blk(AXIS - 750, NB_Y1 - 300, GF, AXIS + 750, NB_Y1 + 300, GF + 2400)
  to:   blk(AXIS - 750, NB_Y1 - WALL - 300, GF, AXIS + 750, NB_Y1 + 300, GF + 2400)
  inner edge 23700 -> 23300; band 23600-24000 fully crossed. Clear 1.5 x 2.4 m on the axis, landing in the ENTRANCE HALL (verified).

Line 257 -- service entrance (east face; inner side subtracts) -- SEE SECTION 3, this door should also move
  from: blk(HX1 - 300, NB_Y0 + 700, GF, HX1 + 300, NB_Y0 + 1800, GF + 2400)
  to:   blk(HX1 - WALL - 300, NB_Y0 + 700, GF, HX1 + 300, NB_Y0 + 1800, GF + 2400)
  inner edge 20700 -> 20300; band 20600-21000 fully crossed.

=== 2. THE TWO SITES THE REVIEW MISSED -- OPPOSITE CORRECTION ===

Lines 174-177, the light slots, have the same 300-vs-400 confusion but need the void SHORTENED, not lengthened. As written they run to WG_Y1 + 300 = 18300 into the north bar's south wall band (18000-18400), cutting a 300 mm deep, 1.0 m wide, full-height notch out of a 400 mm structural wall and leaving a 100 mm fin (measured: 0.360 m3 of residual wall at each slot).

  from: V.append(blk(WW_X1, WG_Y0 - 300, GF - SLAB, LV_X0, WG_Y1 + 300, RF + SLAB + PARAPET))
  to:   V.append(blk(WW_X1, WG_Y0 - 300, GF - SLAB, LV_X0, WG_Y1,       RF + SLAB + PARAPET))
  and the same for the east slot at line 176 (LV_X1 -> EW_X0).

  18300 -> 18000. The slot now dies flush on the outer face of the north bar and leaves the 400 mm wall continuous (verified: 100% solid across the band after the change). Do NOT write WG_Y1 + WALL here -- that would cut a 1.0 m full-height hole straight through the envelope into the hall and kitchen. This asymmetry is the reason a blanket literal replacement is unsafe and the helper below is the real fix.

=== 3. THE RIDER THE FIX EXPOSES -- SERVICE DOOR LANDS IN THE WOMEN'S MAJLIS ===

Once line 257 actually penetrates, the door works and opens directly into the WOMEN'S MAJLIS. Measured: door aperture x 20500-21000 at y 18700-19800; majlis is x 15575-20600, y 18400-23600. That is a street door into the most privacy-critical room in the brief, and it contradicts the scheme's own note (lines 47-48) that the service entrance reaches the dirty kitchen without crossing guest or family space -- the kitchen is on the west side (x 3400-8425).

Move it to the west face and it lands in the SHOW KITCHEN (verified):
  V.append(blk(HX0 - 300, NB_Y0 + 700, GF, HX0 + WALL + 300, NB_Y0 + 1800, GF + 2400))
  -> void x 2700-3700 crossing the 3000-3400 band; clear 1.1 x 2.4 m at y 18700-19800.
  Checked for clashes: the west brise-soleil fins occupy y 12800-17780 at x 2300-2750, clear of the door. The west service alley is 2.65 m clear between the boundary wall (x 0-350) and the house face at x 3000 -- ample for a bin/delivery route.
If the east position is preferred for site reasons, it must land in a service lobby, not the majlis -- but no dirty kitchen or service corridor is modelled, so the west door is the honest minimum change.

=== 4. THE STRUCTURAL FIX -- MAKE THE BUG UNWRITEABLE ===

The root cause is a constant standing in for a parameter, the same shape as the reset-after-set bug already in the project notes. Add near WALL (line 80) and route every opening through it, so no void can ever be dimensioned independently of the band it must cross:

    OVER = 300.0    # boolean over-cut past each face of a pierced band

    def pierce(axis, band_lo, band_hi, a0, a1, z0, z1, over=OVER):
        """Void crossing a wall band on `axis` ('x' or 'y').
        band_lo..band_hi are the two faces of the band being pierced;
        a0..a1 and z0..z1 are the CLEAR opening. The void always runs
        band_lo - over .. band_hi + over, so full penetration is
        guaranteed whatever WALL is set to."""
        if axis == 'y':
            return blk(a0, band_lo - over, z0, a1, band_hi + over, z1)
        return blk(band_lo - over, a0, z0, band_hi + over, a1, z1)

Then, e.g., the GF living glazing becomes
    V.append(pierce('y', WG_Y0, WG_Y0 + WALL, LV_X0 + 200, LV_X1 - 200, GF + 100, GF + 3400))
and the guest door
    V.append(pierce('y', NB_Y1 - WALL, NB_Y1, AXIS - 750, AXIS + 750, GF, GF + 2400))
The light slots stay ordinary blk() calls -- they are massing voids that stop AT a face, not openings that cross one, and the distinction should be visible in the code.

=== 5. REGRESSION CHECK TO KEEP ===

Add an assertion to build() so this cannot silently return. For each external opening, intersect the model with a box spanning the full wall band across the clear opening and assert the solid volume is zero:

    for name, box in OPENING_CHECKS:
        r = model.intersect(box)
        v = 0.0 if r is None else (r.volume if hasattr(r, 'volume') else sum(s.volume for s in r))
        assert v < 1.0, f"{name}: {v/1e9:.3f} m

### Upheld 29

REAL, but the headline is the weakest part of it and the proposed fix would make the villa worse. The geometry checks out; the diagnosis needs re-aiming.

WHAT VERIFIES AS MODELLED
- Gate void (villa_3d.py:284) is x 3800..8300 cut through the boundary wall at y 28650..29000, i.e. on the property line. Standing space inside the plot = 0. True.
- Front court = wall inner face 28650 - house north face NB_Y1 24000 = 4650 mm. Porch (villa_3d.py:110-111) is 24400..28400, so 250 mm behind the wall and 400 mm off the house. True.
- No vehicle can turn: 4650 mm of depth against a 5.5 m aisle for the research hammerhead (RESEARCH:293) and 12.0 m for the forecourt. Side setbacks are 2650 mm clear and the rill (x 11250..12750, raised +150) bisects the court, so there is no loop and no hammerhead anywhere on the plot. Reversing out is mandatory. True.
- Front wall is BH = 2400 solid (villa_3d.py:279, 281) unbroken from x 350 to the west jamb (3450 mm) and from the east jamb to the pedestrian gate (7100 mm). Zero visibility splay. True, and 2400 exceeds the project's own researched Gulf front-wall band of 1800-2000 with the top 600 often required open (RESEARCH:279-281).

WHERE THE CRITICISM IS WRONG OR MIS-AIMED
1. "Reversing is therefore mandatory" is not by itself a defect. The design's own research says the opposite: "Realistically accept reversing and shape the apron for one straight movement" (RESEARCH:294). Reversing out of a villa gate is the Gulf norm. The defect is that the design fails the SECOND half of that sentence.
2. The 0-vs-5500 standing-space "deficit" is unattainable behind a 5.0 m front setback that must also park two cars, as the criticism itself concedes. Quoting it as a 5,500-6,000 mm deficit inflates the severity.
3. "~11,250 mm of blind reverse" conflates the whole manoeuvre. The correct and more damning number: the driver's eye sits ~2,600 mm (saloon) to ~3,500 mm (SUV) forward of the rear bumper, so with the tail at the wall face the car must reverse 2.6-3.5 m before the eye clears the 2400 wall - by which point the rear bumper is already 250-1,150 mm into the carriageway.
4. The proposed fix is self-defeating. Recessing the gate 1,500 mm leaves 3,150 mm of parking depth in a court that is already too short for a car. It solves a soft problem by creating a hard one.

THE TWO DEFECTS THE REVIEWER WALKED PAST, WHICH ARE THE REAL ONES
A. The court cannot park a car inside the boundary. 4,650 mm clear vs 4,985 (Land Cruiser 300), 5,165 (Patrol), 5,252 (Range Rover LWB). Every likely vehicle overhangs the plot line into the gate opening. The code comment at villa_3d.py:109 claims "2 cars, 7.0 x 5.2" but PORCH_Y0/Y1 give 7.0 x 4.0 - the comment is stale and the built depth was never checked against the setback.
B. The apron is not shaped for one straight movement. Gate centre is 6,050, porch centre 7,000. Bay 2 (x 7000..10500, centre 8750) has a car envelope of 7850..9650 against an east jamb at 8300 - it fouls by 1,350 mm. The second car cannot exit on a straight line, and with 4,000 mm of porch there is no room to shunt. On a US$5M villa the second car cannot leave unaided.

So: real, severity major rather than fatal, and the fix has to buy depth, not give it away.

**Corrected fix:**

Do NOT recess the gate. Buy depth by moving the house, widen the opening so both bays exit straight, and pay for the unattainable standing space with a real visibility splay.

1. DEEPEN THE FRONT COURT 4,650 -> 5,650 mm. Shift the whole northern grid south 1,000 mm; nothing else in the parti changes and no room area moves.
   NB_Y0/NB_Y1  18000/24000 -> 17000/23000
   WG_Y0/WG_Y1  12500/18000 -> 11500/17000
   BS_Y0/BS_Y1  15000/24000 -> 14000/23000
   CT_Y0/CT_Y1  15400/19400 -> 14400/18400
   PV           (9000,19000,15000,24000) -> (9000,18000,15000,23000)
   POOL_Y1      12500 -> 11500  (pool 5.0 x 8.5 = 42.5 m2, 6.1% of plot, still above the 8 m plunge threshold; rear setback unchanged, POOL_Y0 stays 3000)
   PORCH_Y0/Y1  24400/28400 -> 23400/28400  (5,000 mm canopy over a 5,650 mm bay)
   Every y in PARTS_GF / DOORS_GF / PARTS_FF / DOORS_FF, the stair loop and the openings shifts -1000 with it. Cleanest as one constant: FRONT_SHIFT = 1000.
   Result: 5,650 mm clear house face to leaf line = one 5,400 mm Gulf bay + 250 mm. Covers everything to a Range Rover LWB / Patrol. Confirm the client's largest vehicle first: a full-size LWB SUV (Escalade ESV 5,766) needs FRONT_SHIFT = 1400 and costs another 400 mm of pool.

2. VEHICLE OPENING 4,500 -> 6,000 mm CLEAR, RECENTRED ON THE PORCH. Gate void x 3800..8300 -> 4000..10000. Bay centrelines 5,250 and 8,750 then both sit inside the opening with >=1,250 mm of jamb clearance, so both cars reverse out on a straight line and no swept path is demanded of the street. Two 3,000 mm bi-parting cantilever sliders, run-back 3,500 mm each (research: opening + 500): west leaf parks x 500..4000, clearing the west boundary inner face at 350 by 150 mm; east leaf parks x 10000..13500, clearing the pedestrian gate at 15400 by 1,900 mm.
   Conflict to clear: the east leaf's track at y ~28150..28650 crosses the rill (x 11250..12750, currently running to y 28300). Pull the rill's north end back to y 27600 and terminate it in a 1,500 x 1,500 x 300 deep spill basin on the axis - a better ending than dead-heading into the wall 350 mm short, which is what it does now.

3. VISIBILITY SPLAY 2.5 x 2.5 m BOTH WAYS. Step the front wall down to 900 mm solid for 2,500 mm each side of the opening - x 1500..4000 and x 10000..12500 - with 45 degree splayed stone returns rising back to full height over the next 600 mm. Nothing above 900 mm in those zones: no piers, no planting, no gate motor housing. Gate hardware on a 900 x 400 mm stone pier at each jamb only. Measured from a driver's eye at 1,050-1,100 mm set 2,400 mm back from the wall face, this beats the 2.4 x 2.4 m minimum.

4. FRONT WALL 2,400 -> 2,000 mm: 1,400 mm solid stone + 600 mm open stone screen (RESEARCH:279-281, "sometimes top 600 mm required open"). Keep east, west and south walls at BH = 2400 - split BH into BH_FRONT = 2000 and BH_SIDE = 2400 at villa_3d.py:279 and rebuild line 281 as a 1,400 solid course plus a 600 screen band. Gate leaves and the pedestrian gate in the same 1,400+600 language so the front reads as one screen. Raise the pedestrian gate void (villa_3d.py:285) from 2200 to 2000 so it matches the new wall head. Privacy is untouched: GF is at +900 and the house face is now 5,650 mm back, so a 2,000 mm wall still cuts every street sightline into the ground floor.

5. STANDING SPACE - DECLARE THE DEPARTURE, DO NOT FAKE IT. 5,500-6,000 mm inside the plot line is geometrically impossible behind a 5.0 m setback that also parks two cars. Compensate: RFID/ANPR reader 25 m up-street plus a ground loop at 6 m, sliders at >=0.4 m/s (6,000 mm bi-parting fully open in 7.5 s; 25 m at 20 km/h = 4.5 s, so add a second reader at 40 m on a faster street); 6,000 mm crossover with 1,000 mm kerb radii and a 25 mm upstand so a car that does wait is square to the opening and clears the traffic lane in one movement. Record it in the submission as a declared departure with the item-3 splay as the compensating measure.

6. FOUND IN THE SAME CHECK, FIX WITH IT:
   - The porch canopy is structurally unsupported as modelled. The only ground-to-soffit element is the blade at x 10250..10500 (villa_3d.py:256); the two "beams" at x 3600 and 6900 (lines 253-254) exist only between z 3800 and 4050 and land on nothing, leaving a 6,750 mm unsupported cantilever. Add a 250 x 400 blade at x 3500..3750 over the full porch depth, or hang the canopy on two 250 mm dia CHS at x 3625 and 7025.
   - The guest entrance (villa_3d.py:248) opens at GF +900 with no external steps or ramp between the court at 0 and the threshold. Add 6 risers at 150 x 340 going (2R+G = 640, inside the 600-650 ideal band), total run 1,700 mm, across the full 1,500 mm door width; plus a 1:15 ramp 13,500 mm long running east along the court from x 12750 to the pedestrian gate for step-free access.
   - Update the stale comment at villa_3d.py:109 to the built figure (7.0 x 5.0 canopy over a 5,650 mm bay) and print the front-court depth in build() alongside the other measured figures, so this cannot drift again.

### Upheld 30

CONFIRMED -- I could not refute it. Every number checks out, and the root cause is worse than the reviewer states.

TOPOLOGY (shapely on the four FF_FOOT rects, villa_3d.py:140-142):
  unary_union -> MultiPolygon, 2 components
    [3000, 12500, 21000, 24000]  163.0 m2   north bar + two wings
    [9000,  9500, 15000, 12900]   20.4 m2   the cantilever island
  min separation 1000.0 mm (the light slot, x 8000-9000 / 15000-16000, itself
  voided full height at villa_3d.py:174-177)
  island north face y12900 -> north bar south face y18000 = 5100 mm across the void
  The ground footprint by contrast returns a single Polygon, 196.0 m2.

The island is not a slab. shell() at :144-151 offsets the whole MultiPolygon, so
the island gets a 400 mm ring wall on all four sides running z 5000 -> 8700
(3.70 m), interior 5200 x 2600 = 13.5 m2, roofed by the slab at :165. Its only
penetration is :240-241, x 9200-14800 by z 5300-7900 -- 5.6 x 2.6 m in the NORTH
wall, i.e. facing the double-height void, sill 300 mm above a 4.10 m drop to the
living-room floor at GF=900. No stair, bridge or landing is anywhere in S; the
stair at :232-235 lands in the north bar at x 13000-14600, y 18700-21900.

I checked the rendered set rather than trusting the code: VILLA_PLAN_FF.png shows
the U-shaped island floating clear of the plan with the 1 m and 5.1 m gaps
visible, and A-202's room schedule (villa_sheets.py:36-44) lists seven rooms,
none of them this one -- the model counts floor area the drawing cannot name.
VILLA_ELEV_S.png confirms a second problem the reviewer missed: the island's
south wall is completely blank. There is no opening in it anywhere in the
openings block (:237-258), so the "cantilever over the pool" is a sealed room
that cannot see the pool.

GFA: ct = area(9000, 9500, 15000, 12500) = 18.0 m2 is added at :293-296, giving
first = 108 + 27.5 + 27.5 + 18 = 181.0 and GFA 407 m2 / 4,381 sq ft. So 18 m2 of
unreachable enclosure is in the headline figure -- and it is under-measured at
that, since the true island footprint is 6.0 x 3.4 = 20.4 m2.

THE ROOT CAUSE IS BIGGER THAN THE ISLAND. fp_ff omits the LV rectangle
altogether, so nothing exists at x 9000-15000, y 12900-18000 between z 4500 and
the roof at 8700 -- walls_gf stops at 4500, and no PARTS_FF entry is south of
y 18250. The double-height living volume therefore has no east or west enclosure
above 3.60 m: a 5.1 x 4.2 m hole on each side opening straight into the
full-height light slots, which are open to the sky. The 7.30 m "clear volume"
is an outdoor room from head height up. The disconnected island and the
unenclosed void are the same defect -- the first floor was never given a face on
the living volume.

This is not taste. It is a footprint that fails a connectivity test, an area
schedule that counts a room with no door, and a section whose central move is
unbuildable as drawn.

**Corrected fix:**

Make the cantilever a real room and give the void its missing faces. Do not demote it to a canopy -- 20.4 m2 of covered, north-lit, pool-facing floor is worth more than the 18 m2 it currently fakes, and the fix lands GFA on the brief.

All coordinates in mm in the existing grid. FF = 5000, RF = 8700, WALL = 400.

1. GALLERY BRIDGE -- new constants beside the plan grid:
     BR_X0, BR_X1 = 13000.0, 14600.0   # 1600 wide, identical to the stair
     BR_Y0, BR_Y1 = 12900.0, 18000.0   # 5100 clear span
   It runs dead in line with the stair (x 13000-14600), so you climb the flight
   and walk straight out over the living room to the room above the pool. Slab
   z 4500-5000, soffit flush with the ground-floor ceiling, 250 mm structural RC
   within the 500 zone (span/depth 5100/220 = 23). It also ties the cantilever
   back into the main frame, which nothing currently does.

2. Add the bridge to the SLAB footprint only, never to the wall shell (the shell
   would wrap it in 400 walls and leave 800 mm of walkway):
     FF_SLAB = FF_FOOT + ((BR_X0, BR_Y0, BR_X1, BR_Y1),)
     _, _, fp_ffs = shell(FF_SLAB, FF, RF)
     S.append(Pos(0, 0, GF + GF_CH) * extrude(fp_ffs, SLAB))   # replaces :160

3. DELETE the void at :162. Its only effect was to strip the slab from
   x 9400-14600, y 12500-12900 -- the back span directly under the island's north
   wall, i.e. the one piece of slab the cantilever depends on. With fp_ffs the
   void area is simply uncovered; nothing needs cutting.

4. ENCLOSE THE DOUBLE-HEIGHT VOLUME at first-floor level -- two 400 mm returns
   continuing the ground-floor living-volume walls, z 5000-8700:
     S.append(blk(LV_X0, BR_Y0, FF, LV_X0 + WALL, WG_Y1, RF))       # x 9000-9400
     S.append(blk(LV_X1 - WALL, BR_Y0, FF, LV_X1, WG_Y1, RF))       # x 14600-15000
   Glaze each to its light slot so the slot finally does its job:
     for x0, x1 in ((LV_X0 - 100, LV_X0 + WALL + 100),
                    (LV_X1 - WALL - 100, LV_X1 + 100)):
         V.append(blk(x0, 13500, FF + 200, x1, 17400, RF - 300))
   = 3.9 x 3.2 m of high-level glazing each side. The upper volume is lit from
   both slots instead of being open to the weather.

5. OPENING FOR THE BRIDGE through the landing's south wall -- 1600 x 2400,
   trimless:
     V.append(blk(BR_X0, WG_Y1 - 300, FF, BR_X1, WG_Y1 + WALL + 300, FF + 2400))

6. GIVE THE ROOM ITS SOUTH FACE -- mirror the north opening, seated sill per the
   research (300-450 for a seated view), head at 2.90 m:
     V.append(blk(LV_X0 + 200, WG_Y0 - CANT - 300, FF + 450,
                  LV_X1 - 200, WG_Y0 - CANT + 400 + 300, FF + 2900))
   5.6 x 2.45 m over the pool. From the hall you now read: compression at
   2.40 m, release into 7.30 m, the bridge crossing high above, and daylight
   through the upper room to the sky over the water.

7. GUARD THE DROPS -- 1,100 mm frameless laminated glass, set back inside the
   room clear of the reveals so the boolean order cannot eat it (60 mm solid in
   the massing model; 21.5 mm laminated in a 15 mm shadow-gapped stainless
   channel in reality):
     S.append(blk(LV_X0 + 400, 13200, FF, LV_X1 - 400, 13260, FF + 1100))  # north
     S.append(blk(LV_X0 + 400, 10200, FF, LV_X1 - 400, 10260, FF + 1100))  # south
     S.append(blk(BR_X0 - 60, BR_Y0, FF, BR_X0, BR_Y1, FF + 1100))         # bridge W
   (Bridge east side needs none -- item 4's wall is its flank.)

8. CORRECT THE AREA ARITHMETIC at :293-296:
     isl = area(LV_X0, WG_Y0 - CANT, LV_X1, WG_Y0 + WALL)   # 20.4, the real one
     br  = area(BR_X0, BR_Y0, BR_X1, BR_Y1)                 # 8.2
     ff  = nb + ww + ew + isl + br                          # 191.6
   Ground 196.0 + first 191.6 + roof 30.0 = GFA 417.6 m2 = 4,495 sq ft against a
   brief of 418 m2 / 4,500 sq ft. Footprint and 28% coverage are unchanged.
   Remaining clear void 3.6 x 5.5 m at 7.30 m, still 5.2 m wide at ground level
   with the gallery reading as a shelf against its east flank (F.LOT's bridge
   across the void; Vertical Courtyard House's bridge carrying circulation).

9. ASSERT IT, so this class of bug cannot come back:
     from shapely.geometry import box as _box
     from shapely.ops import unary_union as _union
     _ff = _union([_box(*r) for r in FF_SLAB])
     assert _ff.geom_type == "Polygon", (
         f"first floor is {len(_ff.geoms)} disconnected pieces: "
         f"{[round(g.area / 1e6, 1) for g in _ff.geoms]} m2")
   I ran this against the current FF_FOOT and it fails with
   "2 disconnected pieces: [20.4, 163.0] m2".

10. NAME IT in villa_sheets.py FIRST so the schedule and the model agree:
     ("FAMILY ROOM OVER POOL", 9400, 9900, 14600, 12500, "habitable"),  # 13.5 m2
     ("GALLERY BRIDGE",       13000, 12900, 14600, 18000, "circulation"),  # 8.2 m2

TWO ADJACENT DEFECTS ON THE SAME LINES, verified while checking this -- fix them
in the same pass:
  * :238 the ground-floor structural glazing void ends at WG_Y0 + 300 = 12800 but
    the wall it must pierce runs y 12500-12900. A 100 mm skin survives across the
    whole 5.6 x 3.3 m opening. Change the y1 term to WG_Y0 + WALL + 300 (13200),
    matching :241.
  * :232-234 the stair is 16 risers x 244 = 3904 mm against a required rise of
    4100 -- it stops 196 mm below the first floor -- and at 244 rise / 170 going it
    pitches at 55.1 deg, against the research's 280 mm minimum going and 30 deg
    max. Item 1's bridge is only as good as what feeds it: re-cut as 17 risers of
    241.2 mm x 300 mm going = 4.80 m run, which fits the 13000-14600 x
    18700-23500 zone.

### Upheld 31

CONFIRMED on every number, and it is not a matter of taste -- it fails the project's own written spec.

GEOMETRY AS MODELLED (villa_3d.py:232-234). blk(x0,y0,z0,x1,y1,z1) with each step = blk(13000, 18700+i*170, GF+i*244, 14600, 18870+i*170, GF+(i+1)*244). The x span is 1600 (stair width), the y span 170, the z span 244. Step i+1 begins in y exactly where step i ends (18700+170(i+1) = 18870+170i), so the exposed walking surface of every tread is 170 mm and the rise between tread tops is 244 mm. Going = 170, riser = 244, pitch = atan(244/170) = 55.13 deg.

AGAINST THE PROJECT'S OWN RESEARCH (VILLA_RESEARCH.md sec.2, "Floating stair"): going >= 280 (luxury 300-320), riser 100-180 (luxury 170), max 30 deg. The model is 39% below the minimum going and 36% above the maximum riser, at 55 deg -- steeper than a ship's ladder and outside every domestic code (UK Part K private stair: max rise 220, min going 220, max pitch 42 deg; IRC: max riser 196, min tread 254).

ARITHMETIC DOES NOT CLOSE. GF = 900, FF = GF + GF_CH + SLAB = 900 + 3600 + 500 = 5000, so the rise is 4100. 16 x 244 = 3904; the last tread top lands at z = 4804, 196 mm below the first floor. There is no 17th step (17 x 244 = 4148 overshoots). So the flight terminates at an odd 196 mm riser -- non-uniform risers, a code violation in its own right -- or it does not reach the floor at all.

WELL SIZE. The void blk(13000, 18700, 4500, 14600, 21900, 5000) is 1.6 x 3.2 m = 5.12 m2 against the research schedule's "Stair per floor 14-18 m2". The flight itself runs only 16 x 170 = 2720 mm in y. A compliant flight needs 24 risers at 170.83 and 23 x 300 = 6900 mm of run -- 2.5x what is provided.

TWO FURTHER FAULTS THE CRITICISM UNDERSTATES.
(1) The 16 boxes are not a connected solid. Block i's bottom face sits at z = 900+244i over y 18700+170i..18870+170i; block i-1's top face is at the same z but over y 18530+170i..18700+170i. They share exactly one line (y = 18700+170i, z = 900+244i) -- edge contact, zero face contact. Only block 0 rests on the ground slab; blocks 1-15 are unsupported, and x 13000-14600 touches no wall (the hall's east partition is at 15425, 825 mm clear). The research explicitly requires an RC supporting wall with tread stubs embedded 250-350 mm; there is no wall at all.
(2) The stair is invisible in the drawing set. The GF plan is cut at GF+1200 = z 2100, which intersects only block 4 (z 1876-2120), so A-201 shows one isolated 1600 x 170 bar in the entrance hall -- no going lines, no up-arrow, no break line. SECTION AA is cut on the water axis at x = 12000, so it misses the stair (x 13000-14600) entirely. villa_sheets.py GROUND/FIRST schedules contain no stair entry, and ENTRANCE HALL is measured over 8575,20550-15425,23600 = 20.9 m2, which is only the strip north of the stair; the 18400-20550 band the stair sits in is unlabelled and uncounted.

RELATED, AND ARGUABLY WORSE: there is no vertical circulation to the semi-basement at all. The only voids cutting the ground slab are the sunken courtyard (CT, x 9500-14500, y 15400-19400) and the two light slots. No stair, no ramp, no lift shaft -- the 142 m2 of staff accommodation and plant is unreachable as modelled, and the research schedule's "stair+lift 18 / lift shaft 1.6 x 1.7 m internal" is nowhere in the file.

WHERE THE CRITICISM'S OWN FIX IS WRONG. Its 2R+G check would not have caught this: 2(244)+170 = 658, inside the 550-700 band. The check must test R and G individually. And its proposed location -- "against the double-height volume's east wall" -- is not available: LV_X1 = 15000 and the east light slot V.append(blk(15000, 12200, 400, 16000, 18300, 9200)) is a full-height void immediately outside that wall, so a flight there stands in the slot. Its half-turn is also unbuildable as described: a 3300 + 1400 = 4700 mm well in a hall only 5200 mm deep internally (y 18400-23600) leaves a 500 mm arrival landing at whichever end the top flight terminates, and blanks the whole 5.2 m side partition that carries the hall-to-majlis door (GF) and the landing-to-suite door (FF).

**Corrected fix:**

1. TREAD GEOMETRY (the non-negotiable part). Rise FF - GF = 4100 mm. Use 24 risers at 170.833 mm and a 300 mm going, 23 goings, flight width 1400 mm.
   pitch = atan(170.833/300) = 29.66 deg (<= 30 research max)
   2R + G = 641.7 (600-650 "ideal" band)
   riser 170.8 = the luxury 170 target; going 300 = luxury 300-320
   nosing 25-38 mm, treads 30 mm honed limestone on cast-in stubs.

2. CONFIGURATION -- quarter-turn (L), not a half-turn, so the well does not consume a full 5.2 m side partition and the arrival landing is real. Unequal flights put the turn where the plan has room.
   Flight A: 14 risers, 13 goings x 300 = 3900 run, 1400 wide, against the hall's west partition at x 8575-9975, ascending SOUTH from y 23600 (z 900) to y 19700 (z = 900 + 14 x 170.833 = 3291.7).
   Quarter landing: x 8575-9975, y 18300-19700 (1400 x 1400) at z 3291.7.
   Flight B: 10 risers, 9 goings x 300 = 2700 run, 1400 wide, y 18300-19700, running EAST from x 9975 (z 3291.7) to x 12675 (z 5000 = FF).
   Arrival landing on FF: x 12675-15425, i.e. 2750 mm deep -- comfortably over the 1400 mm flight width.
   Plan area: 1.4x3.9 + 1.4x1.4 + 2.7x1.4 = 11.2 m2 of flights and landings on GF, ~14 m2 counting the FF void and arrival -- inside the researched 14-18 m2.

3. THE AXIS IS PRESERVED, AND THE STAIR NOW MAKES THE THRESHOLD. Flight B crosses the water axis x = 12000 at z = 3291.7 + 6.75 x 170.833 = 4445; with a 200 mm structural depth the soffit is 4245, giving 3345 mm clear above GF -- above the 3300 mm head of the guest entrance (GF + 2400). The entry axis from the rill runs unbroken beneath the top flight into the 7.30 m volume. Under the quarter landing the soffit is 3092 (2192 clear), which is the researched 2.1-2.4 m compression, used deliberately at the kitchen door.

4. DAYLIGHT ON THE STAIR (the Interlude House move the scheme cites but does not execute). Void the FF slab over x 8575-9975, y 18300-20970 and over x 9975-12675, y 18300-19700; cut a rooflight in the roof slab (z 8700-9200) over x 8900-12400, y 18500-20600. Light drops the full 8.3 m from roof to hall floor down the flights. The FF floor retained at x 8575-9975, y 20970-23600 keeps the landing-to-bedroom-3 door (x 8425-8575, y 21500-22700) on solid floor.

5. CONSEQUENTIAL PLAN MOVES (all one-line edits in villa_3d.py):
   - Guest WC from (8575, 18400, 10400, 20400) to (13600, 18400, 15425, 20400) -- identical 3.65 m2, and it clears the GF hall-to-majlis door at y 20500-21700.
   - GF hall-to-kitchen door from (8425, 21500, 8575, 22700) to (8425, 18450, 8575, 19650), passing under the quarter landing.
   - Partition (8425, 18400, 8575, 23600) becomes a 200 mm RC wall, not the 150 mm stud, over y 18300-23600: research requires RC for a cantilevered stair, stubs embedded 250-350 mm.
   - Add a 1100 mm balustrade line along the FF void edges (currently no guarding is modelled anywhere).

6. VALIDATION IN build() -- test R and G individually, since 2R+G alone passes the broken stair (658):
   import math
   N_RISERS, GOING = 24, 300.0
   RISER = (FF - GF) / N_RISERS
   assert abs(N_RISERS * RISER - (FF - GF)) < 1e-6, "risers must close on FF"
   assert 100.0 <= RISER <= 180.0, RISER
   assert GOING >= 280.0, GOING
   assert 550.0 <= 2 * RISER + GOING <= 700.0
   assert math.degrees(math.atan2(RISER, GOING)) <= 30.0
   assert FLIGHT_W >= 1100.0
   Build the treads from RISER/GOING rather than the literals 244/170, and give each tread a face-to-face bearing into the RC wall so the union is a connected solid instead of 16 edge-touching boxes.

7. SEPARATELY, AND REQUIRED: add a second flight from GF down to the semi-basement (BASE_FL = -2800, rise 3700 = 22 risers at 168.2 with the same 300 going, or 24 at 154.2), plus the 1600 x 1700 lift shaft the research schedules. As modelled the 142 m2 basement has no means of access.

### Upheld 32

CONFIRMED by solid-boolean test on the built model, not by reading the source. I built the model from C:\Users\asdfv\autocad-mcp\villa_3d.py (build123d 0.11.1) and intersected each opening's 400 mm wall band with the finished solid. Residual volume in the band is the test: 0 = pierced, >0 = blocked.

  opening                          band m3   residual m3   % blocked
  GF living structural glazing       7.392       1.8480       25.0%
  FF cantilever island window        5.824       0.0000        0.0%   PIERCED
  GF west wing window                2.756       0.6890       25.0%
  FF west wing window                2.340       0.5850       25.0%
  GF east wing window                2.756       0.6890       25.0%
  FF east wing window                2.340       0.5850       25.0%
  GUEST ENTRANCE DOOR                1.440       0.3600       25.0%
  SERVICE ENTRANCE DOOR              1.056       0.2640       25.0%
  W clerestory band                  1.144       0.0000        0.0%   PIERCED
  E clerestory band                  1.144       0.0000        0.0%   PIERCED

25.0% of a 400 mm band is exactly 100 mm. A y-scan on the west-wing window centreline (x=5500, z=2000, 50 mm steps) returns solid only at y=12800 and y=12850 and void either side, so the residual skin is y 12800-12900 precisely.

The mechanism is as described. WALL = 400.0 (line 80). shell() builds the ring as fp - offset(fp, -400), so the wings' and living volume's south wall band occupies y 12500-12900, the north bar's entrance face 23600-24000, its east face x 20600-21000. Every void's inner face is written against a literal 300: WG_Y0 + 300 = 12800 (lines 239, 243, 244), NB_Y1 - 300 = 23700 (line 248), HX1 - 300 = 20700 (line 257). Each stops 100 mm short. The one opening that works, line 241, is the only one written as WG_Y0 + WALL + 300 -- the reviewer identified the tell correctly.

Independent cross-check: applying the fix drops model volume from 835 m3 to 830 m3, and the seven residual slabs sum to 1.848 + 0.689 + 0.689 + 0.585 + 0.585 + 0.360 + 0.264 = 5.02 m3. The arithmetic closes.

The rendered section corroborates it: in VILLA_SECTION_AA.png the north (entrance) wall is an unbroken vertical line through the full door height -- a 100 mm sliver plots as one line at that scale, which is exactly why the defect survived review of the drawings.

Both entrance doors are sealed, so the "cannot be entered" claim holds literally. Three corrections to the reviewer's numbers, none of which change severity: 7 openings are blocked, not 8 (their own evidence list contains 7 items); the blocked area is 50.2 m2, not 60.1 m2 (they applied the GF sill/head to the FF windows, which are 2.6 x 2.25 m = 5.85 m2, not 2.6 x 2.65 m); and "cannot be seen out of" overstates slightly -- the double-height family living volume is still open to the sky through the two 1.0 m light slots, which are cut full height through the roof slab, so the villa is not hermetic. Every habitable room's actual window, however, is blind, and the formal dining room and study have no other light source at all.

SEPARATE DEFECT FOUND WHILE VERIFYING THE FIX, and it changes what the fix should be. Unblocking the service door where it currently sits makes the design worse. The door is on the east face (HX1, y 18700-19800), but the kitchen is on the WEST side of the north bar: villa_sheets.py GROUND puts SHOW KITCHEN at x 3400-8425 and WOMEN'S MAJLIS at x 15575-20600, both spanning y 18400-23600. So the service door opens directly into the women's majlis at its south-east corner, straight through the most privacy-sensitive room in the brief, and contradicts the docstring's own stated intent ("service on the east boundary reaching the dirty kitchen without crossing guest or family space"). It is a mirror error: the door is on the correct face for the plan that was described, and the wrong face for the plan that was drawn. While the door was blocked this was invisible. The corrected fix therefore moves it as well as pierces it -- verified clear, since the west brise-soleil fins stop at y=17780, south of NB_Y0 = 18000.

**Corrected fix:**

Verified by rebuild: all eight openings return 0.00000 m3 residual after this change, and the printed metrics (GFA 407 m2, footprint 196 m2, coverage 28%, DH 7.30 m, cantilever 3.0 m) are untouched.

1. PIERCE THE FIVE VOIDS. Change only the INNER-face term; leave the outer-face 300 alone, since that 300 mm projection into open air is what guarantees a clean break of the outer face.

  line 239  WG_Y0 + 300      ->  WG_Y0 + WALL + 100      12800 -> 13000   (GF structural glazing, 5.6 x 3.3 m)
  line 243  WG_Y0 + 300      ->  WG_Y0 + WALL + 100      12800 -> 13000   (GF wing windows, 2.6 x 2.65 m each)
  line 244  WG_Y0 + 300      ->  WG_Y0 + WALL + 100      12800 -> 13000   (FF wing windows, 2.6 x 2.25 m each)
  line 248  NB_Y1 - 300      ->  NB_Y1 - WALL - 100      23700 -> 23500   (guest door, 1.5 x 2.4 m)
  line 257  HX1  - 300       ->  HX0  + WALL + 100       20700 -> 3500    (service door, see item 2)

Each void now spans the full 400 mm band plus a 100 mm over-cut past the inner face. Head and sill heights all stay clear of structure: the GF glazing head at GF+3400 = 4300 leaves a 200 mm downstand under the 4500 slab soffit; GF wing heads at 4000 leave 500 mm; FF heads at 7700 sit 1000 mm under RF. Line 241 already works and needs no edit.

2. MOVE THE SERVICE DOOR TO THE WEST FACE. Do not merely unblock it. Replace line 257-258 with:

    V.append(blk(HX0 - 300, NB_Y0 + 700, GF, HX0 + WALL + 100,
                 NB_Y0 + 1800, GF + 2400))                 # service entrance

That is x 2700-3500 crossing the west band 3000-3400, y 18700-19800 (1.1 m leaf), z GF to GF+2400. It opens into the show kitchen at 3400 instead of into the women's majlis at 20600, which is what the docstring already claims the plan does. The 3.0 m west setback minus the 350 mm boundary wall leaves a 2.65 m service side yard, and the brise-soleil fins end at y=17780 so there is no clash.

3. MAKE THE CLASS OF BUG UNREPRESENTABLE. The reviewer's pierce() instinct is right; here is a form that works for all four faces, since two of them run inward in -y/-x:

    def pierce(band, a0, z0, a1, z1, out=300.0, over=100.0):
        """Cut an opening through a wall band. band = (axis, outer, inner);
        inner is outer +/- WALL, so an opening can never be dimensioned
        independently of the wall it has to cross."""
        ax, outer, inner = band
        d = 1.0 if inner > outer else -1.0
        c0, c1 = outer - d * out, inner + d * over
        lo, hi = min(c0, c1), max(c0, c1)
        return (blk(a0, lo, z0, a1, hi, z1) if ax == 'y'
                else blk(lo, a0, z0, hi, a1, z1))

    S_WING = ('y', WG_Y0, WG_Y0 + WALL)          # 12500 -> 12900
    S_ISL  = ('y', WG_Y0 + WALL, WG_Y0)          # island north face, 12900 -> 12500
    N_BAR  = ('y', NB_Y1, NB_Y1 - WALL)          # 24000 -> 23600
    W_BAR  = ('x', HX0,  HX0 + WALL)             #  3000 ->  3400
    E_BAR  = ('x', HX1,  HX1 - WALL)             # 21000 -> 20600

    V.append(pierce(S_WING, LV_X0 + 200, GF + 100, LV_X1 - 200, GF + 3400,
                    out=CANT + 300))
    V.append(pierce(S_ISL,  LV_X0 + 200, FF + 300, LV_X1 - 200, FF + 2900))
    for x0, x1 in ((4200.0, 6800.0), (17200.0, 19800.0)):
        V.append(pierce(S_WING, x0, GF + 450, x1, GF + 3100))
        V.append(pierce(S_WING, x0, FF + 450, x1, FF + 2700))
    V.append(pierce(N_BAR, AXIS - 750, GF, AXIS + 750, GF + 2400))
    V.append(pierce(W_BAR, NB_Y0 + 700, GF, NB_Y0 + 1800, GF + 2400))

4. ADD THE ASSERTION, which is what would actually have caught this. At the end of build(), intersect each declared opening's band with the finished model and fail loudly:

    for name, bx in OPENING_BANDS:            # (name, blk(...)) per opening
        r = (model & bx)
        r = r.volume if r is not None else 0.0
        assert r < 1e3, f"{name}: {r/1e9:.3f} m3 of wall left across the opening"

The 100 mm skin is invisible in plan and reads as a single line in section, so no drawing review will find it. Only a volume test will. This is the same shape as the reset-after-set bug in the project notes: a constant standing in for a parameter, in geometry that looks correct at plot scale.

### Upheld 33

CONFIRMED -- and the built condition is worse than the reviewer states. I could not refute any part of the core claim.

Geometry as coded (villa_3d.py lines 232-235): each step is blk(13000, 18700+i*170, GF+i*244, 14600, 18870+i*170, GF+(i+1)*244) for i in range(16). The blocks are contiguous in y with no overlap, so the tread depth IS the going: going 170, riser 244. Pitch = atan(244/170) = 55.13 deg. Against VILLA_RESEARCH.md section 2 ("Going >= 280 mm (luxury 300-320); riser 100-180 (luxury 170); max 30 deg") that is 110 mm short on going, 64 mm over on riser, and 25 deg over the stated maximum. It is also outside every domestic code maximum (UK Part K 42 deg / 220 riser / 220 going; IRC 196/254 = 37.7 deg). Note the trap: 2R+G = 658 here, so a check on 2R+G ALONE passes this stair -- R and G must be tested individually, as the proposed fix says.

It does not arrive. GF 900 -> FF 5000 = 4100 rise; 16 x 244 = 3904, topping out at z 4804, 196 mm short. But the stairwell void V.append(blk(13000, 18700, GF+GF_CH, 14600, 21900, FF)) spans z 4500-5000 over the whole stair in plan, and is subtracted after the union. It therefore deletes step 15 entirely (4560-4804) and the top 60 mm of step 14. The highest solid tread left in the model is z 4500 -- 500 mm below the first floor, reached by a final 184 mm stub riser. So as modelled the stair is 500 mm short, not 196.

The bottom is clipped too. The sunken-court void blk(CT_X0=9500, CT_Y0=15400, BASE_FL, CT_X1=14500, CT_Y1=19400, GF+200) removes an 1500 x 170 x 200 chunk of step 0, and removes the ground slab (z 400-900) over x 13000-14500, y 18700-19400 -- the first four treads stand over an open 4 m drop to the basement.

Well size confirmed: flight 1600 x 2720 = 4.35 m2, void 1.6 x 3.2 = 5.12 m2, against the research schedule's "Stair per floor 14-18 m2" (section 5). At a compliant 300 going the 4100 rise needs 24-25 risers and 6.9-7.2 m of run, which cannot be straight in a 5.2 m deep hall -- a half-turn is forced, and it needs ~14.5 m2 at the researched 1100-1400 flight width. The reviewer's 2.3 x 4.5 = 10.3 m2 is the minimum-width version; the number is right in kind.

Corroborating symptoms nobody has caught: the GF plan is cut at z = GF+1200 = 2100, which passes through step 4 only, so A-201 renders the stair as a single 1600 x 170 sliver -- the drawing does not show a stair at all (visible in A-201_GROUND_FLOOR_PLAN.png). villa_sheets.py deducts nothing for it: ENTRANCE HALL is scheduled 8575,20550-15425,23600 = 20.9 m2 with the stair's top 870 mm sitting inside it, and FIRST-floor LANDING is scheduled 35.6 m2 with the 5.12 m2 well not deducted. There is also no stair at all between the semi-basement (-2800) and ground, and none to the roof pavilion, so the staff/plant level and the pavilion are unreachable.

Two small corrections to the criticism, neither of which changes the verdict: (1) the stair is not against the hall's east wall -- it sits at x 13000-14600 with an 825 mm gap to the hall/majlis partition at x 15425, i.e. floating in the throat, which is worse, not better; (2) the double-height volume is 7.30 m clear (RF - SLAB - GF), not 7.80 m.

This is a defect, not a matter of taste: the element is unbuildable, non-compliant with the project's own research, and geometrically fails to connect the two floors it exists to connect.

**Corrected fix:**

Replace the 16-block ladder with a half-turn stair in a proper core on the east side of the hall, off the entrance axis, with its mid-landing forming a balcony into the double-height volume.

RISER/GOING (exact, no rounding drift). 4100 rise = 25 risers x 164.0 mm exactly (4100 = 2^2 x 5^2 x 41; 24 x 170.83 does not divide, and a non-integer riser is unbuildable setting-out). Going 300.0. 2R+G = 628 (research ideal 600-650); pitch atan(164/300) = 28.66 deg (<= 30); riser 164 inside the 100-180 band; going 300 inside luxury 300-320. Flight clear width 1400 (research 1100-1400).

CORE. Well x 12525-15425 (2900 = 1400 + 100 well slot + 1400), y 18500-23500 (5000). Area 14.5 m2 -- inside the researched 14-18 m2. East edge lands exactly on the existing hall/majlis partition line x 15425; thicken that wall to 200 mm RC over y 18400-23600 (research: "supporting wall must be RC, not blockwork" for cast-in treads).

FLIGHT A (east, x 14025-15425), 13 risers rising SOUTH. Bottom riser face at y 23500. Tread i (i = 1..12): y from 23500 - i*300 to 23500 - (i-1)*300, top z = 900 + i*164. Run 3600.
MID-LANDING x 12525-15425, y 18500-19900 (1400 deep = flight width), top z = 900 + 13*164 = 3032, 200 mm RC slab (soffit 2832 -- 2.83 m clear headroom under it at ground, the throat into family living). This landing sits on the y 18400 junction with the double-height volume: glaze its south edge with a frameless glass balustrade so the turn is where the 7.30 m clear volume opens up.
FLIGHT B (west, x 12525-13925), 12 risers rising NORTH. First riser face at y 19900; tread j (j = 1..11): y from 19900 + (j-1)*300 to 19900 + j*300, top z = 3032 + j*164. The 12th riser arrives at z = 3032 + 12*164 = 5000.0 exactly, at y 23200. Run 3300. Arrival strip y 23200-23600 stays solid slab.
FF SLAB OPENING (replaces the current void): blk(12525, 18500, GF+GF_CH, 15425, 23200, FF). Landing area on the first floor becomes 35.6 - 13.6 = 22.0 m2, still ample against the research (family landing 12 + circulation 13).

DAYLIGHT -- the move the design basis cites but does not execute. Nothing sits above flight A, so run a 1200 x 2900 rooflight in the roof pavilion (PV = 9000,19000-15000,24000, which already sits directly over this core) on the well centreline x 12525-15425, and let the light fall the full 12.5 m from pavilion roof to ground. That, plus the mid-landing balcony, is the Interlude House clerestory-over-the-stone-stair move.

DOWN AND UP, so the core actually serves the building. Basement: set BASE_FL = -2708.0 (from -2800) so the basement rise is 3608 = 22 x 164 -- one riser dimension throughout. Half-turn 11 + 11 in the same 2900 x 5000 well: run 10 x 300 = 3000 + 1400 landing = 4400, fits. Basement clear height becomes 3108 mm, still inside the researched 2.7-3.3 m excavation and well over the 2.4 m plant-room requirement. Continue the same core FF -> roof pavilion for the stair head.

COORDINATION, mandatory with this fix (pre-existing, exposed by it). The sunken court CT (9500, 15400, 14500, 19400) currently punches the ground slab 1400 mm into the north bar, under the entry throat and under the new mid-landing. Trim to CT_Y1 = 18500 and CT_Y0 = 14500 (5.0 x 4.0 = 20 m2, matching the printed figure) and move BS_Y0 from 15000 to 14500 so the court stays inside the basement footprint (basement 18.0 x 9.5 - 20 = 151 m2).

GUARD RAIL IN CODE -- add to build() before the boolean, so this class of error cannot recur:

    def check_flight(z0, z1, n, going, width=1400.0, name=""):
        rise = (z1 - z0) / n
        assert abs(n * rise - (z1 - z0)) < 1e-9, f"{name}: {n} x {rise} != {z1-z0}"
        assert 100.0 <= rise <= 180.0, f"{name} riser {rise}"      # research S2
        assert going >= 280.0, f"{name} going {going}"             # research S2
        assert 550.0 <= 2 * rise + going <= 700.0, f"{name} 2R+G"
        assert math.degrees(math.atan2(rise, going)) <= 30.0, f"{name} pitch"
        assert 1100.0 <= width <= 1400.0, f"{name} width {width}"
        return rise

Call it as check_flight(BASE_FL, GF, 22, 300.0, name="basement") and check_flight(GF, FF, 25, 300.0, name="ground-first"). Assert R and G separately, not only 2R+G -- the existing ladder passes 2R+G = 658 while being a 55-degree ladder. Add one more assertion that no stair solid intersects any void in V, which is what silently ate the top two treads and the bottom step.

DRAWING FIXES. Cut the GF plan high enough to show the flight and add a break line and UP arrow (the current z = GF+1200 cut renders one 170 mm sliver). In villa_sheets.py deduct the core from both schedules: ENTRANCE HALL drops from 20.9 to ~19.5 m2 net, LANDING from 35.6 to 22.0 m2, and add a "STAIR CORE 14.5 m2" entry to both floors so the printed GFA and the room schedule agree with the model.

### Upheld 34

CONFIRMED -- I tried to refute this and could not. Every number in the criticism reproduces exactly.

1. The first-floor footprint really is two pieces. `shapely.unary_union` of the four FF_FOOT rectangles (villa_3d.py:140-142) returns a MultiPolygon: a 163.0 m2 body (bounds 3000,12500 - 21000,24000) and a 20.4 m2 island (bounds 9000,9500 - 15000,12900), minimum separation 1000.00 mm. The same test on GF_FOOT returns a single 196.0 m2 Polygon, so the ground floor is connected and the first floor is not. The gap is the 1.0 m light slot, and that slot is voided full height (villa_3d.py:174-177, z 400 to 10300), so the two pieces cannot touch at any level below the roof.

2. Nothing bridges it. FF_FOOT has no rectangle at x 9000-15000, y 12900-18000, and villa_3d.py:162 explicitly removes the slab over the living volume, so the nearest first floor to the north is the north bar at y 18000 -- 5100 mm away. I read the whole file: the only stair is the single 16-tread run at villa_3d.py:232-234, entirely inside the north bar. There is no bridge, landing, ladder or second flight anywhere.

3. The only opening is exactly as described. villa_3d.py:240-241 cuts x 9200-14800, y 12200-13200, z 5300-7900 -- a 5600 x 2600 hole that fully removes the 400 mm north wall band (y 12500-12900). Its sill is 300 above the room's own floor (FF = 5000) and 4400 above the living-room floor (GF = 900); the fall from the room's floor is 4100 mm. No balustrade solid exists in the script.

4. The area really is counted. `ct = area(LV_X0, WG_Y0 - CANT, LV_X1, WG_Y0)` = 6000 x 3000 = 18.0 m2, and `ff = nb + ww + ew + ct` = 108 + 27.5 + 27.5 + 18 = 181.0, matching the printed first-floor figure and the 407 m2 / 4,381 sq ft headline. The room is also absent from villa_sheets.py's FIRST schedule (lines 36-44) -- it has no name and no program, which is the giveaway that it was never resolved rather than simply left undrawn.

Two findings that make it worse than the reviewer states, both verified arithmetically:

(a) The sole physical connection to the rest of the building is the roof slab. villa_3d.py:165 spans x 3000-21000, y 9500-24000 at z 8700-9200; the slot voids only remove y 12200-18300, so 2700 mm of slab bridges each slot at y 9500-12200. The 20.4 m2 room is therefore hung off a 1.0 m strip of roof slab and bears at first-floor level on nothing but its own four walls -- and those bear, over the 3.0 m projection (y 9500-12500), on the ground-floor south wall band at y 12500-12900, which the ground glazing void (line 238, y 9200-12800) reduces to a 100 mm residual leaf between z 1000 and 4300. So the cantilever is not just unreachable, it has no modelled load path.

(b) The same defect class hits the roof pavilion. PV (30 m2, floor at z 9200) is a sealed shell -- its only void (lines 170-171) is the interior, there is no door opening, and there is no second stair flight from FF to roof. So 18 + 30 = 48 m2, 11.8% of the 407 m2 GFA, is enclosed floor with no modelled access. (Separately, the existing flight is short: 16 x 244 = 4804, i.e. 196 mm below the FF at 5000, on a 170 mm going -- a different defect, but it is the arrival point any fix depends on.)

This is not a matter of taste. A 20.4 m2 walled, floored, glazed enclosure with a 5.6 m unguarded hole over a 4.1 m drop, credited 18 m2 in the headline GFA, that no occupant can enter, is a fatal defect in the design as modelled.

**Corrected fix:**

The reviewer's diagnosis is right; I would take his first branch (make it habitable), not the canopy branch -- deleting 18 m2 pushes GFA to 389 m2, further from the 418 m2 / 4,500 sq ft brief, and throws away the best room in the scheme. Give the cantilever a program (POOL GALLERY, 5.2 x 2.6 m = 13.5 m2 clear) and return the first-floor slab to it on the stair's own line, so the bridge reads as the stair continuing south rather than as an add-on.

All coordinates in villa_3d.py's grid, mm.

1. GALLERY BRIDGE -- 1600 overall x 5100 span, aligned exactly with the stair (x 13000-14600), hugging the east side of the living volume so the double-height room is not bisected.
   BR_X0, BR_X1 = 13000.0, 14600.0
   BR_Y0, BR_Y1 = WG_Y0 + WALL, NB_Y0          # 12900 -> 18000
   S.append(blk(BR_X0, BR_Y0, GF + GF_CH, BR_X1, BR_Y1, FF))     # 500 slab, z 4500-5000
   Guards, 100 thick x 1100 high, both edges (both sides are open drops):
   S.append(blk(BR_X0, BR_Y0, FF, BR_X0 + 100, BR_Y1, FF + 1100))
   S.append(blk(BR_X1 - 100, BR_Y0, FF, BR_X1, BR_Y1, FF + 1100))
   Clear walking width 1400. Head height under the roof soffit 8700 - 5000 = 3700.

2. TRIM THE DOUBLE-HEIGHT VOID so the batched subtraction does not delete the new slab. Because `model = (Part() + S) - V` applies all voids last, line 162 must be narrowed in x AND pulled off the cantilever's bearing in y:
   replace  V.append(blk(LV_X0 + WALL, WG_Y0,        GF + GF_CH, LV_X1 - WALL, WG_Y1, FF))
   with     V.append(blk(LV_X0 + WALL, WG_Y0 + WALL, GF + GF_CH, BR_X0,        WG_Y1, FF))
   i.e. x 9400-13000, y 12900-18000. Moving y0 from 12500 to 12900 also stops the void eating the 500 mm slab strip under the cantilever's north wall -- the (a) bearing problem above.
   Result: the double-height void is 3.6 x 5.1 m at 7.30 m clear (compression ratio 1:3.0 unchanged), with a 4.5 m soffit over the 1.6 m seating strip beneath the gallery -- the low-ceiling zone against the tall one is what makes the tall one read.

3. REPLACE THE UNGUARDED 5.6 m HOLE (lines 240-241) with a door plus a high-sill screen. Delete that void and substitute:
   V.append(blk(13100.0, WG_Y0 - 300, FF,        14500.0, WG_Y0 + WALL + 300, FF + 2400))   # 1400 x 2400 door, centred on the bridge
   V.append(blk(9200.0,  WG_Y0 - 300, FF + 1100, 13100.0, WG_Y0 + WALL + 300, FF + 2900))   # 3900 x 1800 internal screen
   The 400 mm RC wall below the screen is now a 1100 mm solid upstand -- a compliant guard at the void edge, no separate balustrade needed, and the room still overlooks the double-height living room.

4. ROOF PAVILION -- same defect, same class of fix: a switchback second flight in the existing 1600 x 3200 core, FF 5000 to roof 9200 = 4200 rise, two flights of 12 risers at 175 with 11 goings at 260 (2860 run each) either side of a 1200 half-landing, total 1600 x 4060, which fits the landing's 5200 mm depth. Add a door void to the pavilion shell (lines 169-171), which currently has none.

5. NUMBERS AFTER THE FIX
   bridge 1.6 x 5.1 = 8.2 m2 (circulation)
   first floor 181.0 + 8.2 = 189.2 m2; GFA 196.0 + 189.2 + 30.0 = 415.2 m2 = 4,469 sq ft -- closer to the 418 m2 / 4,500 sq ft brief than the current 407, and now every square metre of it is enterable.
   Ground floor, footprint, coverage (28%), pool and cantilever figures are unchanged.

6. SCHEDULE (villa_sheets.py) -- add to FIRST so the orphan is named and its area computed, not asserted:
   ("POOL GALLERY",   9400, 9900, 14600, 12500, "habitable")     # 13.5 m2
   ("GALLERY BRIDGE", 13000, 12900, 14600, 18000, "circulation") # 8.2 m2

7. ASSERTIONS in build() -- write them on the FLOOR footprint (slab + bridge), not on FF_FOOT, which only drives walls:
   from shapely.geometry import box as _box
   from shapely.ops import unary_union
   ff_floor = unary_union([_box(*r) for r in FF_FOOT] +
                          [_box(BR_X0, BR_Y0, BR_X1, BR_Y1)])
   assert ff_floor.geom_type == "Polygon", \
       f"first-floor slab is in {len(ff_floor.geoms)} pieces"
   circ = unary_union([_box(8575, 18400, 15425, 23600),          # landing
                       _box(BR_X0, BR_Y0, BR_X1, BR_Y1)])        # bridge
   for name, x0, y0, x1, y1, _k in FIRST:
       assert _box(x0, y0, x1, y1).intersects(circ) or <door in DOORS_FF on its boundary>, \
           f"{name} is not reachable from the landing"
   And the same connectivity test at roof level, which is what catches the pavilion.

### Upheld 35

The claim checks out exactly against the model, and it is worse than stated.

VERIFIED FROM CODE (villa_sheets.py:36-44, villa_3d.py:205-220):
- First-floor room schedule, areas recomputed from the rectangles:
  BEDROOM 3 5.025x5.200 = 26.13; LANDING 6.850x5.200 = 35.62; MASTER BEDROOM 2.850x3.200 = 9.12; DRESSING 2.025x3.200 = 6.48; MASTER ENSUITE 5.025x1.850 = 9.30; BEDROOM 1 4.200x5.350 = 22.47; BEDROOM 2 4.200x5.350 = 22.47. Net 131.59 m2.
- Exactly one entry is tagged "wet" on the first floor: MASTER ENSUITE, 9.30 m2. There is no other WC, bathroom or shower anywhere above ground level except the ground-floor GUEST WC (8575,18400 to 10400,20400 = 1.825x2.000 = 3.65 m2). So a 407 m2 GFA, 4-bedroom villa has two WCs in total.
- The one first-floor bathroom is inside the master suite. PARTS_FF wall (15575,21600,20600,21750) closes the en-suite off the whole north bar, and its only door, DOORS_FF (16200,21600,17400,21750), sits at x 16200-17400, which lies inside the dressing room's x-range (15575-17600). The landing door (15425,20200,15575,21400) also lands in the dressing. So the route from the landing to the only first-floor WC is landing -> master dressing -> en-suite. Bedrooms 1, 2 and 3 have no en-suite, no wardrobe and no WC on their floor; the nearest facility is one storey down, off the entrance hall, past the guest route.

TWO ADDITIONAL DEFECTS THE SAME PARTITION LAYOUT PRODUCES, both of which make refutation impossible:
- The "master bedroom" is 2.85 x 3.20 = 9.12 m2, smaller than every other bedroom in the house and a third of VILLA_RESEARCH.md:317's master-bed range of 28-35 m2 (master suite total 55-75; the modelled suite is 9.12+6.48+9.30 = 24.9 m2).
- DOORS_FF (5000,18250,6200,18400) and (17800,18250,19000,18400) mean Bedroom 1 is entered only through Bedroom 3, and Bedroom 2 only through the master bedroom. The bedrooms are in enfilade with no independent access.

This is not taste. Against the project's own sourced standard (VILLA_RESEARCH.md:317-318: guest suite 28-35 m2 = bed 18-22 + wardrobe 4-6 + en-suite 6-8) the floor provides zero of the three required guest en-suites. Fatal severity is correct.

Where I depart from the reviewer: their 36 m2 figure over-states the new area needed. It assumes the three bedrooms keep their present size and the rest of the floor is untouchable. In fact 35.62 m2 of LANDING serves a stair whose opening is only 1.6x3.2 = 5.12 m2, and the 26.13 m2 east bar-end is already being wasted on a 9.12 m2 master. Roughly 16 m2 of the requirement can be recovered by reallocation; only about 30 m2 gross has to be added, and the model already builds the roof over exactly where it should go.

**Corrected fix:**

FIX IN THREE MOVES. All dimensions clear internal, mm, on the existing setting-out grid.

MOVE 1 - Extend the first floor 3.0 m south over both wings, into the space the roof already covers.
villa_3d.py:165 already builds the roof slab as blk(HX0, WG_Y0-CANT, RF, HX1, NB_Y1, RF+SLAB) = x 3000-21000, y 9500-24000, with a parapet. But FF_FOOT stops the wings at y 12500, so there is presently a 5.0 x 3.0 m roof plate flying over open garden at each wing with nothing under it. Fill it:
  FF_FOOT wings become (WW_X0, WG_Y0-CANT, WW_X1, WG_Y1) and (EW_X0, WG_Y0-CANT, EW_X1, WG_Y1), i.e. y 9500-18000.
  +15.0 m2 gross per wing (+30 m2 total). Footprint and site coverage are unchanged at 196 m2 / 28% - it is a 3.0 m cantilever, the same depth as the existing central one and inside the RC sweet spot the design already cites. The roof edge at y 9500 now sits on a wall instead of cantilevering.
  Two consequential edits: extend the light-slot voids (villa_3d.py:174-177) south from WG_Y0-300 to WG_Y0-CANT-300 (y 9200), or the two 1.0 m slots close up at the south face and the three cantilevers merge into one 18 m plate; and move the FF wing windows (villa_3d.py:244) from y WG_Y0+-300 to y WG_Y0-CANT+-300 (9200-9800), since y 12200-12800 is now mid-room.
  Wing interior after the change: x 3400-7600, y 9900-18400 = 4.20 x 8.50 = 35.70 m2 each.
  GFA 407 -> 437 m2 (4,704 sq ft). To hold the 418 m2 brief exactly, delete the 30 m2 roof pavilion (PV) and GFA returns to 407 m2 - the bedroom floor is worth more than a roof room.

MOVE 2 - Master suite into the extended east wing; four en-suites; bedrooms 2 and 3 in the bar-ends.
The master belongs at the south, over the pool and garden under the 3.0 m shading soffit, not landlocked in the north bar over the street with only a 650 mm clerestory.
  MASTER (east wing, mirror on x=12000 of the values below): bedroom x 16400-20600, y 9900-14600 = 4.20 x 4.70 = 19.74; en-suite x 18000-20600, y 14600-17300 = 2.60 x 2.70 = 7.02; dressing x 16400-18000, y 14600-17300 = 1.60 x 2.70 = 4.32; suite lobby x 16400-20600, y 17300-18400 = 4.20 x 1.10 = 4.62. Suite total 35.70 m2.
  BEDROOM 1 (west wing, identical): bedroom 19.74 + en-suite 7.02 + walk-in 4.32 + lobby 4.62 = 35.70 m2. Both suites land inside the research's 28-35 m2 guest-suite band.
  BEDROOM 3 (west bar-end, x 3400-8425, y 18400-23600 = 26.13): bedroom x 3400-8425, y 20600-23600 = 5.025 x 3.00 = 15.08; en-suite x 3400-6100, y 18400-20600 = 2.70 x 2.20 = 5.94; wardrobe x 6100-7325, y 18400-20600 = 1.225 x 2.20 = 2.70; access spur x 7325-8425, y 18400-20600 = 1.10 x 2.20 = 2.42.
  BEDROOM 2 (east bar-end, mirrored): same 15.08 / 5.94 / 2.70 / 2.42.
  These two are the compromise: 15.08 m2 bedrooms against the 18-22 m2 target, but with a real en-suite and robe each.

MOVE 3 - Kill the enfilade and add a family bathroom out of the surplus landing.
  Delete PARTS_FF entries (17600,18400,17750,21600) and (15575,21600,20600,21750) and their doors; delete DOORS_FF (5000,18250,6200,18400) and (17800,18250,19000,18400).
  Landing doors move to the spurs: x 8425-8575 at y 18600-19500 (west) and x 15425-15575 at y 18600-19500 (east). Each spur runs 1.10 m south to a door at y 18250-18400 into the wing suite's lobby - so Bedroom 1 and the master are reached past Bedroom 3's and Bedroom 2's doors, never through them. Every one of the four bedrooms now opens off circulation.
  FAMILY BATHROOM / landing WC: x 8575-10400, y 18400-20400 = 1.825 x 2.00 = 3.65 m2, stacked exactly over the ground-floor GUEST WC so the soil stack is vertical. Door off the landing in the y 20400-20550 wall line.
  Landing reduces from 35.62 to 6.850 x 3.100 = 21.24 m2 gross less the 2.24 m2 stair opening = 19.0 m2 net, plus the two 2.42 m2 spurs. That is still 14-18 m2 of stair per floor per the research, and it stays open to the double-height living volume.

RESULT: wet rooms above ground go from 1 to 5 - four en-suites (7.02, 7.02, 5.94, 5.94 m2) plus a 3.65 m2 family WC - and the ground-floor guest WC stays for the majlis. First-floor net 131.6 -> 154.2 m2 for +30 m2 gross.

ONE STACKING CONSEQUENCE TO RESOLVE ON THE GROUND FLOOR: the west bar-end en-suite at x 3400-6100, y 18400-20600 lands over the SHOW KITCHEN, which occupies that whole zone. Cure it by taking a 2.0 m strip off the kitchen's south end - x 3400-8425, y 18400-20400 = 10.05 m2 - as the dirty/wet kitchen and pantry that villa_3d.py:47-48 already promises the service entrance reaches but the room schedule never provides. Show kitchen then reads 3400,20400-8425,23600 = 16.1 m2, still inside the 20-28 band once the pantry is counted with it, and no bathroom sits over food preparation. The east bar-end en-suite lands over the women's majlis, which is fine. The two wing en-suites sit over the formal dining and study; drop those stacks in the 400 mm wall on the light-slot face (x 8000 / x 16000) inside the 500 mm SLAB services zone the model already allows, down to the basement plant.

### Upheld 36

CONFIRMED -- I tried to refute this and could not.

VERIFIED IN CODE (C:\Users\asdfv\autocad-mcp\villa_3d.py):
1. Basement is an undivided shell. Lines 128-132 add a raft, a solid box (3000-21000 x 15000-24000, BASE_FL to GF-SLAB), an interior void inset by WALL=400, and the court void. Interior = 17.200 x 8.200 = 141.04 m2 (I recomputed it), less the 20.0 m2 court. PARTS_GF are extruded GF to GF+GF_CH and PARTS_FF from FF to RF (lines 222-228) -- nothing exists anywhere between z=-2800 and z=+400 except the perimeter ring. I checked every other S/V append: the pool solid stops at y=12900, the rill starts at y=24400, the boundary walls start at z=0. Nothing intrudes into the basement.
2. No access. The stair loop at 232-234 runs GF+0 to GF+16*244 only; V at 235 is the GF->FF void. There is no basement flight, no ramp, no lift, and the basement perimeter wall has no opening cut in it anywhere. Rendering VILLA_PLAN_BASEMENT.png confirms it visually: a plain rectangle, one wall ring, nothing inside.
3. No plant room in the whole project. villa_sheets.py GROUND = kitchen/hall/guest WC/majlis/dining/family living/study; FIRST = 3 bedrooms + master + dressing + ensuite + landing. There is no electrical room, no AHU, no water tank room, no maid's room, no laundry, no store, no pool plant -- on any level. The docstring at lines 24-27 asserts "staff, laundry, store and all plant go into a SEMI-BASEMENT" and the brief requires it; none of it is modelled or scheduled.
4. Pipe run arithmetic is right. Basin void (line 269) is x 9100-14900, y 1600-2600, z -900 to +640 -- centre (12000, 2100), at the FAR REAR of the plot, while the basement is at the STREET end. My orthogonal measurements: 15.25 m to the outer wall face at y=15000, 15.65 m to the inner face at y=15400, 24.25 m to a corner room at either (5000,17000) or (19000,17000). Research limit is 15 m. The rule genuinely binds on the balance tank, not the pool: this is a deck-level overflow pool, the filtration pump draws from the catch basin, and the research says the basin can be the balance tank -- so plant must sit beside the basin, at y~2100, not 13-24 m away at the other end of the site with the run buried under the pool shell.

TWO CORRECTIONS TO THE REVIEWER, neither of which saves the design:
- "Sealed box" is imprecise. The court void (line 132) runs to GF+200 and so cuts a 5.0 x 4.0 m hole clean through the ground slab into the living room/hall floor, and the two light slots (lines 174-177) start at GF-SLAB=400, which is exactly the top of the basement void -- so 2.9 m2 of each slot (x 8000-9000 and 15000-16000, y 15400-18300) opens the basement straight to the sky. The basement is not sealed; it is open to the weather in three places and still has no means of access. That is worse, not better.
- The proposed fix is dimensionally wrong. The 12900-15000 strip is 2.100 m gross; after a 400 mm retaining wall the clear depth is ~1.700 m, and a 0.9-1.2 m diameter filter with the research's own 600-800 mm clearance each side needs >=2.400 m clear. It also puts pumps directly under the double-height family living room, and still leaves ~13 m of buried run under the pool shell.

This is a defect, not taste: the brief names the semi-basement, the design basis claims it, the drawing set publishes a sheet of it, and what is drawn is a 141 m2 void nobody can enter with none of the rooms it is supposed to contain. Fixing it changes the ground floor plan (a compliant stair core costs ~11 m2 of the hall), so it is a scheme-level problem, correctly called fatal at this stage.

**Corrected fix:**

Three moves. Do not put the pool plant in the basement -- the pool is at the rear and the basement is at the street; that is the fight the reviewer's strip loses.

1. POOL PLANT -- a sunken chamber beside the pool, under a new raised deck (kills the pipe run)
   - Clear internal 4.500 (x 4600-9100) x 3.600 (y 3000-6600) = 16.2 m2, inside the research's 12-18 m2. Its east wall IS the pool shell's west wall (already 400 mm water-retaining RC) -- suction and return penetrations are ~1.0 m long on puddle flanges.
   - FFL -2.000, soffit +0.400 = 2.400 m clear, 300 mm roof slab -> deck top +0.700, flush with the pool coping. The deck becomes the 3.5 m lounging side the pool does not currently have (today the pool has only its 400 mm shell rim -- the research calls a 600 mm coping walk "a developer's pool").
   - South face at y 3000 = the rear building line; west outer face at x 4300, i.e. 4.3 m clear of the boundary wall, well outside the 45 degree load-spread zone.
   - Pipe run to the basin centre (12000, 2100, -450): 5.35 m orthogonal to the room, 13.45 m to its far corner. Was 15.65 m minimum / 24.25 m realistic.
   - 4.500 m across takes filter (1.200) + 800 clearance both sides + 1.000 in front of the panel, per the research clearances.
   - Keep the existing catch basin as the balance tank: 5.8 x 1.0 x 0.9 = 5.2 m3 gross, ~3,200 L usable between low-level cut-out and freeboard, against the 1,950 L required (40.7 L/m2 x 47.5 m2) and inside the 1,900-5,700 L trade range. Basin invert -0.900 = 1.6 m below the +0.700 water line (research wants 1.0-1.5); the plant floor at -2.000 is 1.1 m below that invert, giving genuinely flooded suction. Autofill solenoid and float on the basin, not the pool.
   - Access: 2.000 x 2.000 open well at x 4600-6600, y 6600-8600, floor -2.000, 1.100 m wide galvanised stair, 12 risers x 167, going 300 (2R+G = 634). 1.000 m clear door in the north wall. The well is also the heat pump's outdoor air source and the mechanical vent intake/discharge. 300 x 300 sump with duty/standby pump under the floor gully.
   - Acoustics: 12.4 m from the majlis, ~10 m from the nearest bedroom, no shared wall with any habitable room. The strip under the living room fails this; this does not.

2. BASEMENT ACCESS -- one stacked stair core serving basement/ground/first, at x 12925-15425, y 19100-23600 (2.500 x 4.500 = 11.25 m2), against the hall's east partition.
   - Basement to GF: 3.700 m rise, 22 risers x 168.2, going 300, U-return 11+11, 1.200 m flights either side of a 100 mm well, half-landing at -1.516. 2R+G = 636, pitch 29.3 degrees.
   - GF to FF: 4.100 m rise, 24 risers x 170.8, going 300, U-return 12+12. 2R+G = 642, pitch 29.7 degrees. This also replaces the existing flight at lines 232-234, which is 244 rise / 170 going = 55 degrees -- a ladder, not a stair, and non-compliant against the research's own "going >= 280, riser 100-180, max 30 degrees".
   - Pull the sunken court's north edge back to y 19100 so it clears the core: court becomes 5.000 x 3.700 = 18.5 m2. Hall retains ~18.7 m2 (research 18-30) and still opens into the 7.30 m volume.
   - Cap the two light slots at the GF slab line (z 400-900, x 8000-9000 and 15000-16000, y 15400-18300) with fixed glazing or a walk-on grille over a drained sump, so the basement stops being open to the sky.

3. BASEMENT PARTITIONS -- 141.0 m2 shell, 3.200 m clear height (ample; plant needs 2.400). Less court 18.5 and core 11.25 leaves ~111 m2. Schedule to the research's own room sizes, 150 mm partitions, 1.200 m clear corridor off the core:
   maid's room 3.400 x 3.200 = 10.9 (research 9-12), window onto the court; maid's bath 2.000 x 2.000 = 4.0 (3.5-4.5); laundry 3.600 x 2.800 = 10.1 (8-12); store 3.000 x 2.700 = 8.1 (8); electrical/LV + UPS 2.600 x 2.000 = 5.2 (4-6); AHU/FAHU 3.400 x 2.400 = 8.2 (6-10); water tank room 3.400 x 2.400 = 8.2 (6-10), a separate chamber, never shared with electrical; corridor ~16.8. Total ~71.5 m2 plus partitions -- leaves roughly 30 m2 spare for a driver's room (9-12) and WC (3) if the client wants one. Every one of these rooms needs a 1.000 m clear door off the corridor and the electrical and tank rooms need their own; the plant rooms sit in the east band, away from the maid's room.

### Upheld 37

CONFIRMED, and verified against the built solid, not just by reading the source.

The numbers in villa_3d.py:266-270:
  pool shell   S: x[9100,14900] y[2600,12900] z[-1100,700]   (POOL_Y0-400 = 2600)
  interior     V: x[9500,14500] y[3000,12500] z[-700,800]
  "spill+basin" V: x[9100,14900] y[1600,2600] z[-900,640]    (POOL_Y0-1400 = 1600)

The void's north face (2600) is exactly the shell's south face (2600). I built the model and measured with build123d:
  spill n pool shell        = 0.000 m3
  spill n interior void     = 0.000 m3
  spill n WHOLE MODEL       = 0.000 m3   <- it removes nothing from anything
The reviewer's third figure is the decisive one and it holds: the void does not touch the south boundary wall either (that wall is y[0,350]), and it cannot cut "the ground" because no terrace or garden solid is ever modelled. There is no solid anywhere in x[9100,14900] y[1600,2600] z[-900,640]. The boolean is dead code.

Consequences, measured by probing 100x100 columns through the model:
  SOUTH wall top  z = +700
  NORTH wall top  z = +700 (probe returned 1000, contaminated by the house slab above)
  EAST wall top   z = +700
  WEST wall top   z = +700
  probe at y=2000 -> EMPTY;  probe at y=2500 -> EMPTY
So the pool is a sealed 400 mm-walled tank with the rim dead level at POOL_TW = +700 on all four faces. No weir crest, no notch, no gutter, no basin, no balance chamber. That is confirmed in the render: VILLA_SECTION_AA.png shows a symmetric U at the south end with both walls to the same height and nothing beyond it.

Meanwhile villa_sheets.py:72-73 draws a rectangle at exactly the phantom void's footprint and :84-85 letters it "OVERFLOW EDGE + CATCH BASIN". Plan asserts an element the model does not contain, which is precisely the failure the docstring claims the model-once method eliminates.

Severity: I would call it serious rather than fatal. The scheme, the levels and the raised-plinth strategy are all correct and researched (VILLA_RESEARCH.md:21-23 option (b), raised 600-900 mm -> POOL_TW +700 is right); what is missing is roughly 15 lines of geometry. But "overflow pool" is a named item in the brief and the drawing set currently lies about it, so it must be fixed before issue.

Two further defects found while checking, both real:
1. The docstring (villa_3d.py:19-20) says the pool "overflows one LONG side". The pool as built is 5.0 m (x) x 9.5 m (y), so its long sides are the EAST and WEST faces. The basin - in the sheet, in the dead void, and in the axial composition - is on the SOUTH 5.0 m SHORT end. The wording is a leftover from the research's 12.0 x 4.0 m pool (same 48 m2, transposed proportion). The south end is the right answer (it is the terminus of the gate->rill->house->pool axis, it is what Section AA can cut, and it is what the sheet annotates), so the docstring is what is wrong.
2. The reviewer's PROPOSED FIX is itself wrong and must not be applied as written. A void over POOL_Y0-1400 -> POOL_Y0+400 = y[1600,3400] with top at POOL_TW-60 = 640 would delete the entire south wall from z -900 to +640 across the full shell width x[9100,14900], scoop the bottom out of the east and west walls over y[2600,3000], take a bite out of the floor slab, and leave a 60 mm-thick sliver of coping at z[640,700] hanging unsupported. The void must stop at the wall's pool-side face, and the crest must be made by lowering a wall top, not by cutting a slab through it.

**Corrected fix:**

Model the weir and the basin as real geometry. I implemented and built this; it produces 12 new faces, +3 m3 of concrete, and a legible notch in Section AA (image sent).

Note: villa_3d.py does one batched `(Part() + S) - V`, so every void cuts every solid. All x-ranges below are deliberately clipped so a void cannot reach into the side walls.

1. NEW CONSTANTS, replacing BASIN_D = 900.0 at villa_3d.py:98

    WEIR_DROP = 6.0        # crest below water level (research 2-6 mm; 6 = heavy curtain)
    WEIR_T    = 250.0      # RC weir wall at the crest (research 200-250, widening at base)
    BASIN_T   = 250.0      # basin wall and floor thickness
    BASIN_CW  = 850.0      # clear width of the chamber (y)
    BASIN_FL  = -900.0     # chamber floor (top of slab)
    BASIN_Y1  = POOL_Y0 - 400      # 2600 = the spill face (= shell south outer face)
    BASIN_Y0  = BASIN_Y1 - BASIN_CW  # 1750 = clear south face

2. REPLACE villa_3d.py:269-270 (the dead void) WITH:

    # weir wall: 250 at the crest, stepping out to the full 400 below water
    V.append(blk(POOL_X0, POOL_Y0 - 150, POOL_FL + 600,
                 POOL_X1, POOL_Y0, POOL_TW + 100))
    # crest 6 mm below water level, over the 5.0 m spill width only
    V.append(blk(POOL_X0, POOL_Y0 - 400, POOL_TW - WEIR_DROP,
                 POOL_X1, POOL_Y0, POOL_TW))
    # catch basin / balance chamber: a SOLID, with its interior subtracted
    S.append(blk(POOL_X0 - 400, BASIN_Y0 - BASIN_T, BASIN_FL - BASIN_T,
                 POOL_X1 + 400, BASIN_Y1 + 100, STREET))
    V.append(blk(POOL_X0 - 400 + BASIN_T, BASIN_Y0, BASIN_FL,
                 POOL_X1 + 400 - BASIN_T, BASIN_Y1, STREET + 100))

   Why each range is what it is:
   - Weir void x is clipped to POOL_X0..POOL_X1 (9500-14500) so the east and west copings stay at +700 and still contain the water. Only the 5.0 m spill width is notched.
   - The weir void's z starts at POOL_FL+600 = -100, so the wall is 250 mm from -100 up to the crest and the full 400 mm below - "RC wall 200-250 mm at the crest, widening at base".
   - The basin solid's north face is BASIN_Y1+100 = 2700, i.e. 100 mm INSIDE the shell footprint. That guarantees an overlapping union rather than a coincident-face kiss (the exact failure mode of the original line). The overlap region is already shell, so it adds nothing.
   - The chamber void's north face stops at BASIN_Y1 = 2600 so it cannot eat the weir wall. The chamber's north side IS the spill face - correct, the waterwall runs straight down it into the chamber.
   - Chamber void top at STREET+100 = +100 leaves the trough open at terrace level: a visible basin, per the docstring's own intent.

3. RESULT, measured on the built model (probe columns at x = AXIS):
     weir crest        z = +694   (E/W coping +700 -> a real 6 mm differential)
     weir wall         250 at crest, 400 below z = -100
     spill face        694 -> 0, a 694 mm waterwall
     chamber clear     x[9350,14650] y[1750,2600] = 5.30 x 0.85 m, floor -900
     basin slab soffit -1150
     chamber intruding solid = 0.0000 m3 (genuinely hollow)
     usable surge (floor +200 low-level cut-out to 200 freeboard below deck)
                       = 2,252 L  vs  47.5 m2 x 40.7 L/m2 = 1,933 L required. PASSES.
                       = 3.4% of the 66.5 m3 pool (research band 3-8%). PASSES.
     tank invert       1.60 m below WL - 100 mm past the research's 1.0-1.5 m band,
                       in the safe direction (more flooded suction, more gravity head).
     basin outer face  y = 1500 -> 1.50 m from the property line (research: setback
                       typically 1.5 m, verify) and 1.15 m clear of the boundary-wall
                       face at y=350 (research: 0.9-1.5 m clear ground). BOTH PASS.
                       This is why the chamber is 850 wide, not 1000 - at 1000 clear
                       the basin lands at y=1350 and breaks the 1.5 m setback.

4. ALSO CHANGE:
   - villa_sheets.py:72-73: derive BOTH rectangles from the new constants so plan and
     model can never drift again -
       p.box(v3.POOL_X0 - 400, v3.BASIN_Y0 - v3.BASIN_T,
             v3.POOL_X1 + 400, v3.BASIN_Y1, "A-FLOR-OTLN")            # basin outline
       p.box(v3.POOL_X0 - 400 + v3.BASIN_T, v3.BASIN_Y0,
             v3.POOL_X1 + 400 - v3.BASIN_T, v3.BASIN_Y1, "A-FLOR-OTLN")  # chamber
   - villa_sheets.py:84-85: retitle to carry the datum, e.g.
     "WEIR CREST +0.694 / WL +0.700 - CATCH BASIN + BALANCE CHAMBER 2,250 L"
   - villa_3d.py:19-20 docstring: "overflows one long side" -> "overflows its far
     (south) end on the axis", which is what the geometry, the sheet and Section AA
     all actually do.
   - Add a print to build() so the claim is auditable, in the style of the others:
       print(f"  weir       crest {POOL_TW - WEIR_DROP:.0f} vs WL {POOL_TW:.0f} "
             f"({WEIR_DROP:.0f} mm; research 2-6) over {(POOL_X1 - POOL_X0)/1000:.1f} m")
       print(f"  basin      {surge:.0f} L usable vs {47.5 * 40.7:.0f} L required")

5. DO NOT APPLY the reviewer's own proposed void (POOL_Y0-1400 -> POOL_Y0+400 at
   z -900..640, full width). See reasoning - it destroys the south wall, undercuts the
   side walls and the floor slab, and leaves a 60 mm unsupported coping sliver.

6. FLAGGED, NOT FIXED (out of scope of this criticism, but the basin exposes them):
   - Pipe run from the basin (y~2100) to the basement plant zone (BS_Y0 = 15000) is
     ~13.4 m horizontal plus risers - at the research's "keep under 15 m" limit.
   - Basement floor BASE_FL = -2800 is 3.5 m below the pool water line; research wants
     the plant floor 1.0-1.5 m below WL. Harmless for suction, but it lengthens the run
     and the overflow pump should be sited at the north end of the plant room.
   - Overflow pump duty for a 5.0 m crest: 200-300 L/min thin sheet, 450-750 L/min heavy
     curtain (research 40-60 and 90-150 L/min per linear metre). Separate from filtration.
   - Section AA is cut at x = AXIS = 12000, inside the 5.0 m spill 

### Upheld 38

CONFIRMED -- I could not refute it. The geometry says exactly what the reviewer says.

Connectivity, derived the way villa_3d.py builds it (union of GF_FOOT offset inward by WALL=400):
- north bar interior x 3400..20600, y 18400..23600
- west wing interior x 3400..7600, y 12900..18400
- living volume x 9400..14600, y 12900..18400
- east wing x 16400..20600, y 12900..18400
The inward offset of the re-entrant corners excludes x 7600..9400 and x 14600..16400 for all y < 18400, and the two light-slot voids (villa_3d.py:174-177) cut x 8000..9000 and x 15000..16000 over y 12200..18300 from z=400 to z=10300. So each wing is severed from the living volume at every level and touches the rest of the house ONLY across its neck at y=18400.

Both necks are then closed by a full-width partition:
- (3400,18250,7600,18400) spans x 3400..7600 -- exactly the 4.2 m west wing interior. One door, 1200 mm, at x 5000..6200.
- (16400,18250,20600,18400) spans x 16400..20600 -- exactly the 4.2 m east wing interior. One door, 1200 mm, at x 17800..19000.

villa_sheets.py GROUND fixes the labels and they match the printed areas exactly: SHOW KITCHEN 3400,18400-8425,23600 = 26.1; FORMAL DINING 3400,12900-7600,18250 = 22.5; WOMEN'S MAJLIS 15575,18400-20600,23600 = 26.1; STUDY 16400,12900-20600,18250 = 22.5. x 5000..6200 lies inside the kitchen; x 17800..19000 lies inside the majlis. So the formal dining room's only door is into the working kitchen, and the study's only door is into the women's majlis. Neither has any opening to the entrance hall or the living volume -- the only other voids touching those rooms are the south windows at x 4200..6800 and x 17200..19800 (sill GF+450, so glazing, not doors).

Things that might have saved it, and don't:
- The living volume is open to the hall, but the 1.0 m slots block it from both wings, so that openness buys the wings nothing.
- The big "structural glazing" void (9200,9200,1000)-(14800,18300,4300) thins the living volume's flank walls to 200 mm but leaves them continuous -- it is not an opening into the slots.
- No second door exists anywhere in either neck partition.

This is not taste. Guests processing to a 22.5 m² formal dining room pass through the show kitchen, and the study is a dead-end room behind the women's majlis -- the one space in a Gulf villa whose entire purpose is that it can be closed. The study is unusable whenever the majlis is receiving, and the majlis is compromised whenever the study is used. The first floor repeats the same fault (villa_3d.py:205-220): BEDROOM 1 is reachable only through BEDROOM 3, BEDROOM 2 only through the MASTER BEDROOM.

The reviewer's proposed fix is wrong, though. The 10.4 m² gap is real (ENTRANCE HALL is scheduled only at y 20550..23600, so x 10550..15425 × y 18400..20550 = 10.48 m² is unassigned, less ~3.0 m² of stair), but you cannot "take doors off it into both wings": from x 10550..15425 the nearest wing edge is x 7600 or x 16400, with a 1.0 m full-height slot in between and the necks sitting wholly inside the kitchen and majlis footprints. No door can be drawn on that line. Fixing it inside the north bar instead costs a 1.2 m corridor off the south edge, which drops the kitchen and the majlis to 20.1 m² each -- the majlis falls out of the 25-35 m² band in VILLA_RESEARCH.md §5. The corrected fix below costs neither room a millimetre.

**Corrected fix:**

Do not cut into the kitchen or the majlis. Bridge the light slots at ground level only -- the F.LOT "bridge encased in sliding glass" move -- so the dining and the study hang off the living volume instead of off a service room and a reception room.

1. GLAZED LINKS ACROSS BOTH SLOTS (ground floor only)
Each link: 1.0 m clear wide (the slot width, x 8000-9000 west and x 15000-16000 east) x 1.5 m long, y 16800-18300, i.e. the north end of the slot, landing at the living volume's NW and NE corners where it opens to the hall gallery. Floor at FFL +900 on the basement roof; frameless glass roof at +4600 (100 mm above the first-floor slab soffit) so the slot still reads full height in elevation and section; full-height frameless glazing on the link's south face looking down the remaining 4.6 m of open slot -- which also gives these two dead notches something to light for the first time.

In villa_3d.py replace lines 174-177 with:

    LINK_Y0, LINK_Y1 = 16800.0, 18300.0
    LINK_TOP = GF + GF_CH + 100                 # glass roof at 4600
    for sx0, sx1 in ((WW_X1, LV_X0), (LV_X1, EW_X0)):
        V.append(blk(sx0, WG_Y0 - 300, GF - SLAB, sx1, LINK_Y0,
                     RF + SLAB + PARAPET))      # slot, open full height
        V.append(blk(sx0, LINK_Y0, LINK_TOP, sx1, WG_Y1 + 300,
                     RF + SLAB + PARAPET))      # slot resumes above the link
        S.append(blk(sx0, LINK_Y0, GF - SLAB, sx1, LINK_Y1, GF))        # floor
        S.append(blk(sx0, LINK_Y0, GF + GF_CH, sx1, LINK_Y1, LINK_TOP)) # glass

2. FOUR NEW DOORS, 1200 wide x 2700 high (DH), added to DOORS_GF:

    (7600,  17000,  8000, 18200),   # formal dining -> west link
    (9000,  17000,  9400, 18200),   # west link     -> family living
    (14600, 17000, 15000, 18200),   # family living -> east link
    (16000, 17000, 16400, 18200),   # east link     -> study

3. DEMOTE THE TWO EXISTING WING DOORS
- Replace (5000,18250,6200,18400) with (3900,18250,4800,18400): a 900 mm serving door at the kitchen's working end, so food enters the dining room's NW corner while guests enter at the NE. Kitchen-to-dining survives as a serving door only, which is what it should always have been.
- Delete (17800,18250,19000,18400) entirely. The women's majlis then has one controlled door from the hall (x 15425-15575, y 20500-21700) and no through-route; the study is entered only from the east link.

RESULT
- Guest route to dinner: entrance (x 11250-12750, y 24000) -> hall -> gallery gap y 18400-20550 -> living volume NW corner -> west link -> formal dining. About 14 m, never entering the kitchen. Hall -> living -> dining is the conventional enfilade a formal dining room is supposed to have.
- Study: hall -> living volume NE corner (south of the stair, which starts at y 18700) -> east link -> study. The majlis is never crossed.
- Door count: formal dining 2 (1200 primary + 900 serving), study 1 (1200), majlis 1 internal + service door.
- Areas: kitchen 26.1, majlis 26.1, dining 22.5, study 22.5, living 28.6, hall 20.9 -- all unchanged. The links add 2 x 1.5 = 3.0 m2, so ground 196 -> 199 m2, GFA 407 -> 410 m2 (4,413 sq ft), coverage 28% -> 28.6%. The slot is open y 12200-16800 (4.6 m) at ground and the full 6.1 m above +4600.

FIRST FLOOR (same fault, different cure -- the slot's east side up there is the double-height void, so it cannot be bridged): run the landing 1.2 m south-edge corridor at y 18400-19600 from x 3400 to x 20600 through the bedroom-3 and master zones, doors into both necks at the existing partition line y 18250-18400. Bedroom 3 becomes x 3400-8425, y 19600-23600 = 20.1 m2 (still inside the 18-22 m2 bedroom band); the master suite must be re-cut to sit north of y 19600 -- it needs re-planning regardless, since MASTER BEDROOM is currently 9.1 m2 against a 28-35 m2 luxury target.

Out of scope but adjacent: the service entrance void (20700,18700,21300,19800) opens off the east boundary straight into the women's majlis. Once the majlis is a proper cul-de-sac it should arrive via a short service corridor behind the kitchen, per VILLA_RESEARCH.md §5, not off the boundary wall.

### Upheld 39

CONFIRMED -- I could not refute it. Every number checks out against the model, not just the schedule.

GEOMETRY (villa_3d.py:205-220, PARTS_FF). The north bar internal is 3400..20600 x 18400..23600 (17.2 x 5.2 m). The partition at x 15425..15575 gives an east block of 5.025 x 5.2 = 26.13 m2 gross. Inside it the partition (17600,18400,17750,21600) and (15575,21600,20600,21750) subdivide it into exactly the three rooms the schedule names:
  master bedroom  17750..20600 x 18400..21600 = 2.85 x 3.20 = 9.12 m2
  dressing        15575..17600 x 18400..21600 = 2.025 x 3.20 = 6.48 m2
  master en-suite 15575..20600 x 21750..23600 = 5.025 x 1.85 = 9.30 m2
  suite net 24.90, gross 26.13. VILLA_RESEARCH.md:317 requires 55-75 (bed 28-35, dressing 14-20, en-suite 14-20), and the research's OWN workable schedule at line 335 sets "First ~180: master suite 65 (bed 30 / dressing 16 / en-suite 19)". The model's first floor is 181 m2 and delivers 26.1. The master suite is 40% of the target the design was written to, and the master bedroom is 33% of its minimum. This is arithmetic against the project's own stated standard, not taste.

DAYLIGHT. I enumerated every void in villa_3d.py that intersects the master box (x 15575..20600, y 18400..23600, z 5000..8700). Only four internal door voids and one exterior cut touch it: the east clerestory blk(20400, 18800, 7800, 21100, 23200, 8450). FF is 5000, so the sill is 2800 mm above the bedroom floor and the slot is 650 mm high in a 3700 mm clear room. The wing south windows (x 17200..19800, y 12200..12800) are in the east WING's south wall and serve BEDROOM 2, not the master. The 1.0 m light slot (x 15000..16000) stops at y 18300, 100 mm short of the bar's internal face at 18400, so it delivers nothing to any first-floor bar room. Confirmed: the master bedroom and en-suite have no window, no view and no openable light below 2.8 m. BEDROOM 3 is identical (west clerestory only). The LANDING (35.62 m2) has no exterior opening and no gallery void into the double-height volume either -- the only void in the bar's south wall at first floor is at y 12200..12900, which is the cantilever box, not the landing. Its only light is borrowed down the stairwell.

CROSS-CHECK. The A-202 render agrees: MASTER BEDROOM 9.1, DRESSING 6.5, MASTER ENSUITE 9.3, LANDING 35.6, BEDROOM 3 26.1, BEDROOMS 1 and 2 22.5 each. The plan cut is at FF+1200 = z 6200, below the 7800 clerestory, which is why no opening appears on the master's east or north walls. The master bedroom is the smallest habitable room on the floor; the landing is 3.9x its size and each of the three secondary bedrooms is 2.5x.

TWO THINGS THE CRITICISM UNDERSTATES. (1) Circulation: DOORS_FF puts the landing door at (15425,20200,15575,21400), which opens into the DRESSING, and the en-suite door at (16200,21600,17400,21750), also off the dressing. So the 9.1 m2 master bedroom is a windowless dead-end cell entered through the wardrobe, with its own bathroom not reachable from it. (2) The door (17800,18250,19000,18400) makes BEDROOM 2 accessible only through the master bedroom, and (5000,18250,6200,18400) makes BEDROOM 1 accessible only through BEDROOM 3. Two of four bedrooms are entered through another bedroom.

ONE ERROR IN THE CRITICISM, immaterial: "The master bedroom is smaller than the guest WC" is garbled -- 9.12 vs 3.6 m2. The clause appears to be a corrupted merge; every dimensional figure it cites is exact.

Severity "fatal" is fair. A US$5M villa whose principal bedroom is 9.1 m2, windowless, and reached through the wardrobe fails at the first page of the drawing set.

**Corrected fix:**

The reviewer's direction is right but its two specifics are not buildable. The east limb is only 4.2 m wide internally, so it cannot hold a 28-35 m2 bedroom without being 7-8 m long; and a first-floor terrace on the east wall would project into the 3.0 m side setback, which must stay clear -- that face is also the worst in the plan (3.0 m to a neighbour, over a 2.4 m boundary wall). Put the BEDROOM in the bar (5.85 m wide) and the DRESSING and BATH in the limb (4.2 m wide), and open the master to the NORTH, over the 5.0 m front setback and the entrance rill.

All dimensions mm, on the existing 100 mm setting-out grid.

1. EXTEND THE EAST WING 3.0 m SOUTH, ground and first: footprint (16000, 9500) to (21000, 18000), aligning its south face with the existing cantilever line at y = 9500 so the south elevation becomes three fingers around the pool court. Extend the east light-slot void (currently y 12200..18300) south to y 9200 so the limb still reads as a separate finger. Clearance to the pool edge (x 14500) stays 1.5 m, the research minimum for a walking side. New limb internal: 16400..20600 x 9900..18250 = 4.2 x 8.35 = 35.07 m2.

2. REBUILD THE SUITE (delete PARTS_FF entries 2, 3, 4 and 6 -- the x 15425 partition, the dressing partition, the en-suite partition and the master|bedroom-2 partition):
   - New landing/suite partition at x 14600..14750, flush on the east string of the stair.
   - MASTER BEDROOM = bar east block, 14750..20600 x 18400..23600 = 5.85 x 5.20 = 30.42 m2 (target 28-35; research 30). Bed wall 5.85 m against the north wall: a 1.8 m king with 1.5 m either side and a 2.0 m foot zone, plus a 1.2 m circulation band. Door from the landing at x 14600..14750, y 19500..20700.
   - DRESSING = limb north, 16400..20600 x 14650..18250 = 4.2 x 3.60 = 15.12 m2 (target 14-20; research 16). Entered off the bedroom through the full 4.2 m junction at y 18250..18400. 600 hanging both sides + 3.0 m island aisle.
   - EN-SUITE = limb south, 16400..20600 x 9900..14500 = 4.2 x 4.60 = 19.32 m2 (target 14-20; research 19). Partition at y 14500..14650. 4.2 m clear takes a 1.7 m freestanding bath across the south window with 2.5 m clear in front; the 4.6 m length holds a 1.5 x 1.2 wet room, a 0.9 x 1.5 WC compartment and a 1.8 m twin vanity -- none of which the present 1.85 m depth can take.
   - SUITE TOTAL 30.42 + 15.12 + 19.32 = 64.86 m2, against the 55-75 band and the research's own 65.

3. GIVE IT DAYLIGHT (this is the half of the defect that costs nothing):
   - Master bedroom north window wall: x 15400..20000 (4.6 m) x z 5900..7900 (sill 900, head 2900), in the north wall at y 23600..24000, facing the 5.0 m front setback down the rill axis. Screen it with the fin module already in the model (180 deep x 450 wide, 600 c/c, S.append(blk(...)) as at villa_3d.py:261-263) running x 15400..20000 from FF to RF, which kills the sightline from the gate while keeping the view down the axis.
   - Move the existing FF south window of the east wing from y 12200..12800 to y 9200..9800 (opening x 17200..19800, z 5450..7700) so it serves the new en-suite.
   - Keep the east clerestory as it is -- it now lights the dressing, which is the one room that wants only high light.
   - BEDROOM 3: add a west window x 3000..3400, y 19400..22600, z 5900..7900, and extend the west brise-soleil array north over the bar -- 8 more fins at y 18800..23000, 600 c/c. This also fixes the west elevation, where the fins presently stop dead at the wing.
   - LANDING: cut a gallery void in the bar's south wall, x 10500..14500, y 18000..18400, from z 6100 to RF -- a 4.0 m opening over the double-height living volume with a 1.1 m solid balustrade. That is the move the double-height volume exists for, and it borrows the south glazing's light into the landing.

4. KNOCK-ON -- the displaced BEDROOM 2. Enlarge the roof pavilion from PV = (9000, 19000, 15000, 24000) to (9000, 18400, 15000, 24000), i.e. 6.0 x 5.6 = 33.6 m2 gross, internal 5.5 x 5.1 (250 walls): bedroom 5.5 x 3.60 = 19.8 m2 plus en-suite 5.5 x 1.35 = 7.4 m2, partition at y 22450..22600, opening onto the roof terrace. It becomes the best guest room in the house and it lands squarely over the landing, so the walls line through. This requires the stair to continue to the roof -- which the scheme needs regardless: the pavilion and the whole semi-basement are currently unreachable, and the modelled flight (16 risers x 244 from GF 900) both exceeds a ~190 mm private-stair riser and lands 196 mm below FF 5000 against a 4100 floor-to-floor. Rebuild both flights as dog-legs in the landing: GF to FF, 22 risers at 186.4 x 260 going; FF to roof deck 9200, 23 risers at 182.6 x 260 going, 12 + 11 about a 1.2 m half-landing. The new landing (8575..14600 x 18400..23600 = 31.3 m2 gross, 26.2 net of the well) holds both, against the research allowance of 25 for landing plus circulation.

5. ALSO FIX WHILE THE PARTITIONS ARE OPEN: delete the door (5000,18250,6200,18400) and run a 1.2 m corridor at x 3400..4600 from the landing south into the west limb, so BEDROOM 1 is no longer entered through BEDROOM 3. BEDROOM 2 is no longer entered through the master because it has moved to the roof.

COST OF THE FIX, measured not guessed: ground 196 -> 211 m2, first 181 -> 196 m2, roof 30 -> 33.6 m2, GFA 407 -> 440.6 m2 = 4,743 sq ft; site coverage 211/696 = 30.3% against a buildable envelope of 18 x 21 = 378 m2, so the setbacks are untouched. The ground-floor gain is the study growing from 22.5 to 35.1 m2 -- better used as study 22.5 (16400..20600 x 12900..18250) plus a 12.6 m2 stair/lift core (16400..20600 x 9900..12900) that finally connects basement, ground, first and roof.

### Upheld 40

CONFIRMED -- I could not refute it, and the geometry is worse than the reviewer states.

WHAT I VERIFIED (villa_3d.py:205-220, cross-checked against villa_sheets.py FIRST[] and A-202_FIRST_FLOOR_PLAN.png)

I mapped every one of the six DOORS_FF openings to the rooms 300 mm either side of the leaf:
  (8425,21500)-(8575,22700)   BEDROOM 3  <-> LANDING
  (15425,20200)-(15575,21400) LANDING    <-> DRESSING      <-- not the master
  (17600,19600)-(17750,20500) DRESSING   <-> MASTER
  (16200,21600)-(17400,21750) DRESSING   <-> ENSUITE       <-- not the master
  (5000,18250)-(6200,18400)   BEDROOM 1  <-> BEDROOM 3
  (17800,18250)-(19000,18400) BEDROOM 2  <-> MASTER

So the reviewer's two headline facts are exactly right: Bedroom 1's only door is into Bedroom 3, Bedroom 2's only door is into the master. Neither touches the landing. The partitions are full-width -- PARTS_FF (3400,18250,7600,18400) spans the entire 4.2 m internal width of the west wing, and (16400,18250,20600,18400) the entire east wing -- and the 1.0 m light slots (x 8000-9000 and 15000-16000, cut y 12200-18300 from GF-SLAB to RF+SLAB+PARAPET) sever the wings from the central volume at every level, so those two doors are the only possible connections. There is no second route.

It is in fact one room deeper than claimed: the landing door opens into the DRESSING, so Bedroom 2 is landing -> dressing -> master -> Bedroom 2, three rooms deep, and the master itself is an inner room. The ensuite is off the dressing too, so the master has no direct ensuite access.

The "not habitable" framing is slightly overstated as a general code claim (the IRC does permit intercommunicating rooms provided each sleeping room has an emergency escape opening), but the escape defence fails here on the model's own numbers: the wing windows are cut at FF+450, i.e. sills 5.45 m above the garden, past the 4.5 m limit for a rescue window; and the two north-bar bedrooms (Bedroom 3, master) have no openable window at all -- their only opening is the clerestory band at z 7800-8450 (villa_3d.py:245-247), a 650 mm slot 2.8 m above their own floor. Four bedrooms, no compliant escape opening on the floor, one stair.

The stair claim also stands, and the cited lines contain two further defects: 16 risers x 244 = 3904 from GF+900 tops out at +4804, 196 mm SHORT of the FF slab at +5000 (4100 rise needs 17 risers at 241.2); and the 170 mm going against a 244 mm rise is a 55.1-degree pitch over a 2.72 m run -- a ladder, not a stair. There is no partition anywhere in PARTS_GF between the hall and the living volume, so the flight genuinely stands in a volume open through both storeys.

CORROBORATION -- the same flaw repeats on the ground floor and once more in the massing

Ground floor, DOORS_GF (villa_3d.py:196-201): the FORMAL DINING has one door, (5000,18250)-(6200,18400), from the SHOW KITCHEN; the STUDY has one door, (17800,18250)-(19000,18400), from the WOMEN'S MAJLIS. Guests reach the dining room only by walking through the kitchen, and any family member reaching the study crosses the women's majlis while it is occupied by female guests -- which defeats the one gender-separation move the brief actually asks for. It is the same structural error: the wings hang off the far ends of the north bar and nothing serves them.

Separately, while tracing FF circulation I found the first-floor cantilever is unreachable. FF_FOOT's fourth rectangle is (LV_X0, WG_Y0-CANT, LV_X1, WG_Y0+WALL) = (9000, 9500, 15000, 12900) -- a 3.4 m strip that touches neither wing (slots at 8000-9000 and 15000-16000) and stops 5.1 m short of the north bar. It gets slab, ring walls and roof, and the "structural glazing" at villa_3d.py:240-241 opens it onto the double-height void. It is a 15.6 m2 walled, roofed loggia over the pool with no floor connecting it to anything -- and its 18 m2 is counted in the printed 181 m2 first floor and the 407 m2 GFA. Visible as the detached rectangle over the pool in A-202_FIRST_FLOOR_PLAN.png.

WHERE THE REVIEWER'S PROPOSED FIX IS WRONG

"The 35.6 m2 landing has the area to become a corridor spine... costs ~9 m2." The landing cannot donate the area. It spans x 8575-15425; the wings are at x 3400-7600 and 16400-20600. The landing is not adjacent to either wing -- the two 26.1 m2 end rooms are in the way. The corridor has to be cut out of Bedroom 3 and the master zone, and at 1.40 m clear across each 5.025 m bay it costs 2 x 7.04 = 14.1 m2, not 9. Shrinking the landing buys nothing.

**Corrected fix:**

CORRECTED FIX -- a 1.40 m gallery spine cut from the two END rooms (not the landing), plus the stair moves that make it continuous.

1. ACCESS FIX (this is the whole of the finding; four lines, code-ready)

villa_3d.py PARTS_FF += 
    (3400, 19800,  8425, 19950)    # west gallery | bedroom 3
    (15575, 19800, 20600, 19950)   # east gallery | master suite
villa_3d.py DOORS_FF +=
    (8425, 18600,  8575, 19700)    # landing -> west gallery, 1.10 m leaf
    (15425, 18600, 15575, 19700)   # landing -> east gallery, 1.10 m leaf

This creates a 1.40 m clear gallery at y 18400-19800 running x 3400-8425 (7.04 m2) and x 15575-20600 (7.04 m2). The two existing wing doors -- (5000,18250,6200,18400) and (17800,18250,19000,18400) -- need no change; they now open off circulation instead of off a bedroom. Bedroom 3 keeps its own landing door at (8425,21500,8575,22700). Result: four bedrooms, four independent doors, nobody passes through a sleeping room.

Areas after the cut: Bedroom 3 3400-8425 x 19950-23600 = 5.025 x 3.65 = 18.3 m2; east end zone likewise 18.3 m2. First-floor habitable drops ~14.1 m2 (131.6 -> 117.5 net); GFA unchanged at 407 m2.

2. REQUIRED KNOCK-ON: re-zone the east end. 18.3 m2 cannot hold master + dressing + ensuite, and it could not before either -- the master as drawn is 2.85 x 3.20 = 9.1 m2, which is not a master bedroom in any villa, let alone a US$5M one. Swap the suite outward:
    MASTER  -> the east wing, 16400-20600 x 12900-18250 = 22.5 m2, entered directly off the east gallery through the existing door, taking the pool aspect and the existing south glazing at x 17200-19800.
    add PARTS_FF (18000, 19950, 18150, 23600)
    DRESSING 15575-18000 x 19950-23600 = 2.425 x 3.65 = 8.85 m2
    ENSUITE  18150-20600 x 19950-23600 = 2.450 x 3.65 = 8.94 m2
    both off the east gallery, which then dead-ends as the suite's private lobby (door at 15425-15575 closes it). Suite total 40.3 m2 against 24.9 m2 today.
    The fourth bedroom then comes out of the landing: 8575-11800 x 19950-23600 = 3.225 x 3.65 = 11.8 m2, leaving 22.8 m2 of circulation (spine 9.6 + landing 13.2). That is a real double at UK space-standard minimum (11.5 m2) and it is where the remaining area deficit will bite -- that part belongs to finding 1, not to this one.

3. REQUIRED KNOCK-ON: the stair blocks the spine. As drawn the flight occupies x 13000-14600 from y 18700, leaving only 300 mm between it and the landing's south edge, and only 825 mm between it and the east partition at 15425 -- below the 900 mm minimum. Shift it 300 mm west:
    for i in range(17):
        S.append(blk(12700, 18700 + i*280, GF + i*241.2,
                     14300, 18980 + i*280, GF + (i+1)*241.2))
    V.append(blk(12700, 18700, GF + GF_CH, 14300, 23460, FF))   # stair void
This does three things at once: 1125 mm clear pass east of the stair from the landing to the east gallery door; 17 risers at 241.2 mm land exactly on FF +5000 instead of stopping 196 mm short; and 280 mm goings drop the pitch from 55.1 to 40.7 degrees, inside the 42-degree domestic limit. The 16 x 280 = 4.48 m run fits the 5.2 m bay (18700 -> 23460 against the internal face at 23600). If the straight flight is unwanted, a 9+8 dog-leg with a 1000 mm half-landing is 2240 + 1000 + 1960 = 5200 mm -- the bay depth exactly -- at 2 x 1100 + 100 = 2300 mm wide.

4. ESCAPE (the second half of the criticism, and not solved by the spine). With one stair standing open to a two-storey volume, four bedrooms 5.0 m up, and a basement below, either enclose the stair or add a second escape. Enclosing costs nothing architecturally -- the compression-release is between the 2.40 m entry soffit and the living volume, not the stair: add PARTS_GF/PARTS_FF (12550,18400,12700,22050) and (14300,18400,14450,22050) plus a head wall (12700,22050,14450,22200) with a 1.0 m FD30 door at each level. That still leaves 975 mm clear east of the enclosure to the gallery door. Do not rely on the bedroom windows as the alternative: their sills are at FF+450 = 5.45 m above the garden, and the two north-bar bedrooms have only the 650 mm clerestory at z 7800-8450.

5. SAME PATCH, GROUND FLOOR. The dining-through-the-kitchen and study-through-the-majlis routes are the identical defect and need the identical spine -- with one difference: the guest WC (8575-10400 x 18400-20400, partitions at villa_3d.py:189-190) currently sits across the west end of the spine band, so on the ground floor it has to move north into the hall's north strip (y 21750-23600) before the hall -> west corridor door at (8425,18600,8575,19700) can be cut. The east side needs no such move: (15425,18600,15575,19700) into a gallery at 15575-20600 x 18400-19800 gives the study its own door and stops the family crossing the women's majlis.

6. WHILE THE MODEL IS OPEN: the first-floor cantilever, FF_FOOT (9000, 9500, 15000, 12900), is an enclosed 15.6 m2 room over the pool with no access from anywhere and 18 m2 of it counted in the GFA. Either bridge to it across a slot (e.g. slab at 9000-9400 or 14600-15000, y 11000-12500, with a door) so it becomes the master's or Bedroom 1's terrace, or delete the strip and take the 18 m2 out of the printed first-floor and GFA figures.

### Upheld 41

REAL -- confirmed by measuring the built solid, not by reading. I rebuilt the model (`villa_3d.build()`) and intersected it with 100 mm probe slabs through the ground-slab band (z 600-700) to get the floor actually present inside each schedule rectangle:

  FAMILY LIVING (9400,12900-14600,18400)  nominal 28.60 -> present 13.60 m2  (missing 15.00)
  GUEST WC      (8575,18400-10400,20400)  nominal  3.65 -> present  2.75 m2  (missing  0.90)
  ENTRANCE HALL (8575,20550-15425,23600)  nominal 20.89 -> present 20.89 m2  (missing  0.00)
  hall/stair S strip (8575,18400-15425,20550) nominal 14.73 -> present 9.73 (missing 5.00)
  floor at foot of stair (13000,18400-14600,18700) nominal 0.48 -> present 0.03 (missing 0.45)
  central spine total                                                        missing 20.00 m2

So the headline arithmetic is exact: the court void (villa_3d.py:132, z −2800 → +1100, subtracted at line 287 after the ground slab at z 400-900 is built) removes 10.0 m3 of slab = 20.00 m2 of ground floor. Two of the reviewer's sub-figures are wrong, both in the design's disfavour: the family living room loses 15.00 m2 not 13.0 (leaving 13.60 m2 of the 28.6 labelled on A-201, not 15.6), and the labelled ENTRANCE HALL loses nothing -- the other 5.00 m2 comes out of the unlabelled hall/stair circulation strip south of the WC. The 900 x 1000 hole in the guest WC is exact (0.90 m2 measured).

Roofing: probing vertical columns above the court, every point returns a solid band at z 8700-9200 (the roof slab, x 3000-21000 x y 9500-24000) -- court centre, south end and north end are all ROOFED; the north end additionally has the first-floor slab at 4500-5000 and the pavilion at 10300-12200. The light slots that cut the roof are at x 8000-9000 and 15000-16000; the court at x 9500-14500 sits between them. So the "sunken courtyard lit by sky" of research §1 and §THE SECTION WORTH STEALING is the bottom of an 11.5 m enclosed shaft. "Zero daylight" is rhetorical -- it borrows light from the 3.4 m south glass wall 2.6 m away and through the double-height void -- but it sees no sky and no sun, so the white-pebble bounce cannot work and the basement gets a dim shaft, not a court.

The reviewer also missed the worst consequence. Probing floor presence line by line: at y 15500 / 16500 / 17500 / 18200 the only slab left across the living volume is x 9000-9500 and 14500-15000, and 400 mm of each is the external wall -- the walkable ledge is 100 mm on each side. The court is 5000 wide inside a 5200 wide room. The family living room, the principal ground-floor space and the double-height volume, has no floor connection to the entrance hall at all; and the stair's bottom tread is clipped (its lower 200 mm removed over x 13000-14500) with 0.03 of 0.48 m2 of landing floor beneath it. Unguarded 3.7 m drops occur at the court's south edge in the living room, at its north edge in the hall (probe returns 0.000 m3 of solid z 900-2000), at the foot of the stair, and inside the guest WC.

And none of it is drawn: derive() cuts plans at GF+1200 = 2100, the void tops out at 1100, and the code deliberately omits the "beyond" projection (villa_3d.py:349-350). The rendered A-201 shows FAMILY LIVING as an intact 28.6 m2 room. That is confirmed on the PNG.

Not real, or weak: the sump. Nothing in the model carries drainage anywhere -- no gullies, falls or downpipes -- so its absence is not a modelled defect on its own. The "12 m downhill of the pool" is loose too: the pool's near edge is 2.9 m from the court, not 12, with the basement's south wall between them. Those points do not carry the finding; the 20.00 m2 of missing occupied floor, the severed living room and the unguarded drops do. Fatal is the right severity.

**Corrected fix:**

The court cannot be fixed in place. Two facts settle it:

(1) The ground-floor footprint covers the entire basement footprint (BS x 3000-21000, y 15000-24000) except the two 1.0 m light slots -- so there is no open ground anywhere on the plot from which an external court can reach the basement.
(2) An internal court cannot meet the research minimum. The living volume's clear width is 5200 mm; with the 1.2 m circulation each side needed to keep the room connected to the hall, the court could be 2.4 m wide (x 10800-13200) x 3.0 m = 7.2 m2 -- below the 4 x 4 m minimum, and with H = 11.5 m to the roof, H/W = 4.8. That is a shaft, exactly what research §2 warns against.

So relocate it. Fix in five parts:

1. MANDATORY -- stop the void cutting the ground floor. Delete/retarget villa_3d.py:132 (`V.append(blk(CT_X0, CT_Y0, BASE_FL, CT_X1, CT_Y1, GF + 200))`). This alone restores 20.00 m2 of slab: family living 13.60 -> 28.60, guest WC 2.75 -> 3.65, hall/stair strip 9.73 -> 14.73, stair landing 0.03 -> 0.48, and reconnects the living room to the house.

2. NEW COURT IN THE FRONT SETBACK, against the basement's north wall -- the only open ground that touches the basement.
   CT_X0, CT_X1 = 13600.0, 18600.0     # 5.0 m
   CT_Y0, CT_Y1 = 24000.0, 27600.0     # 3.6 m  ->  18.0 m2
   Invert −2800 (basement FFL), garden 0 -> 2.8 m excavation, inside the research's 2.7-3.3 m. Aspect 3.6:2.8 = 1.29:1, inside the 1:1-2:1 comfort band, and open to sky in every direction above grade.
   South face flush with the basement's north wall (y 23600-24000): glaze it full height, opening 4600 x 2200 (x 13800-18400, z −2600 to −400) into the staff/laundry zone. Floor in white pebble or honed light limestone per research §6.
   Clearances checked against the model: guest entrance void x 11250-12750 (850 mm clear), rill kerb x 11500-12500, car porch x 3500-10500, plot east setback at 21000. Boundary wall inner face y 28650 leaves 1050 mm of ground north of the court -- design the court's north retaining wall to carry the boundary wall's surcharge (the same 45-degree load-spread rule research §3 applies to the pool).
   Move the pedestrian gate (villa_3d.py:285, currently x 15400-16600) to x 19800-21000 so guests do not walk into the court; it then feeds the east side of the forecourt.

3. GUARDING -- 1100 mm to the three exposed sides (research §6, roof terrace minimum). Either a 350 mm stone parapet matching the boundary wall: S.append(blk(CT_X0−350, CT_Y0, 0, CT_X1+350, CT_Y1+350, 1100)) with the court void cut through it, or a frameless glass balustrade 1100 mm set in a channel 150 mm back from the edge. Model it -- an unmodelled guard is how the first one was missed.

4. PUMPED SUMP -- court floor falls 1:80 to a 600 x 600 x 600 deep sump at the north-east corner; 100 mm linear channel drain at the foot of the glazing; twin submersible pumps duty/standby at 6 L/s each on separate circuits, non-return valves, high-level alarm to the panel, discharge above the 1-in-100 flood line. Sizing check: 75 mm/h over 18.0 m2 = 0.38 L/s, so 6 L/s duty carries a >10x factor for blockage. Verify the design rain intensity locally -- 75 mm/h is an assumption, not a code citation.

5. DRAWING -- the new court tops out at z = 0 and the plans are cut at z = 2100, so it will be invisible for the same reason the old one was. Add it explicitly in villa_sheets.sheet(), the way the pool and porch already are:
   p.box(v3.CT_X0, v3.CT_Y0, v3.CT_X1, v3.CT_Y1, "A-FLOR-OTLN")
   p.text("SUNKEN COURT  FFL −2.80", mid, mid, 200, "A-ANNO-TEXT", align="MIDDLE_CENTER")
   General rule while derive() omits the beyond projection: anything below the cut plane must be drawn by hand or it does not exist on the sheet.

One number to correct while you are in there: build() prints `basement 142 m2` from `area(BS) − area(CT)`, i.e. gross minus court. With the court outside the basement box that subtraction is now wrong, and it was already gross not net -- the true net internal is (18000−800) x (9000−800) = 141.0 m2.

### Upheld 42

CONFIRMED by solid-model probing, not code reading. I built the model with build123d and ran boolean-intersection probes.

MECHANISM: villa_3d.py line 132 cuts the court void from BASE_FL up to GF+200=1100. The ground slab occupies z 400-900 (line 155, extrude(fp_gf, SLAB) at GF-SLAB). Line 287 subtracts all voids last (`model = (Part() + S) - V`). The court rectangle x 9500-14500, y 15400-19400 lies ENTIRELY inside fp_gf: 13.0 m2 under the living volume (LV 9000-15000, 12500-18000) and 7.0 m2 under the north bar (3000-21000, 18000-24000).

MEASURED: nominal ground slab 196.00 m2; slab actually present 175.40 m2; removed by voids 20.60 m2 (court 20.00, west light slot 0.30, east light slot 0.30). Probes at z 400-900: court centre in living volume 0.0% solid; court under north bar 0.0%; court strip in guest WC 0.0%; whole court footprint 0.0%. Controls: living room south of court 100.0%, entrance hall 100.0%.

THE REVIEWER UNDERSTATES IT. A floor-support scan across the living room at y=16500 returns floor only at x 9400-9500 and 14500-14600 - 100 mm ledges. The living volume's clear interior is x 9400-14600 and the court is 9500-14500, so the 13.0 m2 of living room south of the court is an ISLAND, reachable only across a 100 mm ledge beside a 3.70 m drop. At the threshold y=19000 the slab is absent continuously x 9500-14500. The slab under the first stair treads (x 13000-14500, y 18700-19400) is also gone, as is the slab under the guest-WC east partition (x 10400-10550, y 18400-19400).

INVISIBILITY CONFIRMED: derive() cuts the GF plan at GF+1200=2100, which is 1000 mm above the court rim at 1100, and 'beyond' projection is disabled (comment line 349). I opened A-201_GROUND_FLOOR_PLAN.png: it labels "FAMILY LIVING 28.6 m2" over an unbroken rectangle with no void shown. villa_sheets.py line 33 bills the full schedule rectangle 9400,12900-14600,18400.

AREA ARITHMETIC: family living scheduled 28.6 m2, overlapped 15.0 m2 (52%), real 13.6 m2. Guest WC loses 0.9 m2. Ground floor billed 196 m2 but really 175.4 m2 - villa_3d.py line 297 subtracts the court from the BASEMENT only, never from the ground floor.

TWO CORRECTIONS TO THE REVIEWER: (1) their remedy "cut the GF plan at 1100+" is wrong - derive() already cuts at 1200 above FFL, which is correct practice; cutting below 1100 would put the plane 200 mm above the floor and render every window as solid wall. Only their dashed below-cut projection is valid. (2) their proposed relocation to y 19000-23000 is under the entrance hall (8575-15425, 20550-23600) - the identical defect moved onto the guest arrival axis.

This is not taste. It is a 20 m2 unguarded 3.7 m drop through the middle of the piano nobile that severs circulation, undermines the stair base, and is invisible on every issued drawing.

**Corrected fix:**

ROOT CONSTRAINT the reviewer missed: the ground-floor footprint covers the ENTIRE basement box (BS 3000-21000 x 15000-24000) except the two 1.0 m light slots. There is no sky over the basement anywhere inside the footprint, so the court cannot be moved "elsewhere in plan" - it must leave the footprint. The basement's east and west walls sit on the side-setback lines (BS_X0=3000, BS_X1=21000) and those strips are empty. Put the court there, split in two, which cross-lights and cross-ventilates an 18 m wide basement as a single central court never could.

TWIN SUNKEN COURTS, SIDE SETBACKS, WHOLLY OUTSIDE THE GROUND-FLOOR FOOTPRINT

* East (service) court: x 21000 -> 23650 (2.65 m, basement wall to boundary-wall inner face), y 15000 -> 18300 (3.30 m) = 8.75 m2. Ends 400 mm clear of the existing service door at y 18700-19800, so the service walk from the forecourt still reaches it.
* West court: x 350 -> 3000 (2.65 m), y 18400 -> 22000 (3.60 m) = 9.54 m2. Clear of the brise-soleil fins, which stop at y 17780. Clear of the porch and vehicle gate (y >= 24400).
* Court paving z = -2650 (150 mm over the basement slab at -2800); depth below grade 2.65 m; width:depth 1.0:1.
* Basement flanks glazed 2.60 m high: east y 15400-17900, west y 18800-21600, z -2700 to -100.
* 1100 mm guard upstands, 300 mm thick, across the two open ends of each court at grade. The current model has no guarding of any kind.
* Pale render on the boundary-wall faces to bounce light; channel drain pumped to sewer (courts sit below invert).
* Flag for the client: an unroofed sunken lightwell in the setback is normally permitted as it is not built area, but confirm against the local municipality code.

Total 18.3 m2 of court against 20.0 m2 lost. Ground floor returns to a truthful 196 m2, family living to its full 28.6 m2, the hall-to-living threshold and the stair base are restored, and the basement grows from 142 to 162 m2. GFA 407 m2 stands.

CODE - replace villa_3d.py lines 104-105:

    CTE = (21000.0, 15000.0, 23650.0, 18300.0)   # east service court  8.75 m2
    CTW = (  350.0, 18400.0,  3000.0, 22000.0)   # west court          9.54 m2
    CT_FL = -2650.0                              # paving, 150 over basement slab

replace line 132:

    for cx0, cy0, cx1, cy1 in (CTE, CTW):
        S.append(blk(cx0, cy0 - 300, CT_FL - 300, cx1, cy1 + 300, STREET))
        S.append(blk(cx0, cy0 - 300, STREET, cx1, cy0, STREET + PARAPET))   # guard
        S.append(blk(cx0, cy1, STREET, cx1, cy1 + 300, STREET + PARAPET))   # guard
        V.append(blk(cx0, cy0, CT_FL, cx1, cy1, STREET + PARAPET + 100))
    V.append(blk(BS_X1 - WALL - 50, 15400, BASE_FL + 100,
                 BS_X1 + 50,        17900, BASE_FL + 2700))
    V.append(blk(BS_X0 - 50,        18800, BASE_FL + 100,
                 BS_X0 + WALL + 50, 21600, BASE_FL + 2700))

line 297 becomes:  base = area(BS_X0, BS_Y0, BS_X1, BS_Y1)          # 162 m2

Also close the 0.60 m2 the light slots take by overrunning 300 mm into the north-bar slab (lines 174-177): use WG_Y1 instead of WG_Y1 + 300 for the slab band, or accept them as glazed floor lights and draw them.

THREE DRAWING/QA FIXES SO THIS CLASS OF ERROR CANNOT HIDE AGAIN

1. In derive(), add a slab-plane section at z = GF - SLAB/2 = 650 (and GF + GF_CH + SLAB/2 = 4750) exported as VILLA_SLAB_GF.dxf / VILLA_SLAB_FF.dxf; import in villa_sheets.sheet() onto a dashed A-FLOR-BELO layer. KEEP the 2100 plan cut as it is - do not lower it.

2. Room schedule: give each entry an optional void list and compute
   a = gross - sum(overlap(room, void)), labelling any room where the two differ:

    def net_area(x1, y1, x2, y2, voids):
        a = (x2 - x1) * (y2 - y1)
        for vx0, vy0, vx1, vy1 in voids:
            a -= max(0, min(x2, vx1) - max(x1, vx0)) * max(0, min(y2, vy1) - max(y1, vy0))
        return a / 1e6

3. Build-time assertion - this would have caught the defect on day one:

    slab = Pos(0, 0, GF - SLAB) * extrude(fp_gf, SLAB)
    lost = (slab.volume - (model & slab).volume) / (SLAB * 1e6)
    print(f"  slab check  {lost:.2f} m2 of ground slab removed by voids")
    assert lost < 0.5, f"unguarded hole(s) in the ground floor: {lost:.2f} m2"

Run against the current file it prints 20.60 and fails; against the fix it prints 0.00.

### Upheld 43

CONFIRMED, and understated. Every number reproduces from source. villa_sheets.py:36-44 sums to 131.59 m2 net / 95.97 m2 habitable -- the 96.0 m2 the A-202 title block prints. VILLA_RESEARCH.md:317-318 gives master suite 55-75 and guest suite 28-35, so 55 + 3x28 = 139 m2 is the bottom of the project's OWN researched luxury band; the floor is 43.0 m2 (31%) below it. The research's worked 418 m2 schedule (lines 335-336) independently asks for a 180 m2 first floor carrying 155 m2 of suites. The orphaned cantilever is real: the double-height void at villa_3d.py:162, blk(9400, 12500, ..., 14600, 18000, ...), spans the full 5.2 m internal width of the living volume, so the 13.5 m2 clear slab at y 9900-12500 has no floor connection to the north bar -- yet its 18 m2 gross is counted in the 407 m2 GFA. Usable first floor gross is therefore 163 m2 (108 north bar + 27.5 + 27.5 wings), net internal 135.64 m2.

Three defects in the same partition set (villa_3d.py:205-220) that the reviewer did not reach, each independently fatal:
(1) MASTER BEDROOM is 2.85 x 3.20 m = 9.1 m2. The research band for the master BED alone is 28-35 m2. 2.85 m internal width takes a 1.8 m bed with 0.5 m each side -- below a code-minimum single bedroom.
(2) The floor has ONE WC. Only MASTER ENSUITE appears in the schedule as "wet", and PARTS_FF contains no other bathroom. Bedrooms 1, 2 and 3 have no en-suite and no shared bathroom.
(3) TWO BEDROOMS ARE INNER ROOMS. Door (5000, 18250, 6200, 18400) is the only way into Bedroom 1, and it is in Bedroom 3's south wall. Door (17800, 18250, 19000, 18400) is the only way into Bedroom 2, and it sits on the MASTER BEDROOM's south wall (master x 17750-20600) -- a guest bedroom entered through the master. The master itself is reached only through its own dressing room, via door (15425, 20200, 15575, 21400) which opens into DRESSING, not the bedroom.

WHERE THE CRITICISM IS WRONG (it does not survive as written, only as a diagnosis):
- "forces the pool to rotate east-west across the south boundary" is false. The pool is x 9500-14500 (shell 9100-14900); the wings are x 3000-8000 and 16000-21000, i.e. 1.1-1.5 m clear of it in X. The wings can be extended SOUTH without touching the water. The rill-to-pool long axis, the Myrtles reference and the 3.0 m cantilever all survive.
- "Do not attempt four en-suited bedrooms on 163 m2" is overstated. 163 m2 gross is 135.64 m2 net internal, which holds four 28-30 m2 en-suite bedrooms plus a 22 m2 landing/stair. What 163 m2 cannot hold is a 55 m2 master ALONGSIDE three 28 m2 suites -- the plate has exactly four bay-sized zones (2 wings + 2 north-bar bays) for four bedrooms, so the master can only reach 55 m2 by taking a second zone.
- "Two bedrooms must leave this plate" -- at most one does, and it need not.
- Fix (a) is not shovel-ready: no stair in the model rises above the first floor (the only stair loop, villa_3d.py:232-234, runs GF to FF), so the 30 m2 roof pavilion is a SECOND orphan already counted in GFA, not a built master. Putting the master two flights above the ground-floor family living also breaks the brief's family-on-ground / bedrooms-above logic.
Separately noted while checking: the sunken court void blk(9500, 15400, -2800, 14500, 19400, 1100) cuts the ground slab, punching a 5.0 x 3.0 m = 15 m2 hole through the FAMILY LIVING floor (9400-14600 / 12900-18400), which villa_sheets.py still schedules as a full 28.6 m2; and the stair is 16 risers x 244 = 3904 mm against a 4100 mm floor-to-floor, with a 170 mm going. Separate findings, but they mean the first floor as modelled is not merely undersized -- it is unreached and unresolved.

**Corrected fix:**

Keep the pool, the axis and the cantilever exactly where they are. Three moves inside the existing parti.

MOVE 1 -- extend both wings 2.5 m south (the only free direction, and the pool does not block it).
Introduce a wing south edge separate from the living-volume datum: WG_S = 10000, applied ONLY to the west and east wing rectangles in GF_FOOT and FF_FOOT. Leave WG_Y0 = 12500 as the south face of the double-height volume and the datum for the 3.0 m cantilever, and extend the two light-slot voids south to y 9700 to match.
Notch the extension so the pool keeps its surround: south of y 12500 the wings are 4.7 m wide, not 5.0 --
  west wing  x 3000-8000  for y 12500-18000 ; x 3000-7700  for y 10000-12500
  east wing  x 16000-21000 for y 12500-18000 ; x 16300-21000 for y 10000-12500
That leaves 1.4 m from wing face to pool shell (research minimum 1.2 m on back sides); without the notch it is 1.1 m and fails.
Result per wing: 39.25 m2 gross / 32.85 m2 net internal (was 27.5 / 23.1).
  First floor gross 204.5 m2 (was 181, of which 18 orphaned)
  Ground floor gross 219.5 m2, site coverage 31.5% (was 28%) -- far under any Gulf 50-60% limit
  GFA 454 m2 = 4,887 sq ft. This is +8.6% on the 418 m2 brief figure, which is the honest price: the research itself (line 31 and the 480-620 m2 note in villa_3d.py's docstring) already identified 418 m2 as short for this programme.

MOVE 2 -- stop orphaning the cantilever; recover 18 m2 of GFA that currently does nothing.
Narrow the double-height void from the full internal width to 4.0 m, leaving a 1.2 m gallery slab on the WEST side (clear of the stair, which occupies x 13000-14600):
  villa_3d.py:162  V.append(blk(LV_X0 + WALL + 1200, WG_Y0, GF + GF_CH, LV_X1 - WALL, WG_Y1, FF))
  -> void x 10600-14600, y 12500-18000 = 22.0 m2, still 7.30 m clear (compression ratio unchanged at 1:3.0).
The 1.2 m gallery at x 9400-10600 links the landing to the 5.2 x 2.6 m (13.5 m2) plate over the pool, which becomes the UPPER FAMILY LOUNGE -- south-glazed under the 3.0 m cantilever soffit, and the "family landing 12" the research schedule asks for. Family living below stays 28.6 m2; 22.0 m2 of it is double height and a 1.2 m soffit at 3.60 m runs along its west edge, which strengthens the compression/release rather than weakening it.

MOVE 3 -- re-plan the first floor so every bedroom opens off the landing and every bedroom has a bathroom. Delete PARTS_FF / DOORS_FF (villa_3d.py:205-220) entirely and reset to five zones across a 155.1 m2 net plate (+20.1 m2 gallery limb):
  MASTER SUITE 54.2 m2 = east wing 32.85 + north-bar east bay x 16500-20600, y 18400-23600 (4.10 x 5.20 = 21.3)
     bedroom 4.20 x 5.50 = 23.1 in the wing, south over the pool with east light; wardrobe 3.90 x 2.50 = 9.75 in the notched extension; dressing 2.00 x 5.20 = 10.4 and en-suite 2.00 x 5.20 = 10.4 in the bay. Entered from the landing at the bay's west face (door x 16350-16500, y 20400-21600).
  BEDROOM 2 SUITE 32.85 m2 = west wing. Bedroom 4.20 x 5.50 = 23.1; en-suite 2.40 x 2.50 = 6.0 and wardrobe 1.50 x 2.50 = 3.75 in the notched extension. Entered from the landing at the wing head (door x 4600-5500 on the y 18400 line) -- NOT through Bedroom 3.
  BEDROOM 3 SUITE 21.6 m2 = north bar x 3400-7550, y 18400-23600. Bedroom 4.15 x 3.60 = 14.9 (north light, y 20000-23600); en-suite 4.15 x 1.60 = 6.6 (y 18400-20000).
  BEDROOM 4 SUITE 21.6 m2 = north bar x 7700-11850, y 18400-23600, same split.
  LANDING + STAIR 22.6 m2 = north bar x 12000-16350, y 18400-23600, plus the 6.6 m2 gallery bridge to the upper lounge.
  North bar balance: 21.3 + 21.6 + 21.6 + 22.6 = 87.1 + 2.3 partitions = 89.4 m2, exact.
  Suites total 130.2 m2 against the 139 m2 research minimum -- 6% short, not 31%, with the two principal rooms (54.2 and 32.9) at or above band and the two junior rooms at 21.6 carrying full en-suites. Counting the 13.5 m2 upper lounge the floor reads as a complete luxury bedroom level.

MOVE 4 -- the stair, which must be rebuilt for any of the above to be reachable. The present flight (villa_3d.py:232-234) is 16 risers x 244 = 3904 mm against a 4100 mm floor-to-floor, so it lands 196 mm low, and its 170 mm going is not walkable. Use 17 risers x 241.2 mm = 4100 exactly, 16 goings x 280 = 4480 mm run, 1.20 m clear width, as a straight flight running east-west in the landing zone (x 12000-16480, y 18400-19600). Add a second flight from the landing to the roof so the 30 m2 pavilion -- the other orphan already counted in GFA -- becomes stair head, roof pantry/WC and store serving the shaded roof terrace, exactly as VILLA_RESEARCH.md:337-338 specifies.

IF THE CLIENT WILL NOT ACCEPT THE +8.6% GFA: the reviewer's option (a), corrected. Extend the roof pavilion from 30 to 55 m2 as the master suite with a private roof terrace, add the roof stair (which the model lacks either way), and the existing 163 m2 plate then carries three suites at 30/30/29 plus a 25 m2 landing with no wing extension at all. That is ONE bedroom leaving the plate, not two, and 55 m2 not 60 -- 60 m2 is 31% of the roof plate and is where Gulf roof-annexe area limits start to bite.

### Upheld 44

I tried to refute this and could not. The core claim -- a 7.80 m volume with no external aperture above 4.30 m -- is verifiable in the code and visible in VILLA_SECTION_AA.png.

WHAT CHECKS OUT (C:\Users\asdfv\autocad-mcp\villa_3d.py):

1. Height. FF_FOOT (line 140-142) puts the first floor over the living bay only at (LV_X0, WG_Y0-CANT, LV_X1, WG_Y0+WALL) = y 9500-12900, i.e. the cantilever alone. Over the bay itself (y 12500-18000) there is no first-floor slab; the void void at line 162 removes the 4500-5000 slab across x 9400-14600. The soffit above is the roof slab, built at RF -> RF+SLAB (line 165), so its underside is 8700. Floor at GF 900. Clear height = 7800, not 7300. build() prints (RF - SLAB - GF), which assumes a slab whose TOP is at RF; the roof slab's top is at RF+SLAB. So the printed "7.30 m clear" and "1:3.0" are wrong: the true figures are 7.80 m and 1:3.25. Real arithmetic slip in a figure the brief calls measured.

2. Proportion. Clear plan 9400-14600 x 12900-18000 = 5.2 x 5.5 m, so h/w 1.50 and h/d 1.42; 223 m3 over 28.6 m2. It fails the research's "at least as wide as it is tall in one direction". (The reviewer overstates by calling it a shaft "by the research's own test" -- the shaft test is "below ~5 x 5 m", which the bay passes at 5.2 x 5.5. And the void's north side is fully open across all 5.2 m to the single-height hall, so the perceived plan depth at ground is 12900-23600 = 10.7 m, giving the eye standoff to read the height. That mitigates the proportion charge; it does not touch the daylight charge.)

3. Apertures. This is the part that stands completely. Every opening cut in the void's four faces:
   - south, ground: x 9200-14800, z 1000-4300 (head 3.40 m above floor);
   - south, first floor: x 9200-14800, y 12200-13200, z 5300-7900 -- this is an INTERNAL opening. It cuts the wall band at y 12500-12900 and gives onto the cantilever volume, which is a fully enclosed box (FF_FOOT generates walls on all four sides from 5000 to 8700, floor 4500-5000, roof slab over) with no external opening cut anywhere, no door, no stair reaching it, and no entry in villa_sheets.py's schedule. 13.5 m2 of sealed, windowless, unreachable volume hanging over the pool. So it delivers zero daylight.
   - east/west: none. The two 1.0 m light slots run full height right past the bay and no window is cut onto them from either side, so they light nothing.
   - north: at ground it is open to the hall; at first floor there is a solid 400 mm wall (fp_ff's north-bar south edge, y 18000-18400, z 5000-8700) with no opening, so the landing does not even overlook the void.
   - roof: the slab spans y 9500-24000 unbroken; the parapet void starts at RF+SLAB so it does not cut the slab. No rooflight, no monitor. The clerestory technique IS used elsewhere (lines 245-247, north-bar flank walls at z 7800-8450), which makes the omission over the principal space harder to defend, not easier.
   Net: 56% of the height of the villa's principal volume (4.30 m to 8.70 m) is blank wall with no light source. Confirmed visually in the section crop -- the roof line runs unbroken over the bay and the cantilever box's south wall is solid from 5000 up through the parapet to 10300.

4. A bug the reviewer missed, in the same wall: the ground "structural glazing" void ends at WG_Y0+300 = 12800, but the wall band runs 12500-12900, so a 100 mm leaf of wall is left standing across the whole opening from z 1000-4300. It shows as a double line in the section.

WHERE THE REVIEWER IS WRONG: the clerestory finding is not quoted in the design-basis docstring (only the brise-soleil finding is); and their proposed fix is worse than the defect. "Widen to 9.0 m by absorbing the slots" is arithmetically off -- both 1.0 m slots give 8.0 m gross / 7.2 m clear; 9.0 m clear means taking 0.9 m off each wing, which drops Bedrooms 1 and 2 to 3.3 x 5.35 = 17.7 m2, below the research's own 18-22 m2 band, and deletes the two three-dimensional patios that docstring move #4 rests on. Their 60/40 then leaves a 2.2 m deep, 7.8 m tall double-height slot -- h/d 3.5, a far worse shaft than the one they are objecting to. And a rooflight is the wrong aperture to reach for first, because the roof already cantilevers 3.0 m over a south wall that is currently blind.

Verdict: real, and major on the daylight/section count. Fixable entirely in section, without touching the plan grid, the slots or the wings.

**Corrected fix:**

Fix it in section. Keep the 6.0 m bay, both 1.0 m light slots, CANT = 3.0 m and the wing widths. Four edits to villa_3d.py.

1. TURN THE SEALED BOX INTO A TWO-STOREY GLASS WALL UNDER THE ROOF CANTILEVER (does most of the work).
The first-floor cantilever is modelled as an enclosed room with no window, no door and no schedule entry. Strip it back to structure and glaze the void's south face instead:
  - delete the wall band x 9400-14600, y 12500-12900, z 5000-8700 -> becomes the void's high-level south glazing, 5.2 x 3.7 m = 19.2 m2, sill 5000 (4.10 m above floor), head 8700 (7.80 m above floor);
  - delete the box's blind south wall, x 9400-14600, y 9500-9900, z 5000-8700;
  - KEEP the two 400 mm flank blades x 9000-9400 and 14600-15000, y 9500-12900, z 5000-8700. Each is a 3.7 m deep wall-beam projecting 3.4 m (span/depth 0.9) and carries both the 4500-5000 canopy slab and the roof slab over the pool;
  - KEEP the 4500-5000 slab over y 9500-12900 as the open shading canopy the docstring already promises.
Shading is then free and correct for 25 degrees N: upper glass head 8700 sits under the roof soffit running out to y 9500 -> projection 3.0 m over a 3.7 m opening, P/H 0.81 (research asks 0.6-0.8). Lower glass head 4300 sits under the canopy at 4500 projecting 3.0 m, P/H 0.91. Specify SHGC <= 0.27, U <= 3.0, 18-22 mm sightlines.
Daylight, by the research's own 2.5 x head-height rule: head 7.80 m above floor -> 19.5 m penetration, reaching y = 32,400, i.e. the full 10.7 m ground-floor depth including the dark north bar. That is the reviewer's stated objective, achieved with a shaded vertical aperture instead of a rooflight.
Read: the south face becomes glass from 1.0 to 8.7 m, 5.2 m wide, broken only by a 700 mm slab band at 4300-5000, framed by two blades and capped by a 3.0 m overhang, looking down the pool.

2. NORTH-FACING ROOF MONITOR (light from above, no direct sun).
  - cut the roof slab x 9400-14600, y 12900-13900 (5.2 x 1.0 m = 5.2 m2). The remaining slab spans 13900-18000 (4.1 m one-way onto the north-bar wall) with the monitor upstand as its edge beam; the 400 mm strip at y 12500-12900 stays on the flank blades;
  - north glass at y 13900, x 9400-14600, z 9200-10300 = 5.2 x 1.1 m = 5.72 m2;
  - solid white-rendered reflector blade at y 12500-12900 from 9200 to 10500; cap slab 10300-10500 over y 12900-14200, i.e. 300 mm overhang past the glass as drip and sun-cut.
Top at 10500 is 200 mm above the parapet (10300) and 1.7 m below the roof pavilion, so it is invisible from the street. Obstruction: the pavilion (top 12200 at y 19000) subtends 25.7 degrees from mid-glass, so there is a usable north sky patch above that; no direct beam at this latitude. Expect roughly 1.5-2.5% DF added at the living floor (the reviewer's 2-4% is optimistic for a vertical aperture with a 7.8 m throw).
Together items 1 and 2 take apertures above 4.30 m from 0 to 24.9 m2.

3. CORRECT THE PRINTED FIGURES.
In build(), replace (RF - SLAB - GF) with (RF - GF) in both places: prints "7.80 m clear" and "compression ratio 1:3.25". The soffit over the void is the roof slab underside at RF, not RF - SLAB.

4. FIX THE 100 mm RESIDUAL WALL LEAF.
The ground glazing void ends at WG_Y0 + 300 = 12800 while the wall band runs to 12900, leaving a 100 mm leaf standing across the whole opening from z 1000-4300. Change WG_Y0 + 300 to WG_Y0 + WALL + 300 (13200), matching what the first-floor opening already does.

AREA EFFECT: the 3.0 m cantilever stops being enclosed floor and becomes a covered terrace/canopy, so GFA goes 407 -> 389 m2 (4,187 sq ft). That is the same BUA argument the file already makes for the car porch. Recover it with the optional item below if the client wants the number back.

OPTIONAL, if the 60/40 discipline is wanted: return a first-floor gallery over the bay's north 2.2 m only -- slab 4500-5000 at x 9400-14600, y 15800-18000 (11.4 m2), with a 1.2 x 2.4 m opening cut in the y 18000-18400 wall to link it to the landing. Ground floor then reads 15.1 m2 double-height at the glass (60%) plus an 11.4 m2 sofa zone at 3.60 m clear under the gallery (40%), and GFA returns to 400 m2. Do NOT go further and apply a literal 60% single-height: at this bay width that leaves a 2.2 m deep void and turns the space into a chimney.

DO NOT widen the bay to 9.0 m. Absorbing both slots yields 7.2 m clear, not 9.0; getting to 9.0 costs 0.9 m off each wing, taking Bedrooms 1 and 2 to 17.7 m2 (below the 18-22 m2 luxury band) and deleting the two three-dimensional patios. The residual h/w 1.50 is acceptable once the volume is glazed top and south and stays open across its full 5.2 m width to the 10.7 m deep single-height hall behind -- the eye has the standoff to read the height, which is what the "as wide as tall" rule is actually protecting.

Separately worth doing while in this area (not required to close this finding): cut a 1.2 m wide full-height glazed strip in each flank wall onto the light slots, x 9000-9400 and 14600-15000, y 14800-16000, z 1000-8300, and match it on the facing wing walls. The slots currently have no window on either side and light nothing.

### Upheld 45

REAL -- and verified by boolean intersection against the built solid, not by reading code. I could not refute it; the geometry is worse than the reviewer describes.

VERIFICATION (probe boxes intersected with the model returned by villa_3d.build(), volume compared to the full probe volume):

  W wing west wall  x3000-3400 y12500-18000 z900-8700 -> 17.160 / 17.160 m3 = 100.00% solid
    fin-covered band y12800-17780                     -> 15.538 / 15.538 m3 = 100.00% solid
    ground storey  z900-4500                          ->  7.920 /  7.920 m3 = 100.00% solid
    first storey   z5000-8700                         ->  8.140 /  8.140 m3 = 100.00% solid

Zero voids. The reviewer's numbers are exact: the 9 fins (villa_3d.py:261-263) are at x 2300-2750, y 12800-17780, z 900-8700; the west flank behind them is x 3000, y 12500-18000, 5.5 x 7.8 = 42.9 m2, unbroken at both levels. The elevation confirms it visually (C:\Users\asdfv\OneDrive\Desktop\Villa\VILLA_ELEV_W.png): the fin array floats on a blank plane.

THREE THINGS THAT MAKE IT WORSE THAN CLAIMED:

1. The one piece of true west glass on the villa is left unshaded. The clerestory loop at villa_3d.py:245-247 with xx=HX0 does cut the west wall -- probe returns 0.00% solid at x 3000-3400, y 18800-23200, z 7800-8450, i.e. a 4.4 m x 0.65 m = 2.9 m2 west-facing slot. The fins stop at y 17780, 1,020 mm short of it. So the screen is not merely in the wrong place; it is on the wrong side of the only opening it could have served.

2. The fins would not work even with glass behind them. Blade 450 deep, 180 wide, 600 c/c -> clear gap 420, screen 70% open, shading cut-off = atan(420/450) = 43.0 degrees from the wall normal. At 25N the summer afternoon sun that loads a west wall arrives roughly 5-25 degrees off due west -- entirely inside the 43-degree cut-off. The array is open to precisely the sun it is named after. VILLA_RESEARCH.md:135-139 supplies the sizing method (VSA = arctan(projection / window height), east/west needs "vertical fins, deep recesses or operable louvres") and it was not applied.

3. The fins break the setting-out. They occupy x 2300-2750; the side setback line is x=3000 (SB_SIDE=3000, HX0=3000, and VILLA_RESEARCH.md:264-265 gives Gulf side setbacks as 3.0 m). They project 700 mm into the side setback -- the only element in the model that does. Flag for verification rather than treat as fatal, since many Gulf authorities permit a shading projection into a setback, but the model's own grid says every wall, slot and opening lands on the grid, and this does not.

WHY THE REVIEWER'S PROPOSED FIX IS WRONG AND MUST NOT BE BUILT:
He asks for a 4,200 x 2,900 opening (12.2 m2) in the west wall at BOTH levels. At first floor that is a bedroom window with its sill at +5,450, looking over a 2,400-high boundary wall across a 3.0 m gap directly into the neighbour's plot. In a house whose brief is a women's majlis and no dewaniya, that is not a detail, it is a brief violation. Thermally it adds 12.2 m2 x 2 = 24 m2 of the worst-oriented glass on the plot against the research envelope (WWR <30%, SHGC 0.27, VILLA_RESEARCH.md:139-140). And because a west screen must project outward, any screen sized to shade it necessarily encroaches the setback further. His fallback -- delete the fins, blank stone flank -- is the defensible half of his own proposal.

SEPARATE DEFECTS FOUND WHILE VERIFYING (not this finding, but they are in the same model and I would not want them lost):
  a) EVERY south opening is blind by 100 mm. villa_3d.py:238-244 cuts voids to y = WG_Y0 + 300 = 12,800, but the 400 wall runs y 12,500-12,900. Probe: all four south openings return exactly 25.00% solid -- a 100 mm membrane of blockwork across the full width of the living-volume structural glazing and both wing windows, at both levels. Fix: WG_Y0 + 300 -> WG_Y0 + WALL + 300 on lines 239, 243, 244.
  b) The 1.0 m light slots are sealed shafts on the wing side. W wing east wall (x 7600-8000) and E wing west wall (x 16000-16400) both return 100.00% solid; only the living volume's two flanks are pierced (47.70%). The slots light the double-height volume and nothing else, which is not what the docstring claims for them.

**Corrected fix:**

Turn the applied screen into a cut screen: delete the fins, and put the same rhythm INTO the wall as three deep slot windows at ground floor only. The west elevation keeps the striped reading the designer wanted, the shadow becomes real, the setback is respected, and the first floor stays blind for privacy.

STEP 1 -- Delete the fake device.
Delete villa_3d.py lines 260-263 in full:
    # ============================================================ west fins
    for i in range(9):
        yy = WG_Y0 + 300 + i * 600
        S.append(blk(HX0 - 700, yy, GF, HX0 - 250, yy + 180, RF))
and strike the docstring bullet at line 45 ("West brise-soleil fins - east/west CANNOT be shaded by horizontals"), which is the stated basis for a device that will no longer exist. This alone recovers the 700 mm setback encroachment and removes the defect.

STEP 2 -- Cut three west slots, GROUND FLOOR ONLY, in the formal dining room.
Room is x 3,400-7,600, y 12,900-18,250. Three slots in the west wall:
  each 700 wide (in y) x 2,650 high
  sill +1,350 (GF+450), head +4,000 (GF+3,100) -- identical to the south windows at line 243, so every ground-floor head aligns
  slot centres y 14,600 / 15,900 / 17,200 (1,300 c/c)
  slot extents y 14,250-14,950 / 15,550-16,250 / 16,850-17,550
  solid returns: 1,350 to the south wall inner face (12,900), 700 to the kitchen partition (18,250), 600 piers between slots
Insert after the other openings (i.e. where the fin loop was):
    # west slots - cut screen, ground only; first floor stays blind (side privacy)
    for yc in (14600.0, 15900.0, 17200.0):
        V.append(blk(HX0 - 300, yc - 350, GF + 450, HX0 + 700, yc + 350, GF + 3100))
Note the x range 2,700-3,700 deliberately straddles the 3,000-3,400 wall so the void fully penetrates -- do not repeat the HX0+300 pattern that leaves the 100 mm membrane on the south face.

WHY THESE NUMBERS:
  Glass area 3 x 0.7 x 2.65 = 5.57 m2 on a 42.9 m2 flank = 13% west WWR, well inside the ECBC <30% the research sets (VILLA_RESEARCH.md:139-140), against 28% for the reviewer's single picture window.
  Self-shading: each 700 wide slot in a 400 wall has a horizontal cut-off at the jamb of atan(400/700) = 29.7 degrees, and the 600 piers close the rest -- the wall does the shading, so no device projects into the 3.0 m setback at all.
  Privacy at ground is free: GF floor is +900 and the boundary wall is 2,400 high at x=350. A standing eye at +2,500 sees the wall top at 1.9 degrees below horizontal across the 3,050 gap, so nothing of the neighbour's plot is visible and nothing of the dining room is visible from it. That is exactly why the opening must be ground-only.
  First floor: bedroom 1 gets no west opening. It keeps its 2.6 m south window (line 244), 6.6 m2 on a 22.5 m2 room, which is adequate. A first-floor west window here overlooks the neighbour at 3 m and must not be cut.

STEP 3 -- Deal with the clerestory the fins were pretending to shade.
The west clerestory (x 2,900-3,600, y 18,800-23,200, z 7,800-8,450) is the only west glass in the current model and is completely unshaded. Either accept it -- 2.9 m2 at 650 mm high behind a 400 reveal is a trivial load, and I would accept it -- or deepen its reveal to 700 by changing line 246-247 to blk(xx - 100, NB_Y0 + 800, RF - 900, xx + 900, NB_Y1 - 800, RF - 250), giving a 700/650 = 47-degree jamb cut-off. Do not reintroduce an external screen for it.

IF THE CLIENT WANTS THE WEST FLANK ABSOLUTELY BLIND:
Stop at STEP 1. A blank stone side elevation 3.0 m from a boundary wall is normal, correct and defensible -- nobody ever sees it obliquely enough for the blankness to register. What is not defensible is the blank wall wearing a sunscreen, and that is what one line deletion removes.

### Upheld 46

REAL -- and it cannot be refuted, because the model contradicts the design's own written claim. Everything I could check reproduced exactly.

VERIFIED AGAINST THE GEOMETRY

1. The claimed service route does not exist. villa_3d.py:46-48 states "Three entrances (Gulf discipline): guest on the axis, family via the garage, service on the east boundary reaching the dirty kitchen without crossing guest or family space." Counting the voids that actually pierce an external wall: the guest door (x 11250-12750 in the north wall) exists; there is NO family door anywhere in the north wall -- the car porch spans x 3500-10500 and the only north opening is at x 12000, so arriving by car you walk out of the porch and in through the guest door; and the "service" door lands in the majlis (below). One of three claimed entrances is real.

2. No dirty kitchen, no pantry. villa_sheets.py:27-35 lists seven ground rooms totalling 150.3 m² net; none is a dirty kitchen or pantry. The basement is genuinely undivided: lines 128-132 are a raft, a shell, one hollowing void and the court void -- no partitions, no rooms, and no stair down to it at all (the only stair in the model is the 16-riser GF→FF flight at x 13000-14600). So the scheme's stated resolution -- "staff, laundry, store and all plant go into a SEMI-BASEMENT" (line 24-26) -- is an assertion with no geometry behind it, and even if it had, VILLA_RESEARCH.md:323 requires the dirty/wet kitchen to sit beside the show kitchen with its OWN external door, which a basement cannot provide.

3. The 7.07 m traverse is exact. Door void centres from DOORS_GF: hall→kitchen (8500, 22100), hall→majlis (15500, 21100). Distance = 7071.1 mm, straight across the ENTRANCE HALL (8575-15425 × 20550-23600), directly past the front door on the axis at x 12000, and in view of the double-height volume, which the code deliberately leaves open to the hall (line 202-203). Every coffee tray to the women's majlis crosses the guest arrival space.

4. The service door lands in the women's majlis. villa_3d.py:257-258 cuts x 20700-21300, y 18700-19800. At the inner face (x 20600) that band falls inside WOMEN'S MAJLIS (15575-20600 × 18400-23600) and nowhere else -- the majlis|study partition is at y 18250-18400, well south of it. It is 12.82 m from the kitchen door it is supposed to serve. Two details make it worse, not better: the void starts at x 20700 but the wall spans 20600-21000, so it leaves 100 mm of wall standing and is not an opening at all as modelled (the guest entrance has the same 100 mm defect); and the east BOUNDARY wall (x 23650-24000) has no opening whatsoever -- the only two gates, lines 284-285, are both in the north wall -- so the "east boundary service route" has no gate to enter by.

5. The study is unbriefed and is 22.47 m² (4200 × 5350) -- confirmed. The brief asks for 4 bedrooms, women's majlis, family living, pool, garden, 2 cars, gate, wall, semi-basement. No study.

WHY IT IS NOT TASTE. The requirement is not mine or the reviewer's -- it is the project's own sourced research (VILLA_RESEARCH.md:348-354): a separate service door to the dirty kitchen without crossing guest or family space, and "a short service corridor behind the show kitchen with a discreet door into the majlis." The model does the precise opposite, and the docstring claims otherwise. A false claim contradicted by the geometry is a defect. And in the Gulf context a service door opening into the women's majlis -- the one room where unrelated women sit unveiled -- is the single most serious privacy error available in this plan type; any reviewer with 20 years' experience flags it in the first minute.

WHERE THE REVIEWER IS WRONG. Two small inaccuracies (neither weakens the finding): the door punches the house's east external wall, not the boundary wall 2.65 m beyond it (which is blind); and the study is in the south wing, not on the north-bar service frontage -- the majlis holds that frontage.

More importantly, THE PROPOSED FIX DOES NOT WORK. Swapping kitchen and majlis just mirrors the defect: coffee would then run 7 m east-to-west across the same hall. The reason is structural, not incidental -- the axial link from the entrance hall into the double-height volume (x ~10500-14600, y 18400-20550) plus the stair at x 13000-14600 block the entire south edge of the north bar, so NO ground-level service corridor can pass from the west end to the east end without cutting through the compression-release that is the whole parti. Kitchen and majlis therefore cannot be joined horizontally. Nor can they be paired on the east: majlis 26 + show 21 + dirty 13 + pantry 5 ≈ 65 m², against 48.6 m² available (NE block 26.13 + east wing 22.47). The fix has to serve the majlis vertically, which is exactly what the scheme's own semi-basement strategy already implies. That is what my corrected fix does.

INCIDENTAL, SEPARATE DEFECTS I hit while measuring (not part of this finding, but they share the root cause -- rooms butted together with doors punched between them and no circulation strategy): the formal dining is reachable only through the show kitchen; on the first floor Bedroom 1 is reachable only through Bedroom 3 and Bedroom 2 only through the master bedroom; the sunken court void (9500-14500 × 15400-19400, cut from BASE_FL up to GF+200) removes 15.0 m² of the FAMILY LIVING floor slab and the hall-to-living link; and the stair is 16 × 244 = 3904 mm against a 4100 mm floor-to-floor, 196 mm short.

**Corrected fix:**

Serve the majlis VERTICALLY from the semi-basement, and put the dirty kitchen where the research says -- beside the show kitchen with its own external door. No footprint growth; ground stays 196 m², GFA 407 m². All partitions 150 mm, doors 900 mm unless noted.

A. SERVICE DOOR -- relocate and make it real (villa_3d.py:257-258).
Replace blk(HX1-300, NB_Y0+700, GF, HX1+300, NB_Y0+1800, GF+2400) with
blk(20500, 18600, GF, 21100, 19600, GF+2100) -- x 20500-21100 fully cuts the 400 mm wall (20600-21000) instead of leaving 100 mm standing, and y 18600-19600 now lands in the servery, not the majlis. Apply the same +200/-200 correction to the guest-entrance void (line 248-249), which has the identical 100 mm residual.

B. MAJLIS SERVERY -- 2000 × 2400 = 4.80 m², at x 18600-20600, y 18400-20800 (the majlis's south-east corner). New partitions (18450,18400,18600,20800) and (18600,20650,20600,20800). A 900 mm discreet door at x 18600-19500 in the y 20650-20800 partition -- in the corner, off the majlis's main face. Fit a 900 × 900 DUMBWAITER plus a 600 mm coffee counter; it drops to the basement scullery directly below. This is the researched "discreet door into the majlis", and the hall traverse becomes 0 m.

C. MAJLIS RESTORED TO 30.78 m² (research 25-35). Delete the partition (16400,18250,20600,18400) and let the majlis run south into the east wing to y 16000: 26.13 − 4.80 (servery) + 9.45 (annex 4200 × 2250) = 30.78 m². The 1.0 m east light slot glazes the step at x 15575/16400, giving the annex a full-height slot of daylight.

D. DELETE THE STUDY (22.47 m²) and give the east wing's south end to the majlis:
  MAJLIS ANTE / PRAYER  x 16400-18600, y 12900-16000 = 2200 × 3100 = 6.82 m²
  WOMEN'S GUEST WC      x 18600-20600, y 12900-14700 = 2000 × 1800 = 3.60 m²  (research 3.5-5; today the majlis's nearest WC is 7 m away across the front door)
  LINEN / STORE         x 18600-20600, y 14700-16000 = 2000 × 1300 = 2.60 m²

E. PANTRY off the show kitchen -- 1600 × 3000 = 4.80 m² at x 3400-5000, y 18400-21400 (research 4-6). SHOW KITCHEN becomes L-shaped at 26.13 − 4.80 = 21.33 m² (research 20-28). A 900 mm door at x 3700-4600 through the y 18250-18400 partition links the pantry straight down to:

F. DIRTY / WET KITCHEN -- 4200 × 3250 = 13.65 m² at x 3400-7600, y 15000-18250 (research 12-18), directly under the show kitchen, i.e. literally the "short service corridor behind the show kitchen". Its OWN external door: blk(2900, 15900, GF, 3500, 16900, GF+2100) in the west wall. Delete the two brise-soleil fins that foul it -- i = 5 and i = 6 in the fin loop (yy = 15800 and 16400); a gap at the service door is honest and reads as such.
  STAFF STAIR + STORE CORE  x 3400-7600, y 12900-15000 = 4200 × 2100 = 8.82 m², enough for a three-flight stair (21 risers @ 176, flights 7/7/7, 1.6 m runs) down the 3700 mm to BASE_FL −2800, plus bin/gas store.

G. SERVICE GATES (the boundary wall currently has none -- only the north vehicle gate x 3800-8300 and north pedestrian gate x 15400-16600). Add a 1000 mm gate in the WEST boundary wall at y 15400-16400 feeding the dirty-kitchen door down the 2.65 m west side strip, and a 1000 mm gate in the EAST boundary wall at y 17000-18000 feeding the servery supply door down the 2.65 m east strip.

H. BASEMENT -- subdivide it and connect it. Under the servery put the SCULLERY / STAFF KITCHEN at the dumbwaiter (x 18600-20600, y 18400-20800, 4.8 m²); then staff bed 11 + bath 4 + laundry 10 + stores 12 + plant 16 + pool plant 14 in the remaining 142 m². Move the sunken court OUT of the living-room floor to the east side strip: x 21000-23400, y 15400-20400 = 12.0 m², open to sky, with an external staff stair from the new east gate down to BASE_FL. This gives the basement real daylight and its own staff entrance (F.LOT, as the scheme intends), and it repairs the 15.0 m² hole the present court (9500-14500 × 15400-19400) cuts through the FAMILY LIVING slab and the hall-to-living link.

I. THE COST, stated honestly. Steps E-F consume the west wing, so the separate FORMAL DINING (22.47 m²) goes; the double-height volume becomes a LIVING / DINING great room (28.60 m², 7.30 m clear). That is the trade the research's own arithmetic forces -- its workable schedule needs ground ≈ 205 m² and this ground floor is 196 m² gross / 150.3 m² net. Deleting the unbriefed study and the duplicated dining is exactly what pays for the service package.

J. Rewrite villa_3d.py:46-48 to describe what is built: guest entrance on the axis; service on the WEST strip to the dirty kitchen and on the EAST strip to the servery and the staff court; and either model a family door from the car porch into the north wall (e.g. blk(9200, 23500, GF, 10400, 23900, GF+2400) into the kitchen lobby) or drop the three-entrance claim.

RESULT: service route to the majlis = basement scullery → dumbwaiter → servery → discreet door → majlis. Guest space crossed: none. Family space crossed: none. Hall traverse: 0 m, down from 7.07 m. Dirty kitchen 13.65 m² with its own external door; pantry 4.80 m²; majlis 30.78 m² with its own 3.60 m² WC; service door lands in service space.

### Upheld 47

I tried to refute this and could not. Every citation verifies against C:\Users\asdfv\autocad-mcp\villa_3d.py:

1. Front wall (line 281) runs y 28650..29000 at BH = 2400 (line 279) -- the gate void (line 284, x 3800..8300) is cut through the property-line wall. Standing space inside the plot is genuinely 0 mm. VILLA_RESEARCH.md:288 does ask for 5.5-6.0 m between gate line and street.
2. Court depth: house north face NB_Y1 = 24000 to wall inner face 28650 = 4650 mm, exactly as claimed. Hammerhead deficit 5500 - 4650 = 850 mm; forecourt deficit 12000 - 4650 = 7350 mm. Arithmetic correct.
3. No visibility splay: the front wall is solid at full 2400 mm for 3800 mm west of the vehicle gate and 7100 mm east of it (to the pedestrian gate). Unbroken to both jambs, confirmed.
4. Wall height: BH = 2400 is applied to all four boundaries including the street frontage, while the project's OWN research (VILLA_RESEARCH.md:279-281) puts Gulf front walls at 1.8-2.0 m, sometimes with the top 600 mm required open, some jurisdictions capping the front at 1.2-1.5 m solid + screen. That is an internal contradiction between the design and its stated basis, not a matter of taste.
5. No escape route exists. I checked whether the car could turn anywhere else: the front rill (lines 273-276) sits 150 mm proud with a 300 mm channel across x 11500..12500, and the gate is at x 3800..8300, west of it -- so the eastern 11.15 m of forecourt is not vehicle-accessible at all. The reachable envelope is 11.15 x 4.65 m. Reversing onto the street is mandatory.

The reviewer also UNDERSTATED the defect. Framing it as a turning-circle problem buries the sharper fact: the court is shorter than the car. At 4650 mm clear a Golf (4284) fits; an E-Class (4949), Range Rover LWB (5252), GLS (5207) and Escalade (5766) do not. On a villa pitched at US$5M the client's own car cannot stand inside the closed gate -- its tail sits in the gate reveal. Related: the porch is modelled at 7.0 x 4.0 m (PORCH_Y0/Y1 = 24400/28400, lines 110-111) while its own docstring on line 109 claims "2 cars, 7.0 x 5.2", and villa_sheets.py:88 prints "COVERED CAR PORCH 2 CARS" onto sheet A-201. The drawing asserts a capacity the geometry does not deliver.

Where I do push back: "fatal" overstates it. A gate on the boundary with a reverse-out is the ordinary condition for a walled Gulf villa on a 5 m setback, and VILLA_RESEARCH.md:293-294 explicitly sanctions it -- "Realistically accept reversing and shape the apron for one straight movement." The reviewer concedes the 5.5-6.0 m standing space is unattainable here, so that component is a plot constraint, not a design error. The design's failure is that it does not shape the apron, does not provide the splay, and does not fit the car. Severity is serious/major, not fatal. The reviewer's fix is also directionally right but self-defeating on one point: recessing the gate 1500 mm subtracts from an already-deficient 4650 mm court, leaving 3150 mm. The depth has to be found from the house, not from the court.

**Corrected fix:**

Four changes. The governing insight the reviewer missed: court depth and gate recess are zero-sum inside a 5.0 m setback, so the depth must come off the house.

1. FIND THE COURT DEPTH FROM THE HOUSE (fixes the car-doesn't-fit defect)
Recess the GROUND-FLOOR north face by 500 mm over the porch width only. Split the north-bar rectangle in GF_FOOT (villa_3d.py:138) into (HX0, NB_Y0, 10500, 23500) + (10500, NB_Y0, HX1, NB_Y1); leave FF_FOOT unchanged so the first floor oversails 500 mm over the arrival -- a gain, not a loss. Shorten the kitchen|hall partition (line 188) from y 23600 to 23100.
  - Court becomes 23500 -> 29000 = 5500 mm clear, with the slider leaf hung on the OUTER wall face (y 29000) rather than mid-thickness, which is where the last 350 mm comes from.
  - Takes any vehicle up to 5400 mm with 100 mm to the closed leaf.
  - Cost: 7500 x 500 = 3.75 m2 of ground floor. Kitchen 26.1 -> 23.6 m2 (research show-kitchen range 20-28, still compliant). Hall loses 0.96 m2. GFA 407 -> 403 m2.
Re-set the porch to PORCH_X0/X1 = 3300/10800 and PORCH_Y0/Y1 = 23700/28700 -- 7.5 x 5.0 m, the first version that honestly carries two cars (2 x 2.7 m bays + 900 between + 600 to each side = 7.5 m; research min 5.5 x 5.5, comfortable 6.0 x 6.5). Move the blade wall (line 256) to x 10550..10800, leaving 450 mm clear of the guest-entrance glazing at x 11250. Correct the line 109 docstring and the villa_sheets.py:88 label to the built 7.5 x 5.0.

2. FRONT WALL -- 1800 mm, NOT 2400 (fixes the code exposure, and is what actually restores sight)
Replace the single front-wall block at line 281 with a banded wall: 1200 mm solid stone + 600 mm open screen (60 mm slots at 120 mm centres) = 1800 mm overall. Sides and rear stay at 2400 mm -- pool and garden privacy is unaffected, since it is the arrival court that opens up, not the garden. This brings the frontage inside the researched 1.8-2.0 m band at VILLA_RESEARCH.md:279-281 and removes the likely breach.

3. VISIBILITY SPLAY -- 2.4 x 3.0 m both ways
Over 3000 mm each side of the vehicle opening (x 1250..4250 and 9750..12750) drop the front wall to 900 mm solid with NO screen above. 900 mm is below eye height in every seated car and below standing pedestrian eye height, so the driver has real two-way sight before the nose reaches the footpath. This is worth more than the reviewer's 2.4 x 2.4 m notch: on a 30 km/h street the y-distance for a true splay is 25-33 m along the kerb, unattainable behind any wall -- the answer is to make the wall transparent at eye height across the whole crossover, not to notch it.

4. GATE -- widen, and meet the standing requirement with time rather than depth
  - Vehicle opening 4500 -> 5500 mm clear, x 4250..9750, centred on the 7.5 m porch (line 284). A wider crossover puts the driver's shoulder past the wall line before the nose reaches the footpath, and lets the car enter and leave on a skew without a shunt.
  - Cantilever slider running EAST: run-back = opening + 500 = 6000 mm, x 9750..15750. That clashes with the pedestrian gate, so move it (line 285) from x 15400..16600 to x 16400..17600.
  - High-speed slider at 0.5 m/s (5500 mm in 11 s) + long-range UHF RFID + inductive safety loop inside the leaf line, so the gate is open on approach. Inside a 5.0 m setback the standing requirement can only be met in the time domain -- there is no depth to buy it with, and the reviewer is right to concede that.
  - Shape the apron for one straight movement (the research's own instruction): keep the court clear east of the porch to x 11500 so the reverse runs straight on the porch centreline, 5.5 m to the leaf line, not on a curve.

RESIDUAL, STATED HONESTLY: the exit is still a reverse onto the street. Nothing on a 24 x 29 m plot with a 5 m front setback and a 3.9 m rill on the centre axis avoids that, and the reviewer's fix does not avoid it either -- their "straight-in/straight-out" claim is contingent on a separate garage fix. What these four changes deliver is that the car fits inside the closed gate, the reverse becomes one straight sighted movement instead of a blind curve, the crossover gets a real splay, and the frontage stops contradicting the project's own research.

### Upheld 48

CONFIRMED -- real, and it is a modelling defect, not a matter of taste.

MECHANISM. `shell()` (villa_3d.py:144-151) builds the wall as `ring = fp - offset(fp, -WALL)`, so the wall band occupies the 400 mm measured INWARD from the outer face. Every envelope void, however, is dimensioned ±300 about that same outer face. 300 < 400, so 100 mm of wall survives on the inside of each opening.

VERIFIED IN THE DERIVED GEOMETRY (I parsed the shipped DXFs, which carry the same mtime as villa_3d.py, so they are current):

VILLA_PLAN_GF.dxf, cut at z=2100 --
  front door: outer face y=24000 breaks at x 11250-12750, drops to y=23700; inner face y=23600 runs UNBROKEN x 8575→15425. 100 mm skin x 1500 wide.
  garden glazing: outer 12500 breaks 9200-14800 to 12800; inner 12900 continuous 9400→14600. 100 mm x 5600.
  wing windows: outer 12500 breaks 4200-6800 to 12800; inner 12900 continuous 3400→7600. Same on the east wing (17200-19800).
  service door: outer x=21000 breaks y 18700-19800 to 20700; inner 20600 continuous 18400→23600. 100 mm x 1100.
VILLA_PLAN_FF.dxf -- the wing bands repeat the same signature at first floor (line 244).

So the front door on the water axis is a 1500 x 2400 x 300 mm niche, and there is no way into or out of the house at ground level. Every derived plan, section and elevation inherits it, which defeats the file's own premise that the drawings cannot disagree.

THE REVIEWER'S EXCLUSIONS ARE ALSO CORRECT. The two clerestories (245-247, ±100/+600 across a 400 band) cut through. So does the first-floor glazing at 240-241 (void y 12200→13200 across the 12500-12900 band) -- the FF plan shows only the two 200 mm nibs at x 9000-9200 / 14800-15000, no continuous inner face. Both boundary-wall gates (284-285) cut through as well. So the failing set is exactly the five lines named.

TWO CORRECTIONS to the report, neither of which touches the verdict:
1. Count. It is 7 opening instances across 5 source lines, not 6 -- lines 243 and 244 each loop over two x-ranges, so the wing bands fail at both ground AND first floor.
2. The claim "this is why VILLA_ELEV_S.png reads as four shallow punched squares" is a wrong causal attribution. The fix does not change the south elevation at all: the outer-face outline of every opening is identical before and after, and `Drawing(..., with_hidden=False)` never drew the inner face. I re-cut and compared -- the elevation linework is unchanged. The flat elevation is a compositional problem with the opening proportions (2.6 x 2.65 m and 2.6 x 2.25 m punched squares), a separate criticism. The symptom of THIS bug is a hermetically sealed solid, not a flat drawing.

I APPLIED AND RE-DERIVED THE FIX. After the five edits the GF plan reads: inner face y=23600 broken at 11250-12750 with both jambs running the full 23600→24000 depth; y=12800 and y=12900 gone across 9200-14800; inner face 20600 broken at 18700-19800. All openings pierce. Every printed metric is unchanged (GFA 407 m2, footprint 196 m2, coverage 28%, 7.30 m clear, 1:3.0), because the fix removes only 100 mm slivers of air. I checked for collateral damage: the 100 mm inward overshoot lands in open floor at all seven sites -- no PARTS_GF/PARTS_FF partition, no stair (all at y >= 18250 or x 13000-14600), and no slab is touched.

ONE ARTEFACT WORTH KNOWING ABOUT, present in the original and merely deepened by the minimal fix: the garden glazing's x range (LV_X0+200 .. LV_X1-200 = 9200..14800) straddles the flanking return walls, whose inner faces are at 9400 and 14600. The deepened void therefore notches 200 x 100 mm out of each inner corner -- visible in the re-cut plan as new stubs at y=13000, x 9200-9400 and 14600-14800. Detail it as the structural-glazing channel, or take the clean option in the fix below.

ADJACENT (out of scope, flag separately): with the envelope openings enumerated, guest bedroom 3 and the master -- both in the north bar at first floor -- have no opening at all except one 700 mm clerestory slot at the extreme west/east end. No view window, no north light. That is a separate defect and this fix does not address it.

**Corrected fix:**

Five lines in C:\Users\asdfv\autocad-mcp\villa_3d.py. The rule: an envelope void must run from 300 OUTSIDE the outer face to WALL+100 INSIDE it, i.e. span 800 mm across a 400 mm wall, never 600.

1) Ground structural glazing, line 238-239 -- y1: 12800 -> 13000
   V.append(blk(LV_X0 + 200, WG_Y0 - CANT - 300, GF + 100,
                LV_X1 - 200, WG_Y0 + WALL + 100, GF + 3400))

2) Wing window band, ground, line 243 -- y1: 12800 -> 13000 (both x ranges)
   V.append(blk(x0, WG_Y0 - 300, GF + 450, x1, WG_Y0 + WALL + 100, GF + 3100))

3) Wing window band, first floor, line 244 -- y1: 12800 -> 13000 (both x ranges)
   V.append(blk(x0, WG_Y0 - 300, FF + 450, x1, WG_Y0 + WALL + 100, FF + 2700))

4) Guest entrance on the axis, line 248-249 -- y0: 23700 -> 23500
   V.append(blk(AXIS - 750, NB_Y1 - WALL - 100, GF, AXIS + 750,
                NB_Y1 + 300, GF + 2400))

5) Service entrance, line 257-258 -- x0: 20700 -> 20500
   V.append(blk(HX1 - WALL - 100, NB_Y0 + 700, GF, HX1 + 300,
                NB_Y0 + 1800, GF + 2400))

LEAVE ALONE -- already correct, do not "fix" them: lines 240-241 (FF glazing, 12200->13200), 245-247 (clerestories, -100/+600), 284-285 (boundary gates).

OPTIONAL, recommended with (1): change the glazing's x limits from LV_X0 + 200 / LV_X1 - 200 (9200/14800) to LV_X0 + WALL / LV_X1 - WALL (9400/14600). The opening becomes 5.2 m clear instead of 5.6 m, sits exactly between the inner faces of the flanking walls, and stops notching their corners. Keep 9200/14800 only if you intend that 200 x 100 mm rebate as the glazing channel and will draw it.

VERIFICATION after re-running (I ran this; these are measured, not predicted):
  VILLA_PLAN_GF.dxf  y=23600 breaks at x 11250-12750; jambs x=11250 and 12750 span 23600->24000
  VILLA_PLAN_GF.dxf  y=12800 and y=12900 both absent across x 9200-14800 and x 4200-6800
  VILLA_PLAN_GF.dxf  x=20600 breaks at y 18700-19800
  VILLA_PLAN_FF.dxf  y=12900 breaks at 4200-6800 and 17200-19800
  metrics unchanged: GFA 407 m2, footprint 196 m2, coverage 28%, DH 7.30 m, 1:3.0
Acceptance test worth adding to the script so this cannot regress: for each envelope opening, assert the plan section contains no continuous inner-face segment spanning the opening's width.

### Upheld 49

Real, and the model is worse than the reviewer states. I could not refute it. I rebuilt the model and probed it rather than reading the source alone.

CONFIRMED -- the box is blank. Probing each face of the box (x 9000-15000, y 9500-12900, z 5000-8700) with thin slabs and measuring the solid fraction: south face y=9500 is 1.000 solid, west x=9000 is 1.000 solid, east x=15000 is 1.000 solid. The only opening is in the north face (0.344 solid), which faces into the double-height shaft. The reviewer's y-range for lines 240-241 is slightly off (the void is y 12200-13200, not 12200-12900, because it is WG_Y0 + WALL + 300) but the substance is exactly right: it is the box's north wall. The rendered VILLA_ELEV_S.png shows it -- the wings each carry two openings, and the centre plane, the closest and most exposed surface in the composition, is one unbroken rectangle from the pool coping to the parapet (22.2 m2 of wall, or 32 m2 counting the flush roof edge and 1100 parapet above it, which are also unrelieved).

CONFIRMED -- nothing occupies it. villa_sheets.FIRST schedules seven rooms; the minimum y of any of them is 12900, so every scheduled first-floor room is north of the box. The FIRST schedule nets 131.6 m2 against a printed first-floor GFA of 181.0 m2, of which exactly 18.0 m2 is the cantilever (ct = area(LV_X0, WG_Y0-CANT, LV_X1, WG_Y0) at line 293, summed into ff at line 295). So 18 m2 of the advertised 407 m2 GFA / 4,381 sq ft is a room that does not exist in any drawing.

WORSE THAN CLAIMED -- the box is not reachable. The first-floor footprint union (FF_FOOT, line 140-142) resolves to TWO disconnected faces. The box is x 9000-15000, y 9500-12900; the wings are at x 3000-8000 and 16000-21000, and the light slots (lines 174-177) cut x 8000-9000 and 15000-16000 through every level, so there is no lateral contact either. Probing the 5.1 m gap between the box's north wall and the north bar (y 12900-18000, x 9000-15000): slab zone z 4500-5000 is 0.0000 solid, and z 5000-5100 is 0.0000 solid. There is no floor, no bridge, no landing. Its interior -- 5.2 x 2.6 m = 13.5 m2, 1.000 void -- is a sealed volume you could only enter by stepping off a 4.1 m drop into the living room. It is not an unfurnished room; it is an unenterable one.

The "it was always meant as a solid shading canopy" defence does not survive the model: a canopy would be a slab, not a 3.7 m storey with a floor slab, a four-sided 400 mm wall ring, a hollow interior, a 5.6 x 2.6 m room-sized opening, and 18 m2 booked into GFA. Either reading is a defect -- an unreachable blank room, or a canopy modelled as a fake storey and counted as floor area.

Not taste, not a matter of composition preference: three probes at 1.000 solid, a footprint that resolves to two islands, 0.0000 floor material in the connecting gap, and a 49.4 m2 gap between the schedule and the printed first-floor area. Severity "fatal" is fair -- it is the element that terminates the entry axis and hangs over the pool.

Collateral finding while probing, worth passing on: the openings the reviewer calls "the current punched holes" are not holes either. Lines 238 and 242-243 cut y0-300 to y0+300, which penetrates only 300 mm of the 400 mm wall. Measured solid fraction through the wall band: ground-floor structural glazing onto the pool 0.250, wing windows 0.250. Every south-facing opening in the villa is a 300 mm recess with a 100 mm concrete skin behind it. Only lines 240-241 (the internal one) use the correct +WALL+300 form and actually go through.

**Corrected fix:**

CORRECTED FIX -- four edits to villa_3d.py plus one to villa_sheets.py. The reviewer's fix (glaze 5200x2400, sill +750, 600 reveal) is directionally right but cannot be built as written: it glazes a room with no floor leading to it, and its 600 mm reveal does not shade anything at this latitude.

1. DEEPEN THE BOX SO IT CAN HOLD A ROOM (it is currently 2.6 m clear -- no room fits)
   - line 142, FF_FOOT rect 4: (LV_X0, WG_Y0 - CANT, LV_X1, WG_Y0 + WALL) -> (LV_X0, WG_Y0 - CANT, LV_X1, WG_Y0 + 1600), i.e. x 9000-15000, y 9500-14100.
   - line 162, the slab void MUST follow or it eats the new floor: blk(LV_X0 + WALL, WG_Y0, ...) -> blk(LV_X0 + WALL, WG_Y0 + 1600, ...). Without this you get a 5.2 x 1.6 m hole in the room's floor.
   Result: clear interior 9400-14600 x 9900-13700. Double-height void becomes 5.2 x 4.3 m, still 7.30 m clear, and the release still happens at the hall threshold because the void is on the hall side.

2. CONNECT IT (the reviewer missed this; it is the harder half of the defect)
   - Gallery slab: blk(12900, 14100, 4500, 14600, 18000, 5000) -- 1.70 m wide x 3.90 m long, along the east edge of the void, landing on the head of the existing stair (x 13000-14600).
   - Guard: blk(12900, 14100, 5000, 13050, 18000, 6100) -- 150 thick x 1100 high, leaving 1.55 m clear walking width.
   - Cut the north-bar south wall so the landing reaches the gallery: V.append(blk(12900, 17900, 5000, 14600, 18500, 7400)) -- 1700 x 2400 through the 400 band at y 18000-18400. That wall is presently solid, so the landing also currently faces a blind wall where it should overlook the living volume.
   - Re-point the existing internal opening (lines 240-241) to the box's NEW north wall: blk(9200, 13400, 5300, 14800, 14400, 7900) -- 5.6 m wide x 2.6 m high. The gallery arrives through it and the room reads both ways: south to the pool, north down into the double-height living room.
   - Dependency: the stair is 196 mm short of the first floor (16 risers x 244 = 3904 from GF 900 -> 4804, vs FF 5000). Use 17 risers at 241.2 (4100/17) or the gallery is not reachable either.

3. THE SOUTH FACE -- cut it, and cut it THROUGH
   V.append(blk(LV_X0 + 400, WG_Y0 - CANT - 300, FF, LV_X1 - 400, WG_Y0 - CANT + WALL + 300, FF + 3100))
   = x 9400-14600 (5200 wide), y 9200-10200, z 5000-8100 (3100 high, floor to a 600 soffit downstand below the 8700 ceiling).
   Note the y form: -300 -> +WALL+300. The existing openings at lines 238 and 242-243 use y0-300 -> y0+300, which cuts only 300 mm of the 400 mm wall -- measured, those "windows" are still 25% solid, i.e. 300 mm recesses with a 100 mm concrete skin behind. Do not copy that pattern into the new opening.
   Full height with a 600 downstand, not the reviewer's 5200 x 2400 with a 750 sill: a punched hole with a sill repeats the wing language on the one plane that must not look like the wings.

4. REAL REVEAL + REAL SHADE (the reviewer's 76 deg VSA is the wrong target)
   - Head lining to set the glass 900 back from the outer face: S.append(blk(9400, 9900, 8100, 14600, 10400, 8700)). Glass plane y = 10400. The jambs need nothing added -- the box's 9000-9400 and 14600-15000 side walls already run the full depth, so the reveal is 900 on head and both jambs; the floor slab already returns to the face as the cill.
   - Shadow blade at the head: S.append(blk(9200, 8900, 8100, 14800, 9500, 8250)) -- 600 deep x 150 thick, projecting 600 beyond the box face. Total overhang above the glass head = 900 reveal + 600 blade = 1500 mm.
   - Why 1500: at ~25 deg N a due-south opening needs P = H/tan(65 deg) = 3100/2.145 = 1446 mm to be fully shaded at equinox noon. 1500 gives VSA 64.2 deg -- the whole opening in shade across the entire cooling season, while winter sun (altitude 41.6 deg) drops only 1330 mm below the head and washes the lower 1770 mm of glass. The reviewer's 600 reveal on a 2400 opening gives VSA 76 deg, which at 25 deg N is exceeded only from about mid-May to late July around solar noon -- it shades essentially nothing, so their own criticism of the punched holes applies to their fix.
   - Keep the roof slab and parapet flush at y 9500. Extending them to shade instead would push the roof cantilever to 4.05 m, past the 2.5-3.5 m band the model's own docstring cites.

5. SCHEDULE IT -- villa_sheets.py FIRST:
   ("UPPER FAMILY ROOM", 9400, 10400, 14600, 13700, "habitable")  -> 5.2 x 3.3 = 17.2 m2
   ("GALLERY",           12900, 14100, 14600, 18000, "circulation") -> 1.7 x 3.9 = 6.6 m2
   Programme it as the upper family room (majlis al-aila) serving the four bedrooms, not the master bed head -- the master sits at x 15575-20600 in the north bar and its head cannot move 6 m across the void without replanning that wing.

EFFECT ON THE PRINTED FIGURES: the counted cantilever area rises 18.0 -> 27.6 m2, first floor 181 -> 190.6 m2, GFA 407 -> 417 m2 = 4,485 sq ft (424 m2 / 4,555 sq ft if the gallery is counted) -- closer to the 418 m2 / 4,500 sq ft brief than the current model, and every square metre of it now has a name and a door.

### Upheld 50

REAL, but only about half of it. The headline -- no car fits between the gate and the house -- is a genuine, verified, fatal-grade defect. The second half of the argument (bay 2 unreachable, capacity one car) is wrong and should not be repeated.

CONFIRMED BY DIRECT MEASUREMENT OF villa_3d.py:

1. Comment/model mismatch is real. Line 109 says "2 cars, 7.0 x 5.2"; lines 110-111 set PORCH_X0..X1 = 3500..10500 and PORCH_Y0..Y1 = 24400..28400, i.e. 7.0 x 4.0 = 28.0 m2. A 1,200 mm discrepancy, and the 5.2 m was never achievable anyway.

2. The 4,650 mm hard limit is real and is the actual defect. The villa's north face is NB_Y1 = 24000; the north boundary wall is PLOT_D - BW = 28650 inner face (villa_3d.py:281, BW = 350). Absolute clear depth between them = 4,650 mm. Nothing in the scheme can be parked deeper than that. Measured against real Gulf-villa cars: Land Cruiser 300 (4,985) overhangs the wall inner face by 335; Range Rover LWB (5,200) by 550; Mercedes GLS (5,210) by 560. Even a Camry (4,885) overhangs by 235. The gate void is cut at y 28450..29200 (villa_3d.py:284), so the gate leaf plane sits inside 28650..29000 -- those tails are physically in the gate's path and it cannot close. With the reviewer's 300 mm at each end the longest car that stands behind a closed gate is 4,050 mm. That is a Golf, on a plot whose brief is a US$5M villa. Confirmed.

3. The research shortfall is real. VILLA_RESEARCH.md:295-296 gives "Garage 2 cars: min 5.5 x 5.5 (30 m2)". The porch is 4.0 m on the governing dimension (4.65 m absolute) -- 27% short as drawn, 15% short even counting the uncovered strip. Line 300 also notes the basement-ramp escape is impossible on a 29 m plot, so there is no fallback in the scheme.

4. An unflagged supporting defect: the module docstring (villa_3d.py:47) promises "family via the garage" as one of three entrances. There is no garage anywhere in the model -- the north bar's west end is SHOW KITCHEN (villa_sheets.py:28). The third entrance does not exist.

REFUTED -- these parts of the criticism do not stand:

5. "The beams at 3600 and 6900 imply two bays." They do not. Line 254 places those beams at z = GF+2900 to GF+3150, i.e. 3,800..4,050 mm above street level. They are overhead members; cars park under them. The only ground-level obstruction inside the porch is the blade wall at x 10250..10500 (line 256). Clear drivable width at car height is therefore x 3500..10250 = 6,750 mm, continuous. There is no fixed bay geometry for a car to be "2,650 mm off the centreline of".

6. "Bay 2 cannot be entered by any vehicle; capacity is one car." False, and it follows only from (5). Two 2.5 m bays fit anywhere within 6,750 mm of clear width, and the reviewer's reverse-curve figure (7,307 mm, which is arithmetically correct for a two-arc curve at R = 5,700, d = 2,650) assumes the whole lateral shift must occur between the gate face and y = 24400. It does not: the approach and alignment happen on the street outside the gate, which is how every villa driveway on earth works. With the bays centred on the gate rather than on the beams, the required shift is ~125 mm, not 2,650. Capacity is two cars in width -- the problem is that neither of them is short enough to fit in depth.

7. Minor overstatement: a 5.0 m car's tail lands 350 mm past the wall's INNER face, not past the property line (which is a further 350 mm out at y = 29000). The operative conclusion -- the gate cannot close -- is unaffected.

So: the criticism is real, the severity is right, the mechanism is half wrong. It is a depth failure, not a manoeuvring failure, and the fix has to buy depth, not realign bays.

**Corrected fix:**

CORRECTED FIX -- recess the carport into the building line under the first floor, rather than build a garage in the north bar.

The reviewer is right that the cars must come inside the building line, but their fix does not work: a garage at y 18000..23600 is not 5.6 m internal -- 18000 is the structural line and the north bar's clear depth is 18400..23600 = 5,200 mm, which is exactly the 5.5-6.5 m shortfall villa_3d.py:250-252 already rejected. Two 2.7 m doors in a 6.0 m wall leave ~150-300 mm piers (unbuildable; the research's "two 2.7 m doors" assumes a 6.5-7.0 m luxury garage). And an enclosed garage at ground level collides with GF = +900: either the garage floor sits at 0 and you get a 1.8 m dead void under the first-floor slab, or it sits at +900 and you must climb 900 mm inside a 4,650 mm apron -- a 19% ramp. The fix also evicts the show kitchen into the formal dining and leaves the dining homeless.

Instead, notch the GROUND floor only and let the first floor oversail it. All dimensions in mm, villa_3d.py coordinates.

1. NORTH-FACE NOTCH (villa_3d.py, ground shell). Over x 3000..9300, pull the north-bar exterior wall back from y 23600..24000 to y 22400..22800. Notch depth 1,200. Add a 400 wall at x 8900..9300, y 22800..24000 forming the notch's east cheek and the hall's new west wall. FF_FOOT is UNCHANGED -- the first floor stays at 18000..24000 full width, so the slab cantilevers 1,200 over the carport. That is a 1.2 m RC cantilever against the 3.0 m one the scheme already carries over the pool, and it gives a covered carport with zero added structure.

2. CARPORT. Clear x 3400..8900 = 5,500; clear y 22800..28650 (boundary-wall inner face) = 5,850. Area 32.2 m2 -- beats the research minimum 5.5 x 5.5 / 30.25 m2 on BOTH dimensions, not just the product. Two bays at 2,750 (research: 2.7-3.0 per bay). A 5,210 mm Mercedes GLS parks with 300 at the nose and 340 behind the tail to the closed gate; a Land Cruiser 300 leaves 565 behind. Head clearance = street 0 to the first-floor soffit at 4,500 (research min 2,400; 2,700 if a lift is ever added).

3. GATE. Delete the 4,500 gate at x 3800..8300 and cut a 5,000 clear opening at x 3650..8650 (villa_3d.py:284), dead on the carport centreline x = 6,150. Both bays are then entered and left in one straight movement: a 2.0 m car centred in bay 1 occupies 3775..5775 and in bay 2 occupies 6525..8525, both wholly inside the 3650..8650 jambs -- no lateral shift at all, so the reverse-curve arithmetic never applies. Cantilever slider running EAST, parked leaf x 8650..14150 (opening + 500 run-back per the research). No clash: the rill stops at y 28300, 350 short of the wall inner face where the track sits, and the pedestrian gate at x 15400 is clear.

4. DELETE the free-standing porch entirely -- villa_3d.py:110-111 (PORCH_*), :253-254 (beams), :255 (slab), :256 (blade wall), and the villa_sheets.py:76 and :88-90 porch box and "2 CARS" label. Replace the label with "COVERED CARPORT 2 CARS 5.5 x 5.85 m / 32.2 m2" placed at x 3400..8900, y 22800..28650.

5. FAMILY ENTRANCE (fixes the docstring's "family via the garage", which the model never built). 1,000 mm door in the notch's east cheek at x 8900..9300, y 22300..23300, into a 1,600 x 1,600 lobby at x 9300..10900, y 22000..23600 taken from the hall's NW corner, with 6R x 150 / 5G x 280 climbing the 900 mm to GF. Same climb the guest entrance already makes.

6. ROOMS AFTER (villa_sheets.py GROUND schedule):
   SHOW KITCHEN   x 3400..8900, y 18400..22400 = 5,500 x 4,000 = 22.0 m2 (was 26.1; research band 20-28) -- move the kitchen|hall partition from x 8425..8575 to the new 8900..9300 wall.
   ENTRANCE HALL  x 9300..15425, y 20550..23600 = 18.7 m2 less the 2.6 m2 lobby = 16.1 m2 (was 20.9; circulation, no band).
   GUEST WC       x 9300..11500, y 18400..20400 = 4.4 m2 (was 3.6) -- move its east wall from x 10400..10550 to 11500..11650 so it is not squeezed by the hall's new west wall.
   FORMAL DINING 22.5, WOMEN'S MAJLIS 26.1, FAMILY LIVING 28.6, STUDY 22.5 and ALL FOUR BEDROOMS are untouched -- the notch is ground-floor only.

7. AREA. Ground loses 6,300 x 1,200 = 7.6 m2. GFA 407 -> 399.4 m2 (4,299 sq ft). Recover it if wanted by deepening the roof pavilion PV from (9000, 19000, 15000, 24000) to (9000, 17700, 15000, 24000): 6.0 x 6.3 = 37.8 m2, +7.8, restoring GFA to 407.2. Note also that the 32.2 m2 carport is now genuinely covered by habitable floor, so if the authority counts covered parking the BUA rises rather than falls.

Net: two full-size SUV bays behind a closed gate, both entered in one straight movement, at a cost of 4.1 m2 off the kitchen and 4.8 m2 off a circulation space -- and the north elevation gains a 1.2 m deep, 6.3 m wide, 4.5 m tall shadow recess that rhymes with the 3.0 m cantilever on the pool front.

### Upheld 51

REAL, and I could not refute it -- I reproduced it three independent ways.

1. Source arithmetic. shell() (villa_3d.py:144-151) builds `ring = fp - offset(fp, -t)`, so every external wall occupies the OUTER 400 mm of the footprint rectangle. North-bar north wall = y 23600..24000; wing/living-volume south wall = y 12500..12900; east wall = x 20600..21000. Every opening void is cut at face +/-300, which spans only the outer 300 mm and leaves exactly 100 mm of inner leaf.

2. Solid probe of the built model (build123d boolean intersection against the real Part, not a re-derivation):
   guest entrance, y 23600-23700 across the 1500 mm door: 100.0% material; y 23700-24000: 0.0%. The 400 mm wall is 25% intact across the whole doorway.
   service door, x 20600-20700: 100.0% material.
   pool structural glazing, y 12800-12900 over the full 5.6 m: 100.0% material.
   west and east wing south windows, GF and FF, y 12800-12900: 100.0% material (all four).
   control - clerestory (line 245-247, cut xx-100..xx+600, spanning both faces): 0.0% material, i.e. correctly open.

3. Drawing evidence. Cutting VILLA_PLAN_GF.dxf at z = GF+1200 and zooming the entrance shows the outer line (y 24000) stepping back to y 23700 between x 11250 and 12750 while the inner line at y 23600 runs unbroken straight through. It is a 300 mm-deep niche, not a door. A-201 imports that same DXF (villa_sheets.py:67, import_geometry of VILLA_PLAN_GF), so the sheet inherits it rather than masking it.

The clincher that this is an oversight and not an intended reveal detail: line 240-241, the first-floor glazing, is the one opening written as `WG_Y0 + WALL + 300` -- the correct through-cut pattern exists exactly once in the file, and probes 0% material. Every other opening dropped the `+ WALL` term.

Severity is fairly stated as major. The scheme's whole argument is that plan, section and elevation are cut from one solid and therefore cannot disagree; here they agree on a house whose guest entrance, service entrance, 5.6 m pool glazing and all four wing windows are blind. It is also not cosmetic in the model: it changes the fabric volume by 5.1 m3 and is what a reviewer sees first in the S elevation.

One correction to the reviewer: the proposed literal replacement `(face - WALL - 100) to (face + 100)` is only right for the two faces whose interior lies on the minus side (NB_Y1, HX1). Applied to the south faces at WG_Y0 it would cut y 12000..12600 and leave 300 mm solid -- worse than now. The inward direction must be per face, as the reviewer's own cut_opening(..., inward=) suggestion implies.

**Corrected fix:**

Cut through the full 400 mm with a 100 mm over-run on BOTH faces, taking the inward direction per face (do not apply one formula to all four).

Helper, next to blk():

    def thru(face, inward, t=WALL, over=100.0):
        """(lo, hi) spanning a wall whose outer face is at `face` and whose
        interior lies in direction `inward` (+1 or -1), over-running both faces."""
        inner = face + inward * t
        return min(face, inner) - over, max(face, inner) + over

Per-line changes (mm):

1. Guest entrance, line 248-249 -- north face NB_Y1 = 24000, interior at -y, wall 23600..24000:
   V.append(blk(AXIS - 750, NB_Y1 - WALL - 100, GF, AXIS + 750, NB_Y1 + 100, GF + 2400))
   y 23700..24300 -> 23500..24100. Gives a 1500 x 2400 through-opening.

2. Service door, line 257-258 -- east face HX1 = 21000, interior at -x, wall 20600..21000:
   V.append(blk(HX1 - WALL - 100, NB_Y0 + 700, GF, HX1 + 100, NB_Y0 + 1800, GF + 2400))
   x 20700..21300 -> 20500..21100. 1100 x 2400 through-opening.

3. Pool structural glazing, line 238-239 -- south face WG_Y0 = 12500, interior at +y, wall 12500..12900. Only the inner limit is wrong:
   V.append(blk(LV_X0 + 200, WG_Y0 - CANT - 100, GF + 100, LV_X1 - 200, WG_Y0 + WALL + 100, GF + 3400))
   inner limit 12800 -> 13000 (= WG_Y0 + WALL + 100).

4. Wing south windows, ground, line 243:
   V.append(blk(x0, WG_Y0 - 100, GF + 450, x1, WG_Y0 + WALL + 100, GF + 3100))
   y 12200..12800 -> 12400..13000.

5. Wing south windows, first floor, line 244:
   V.append(blk(x0, WG_Y0 - 100, FF + 450, x1, WG_Y0 + WALL + 100, FF + 2700))
   same y range 12400..13000.

Leave line 240-241 (already `WG_Y0 + WALL + 300`) and the clerestory at 245-247 alone; both already cut clean through.

Verified on a patched copy of villa_3d.py, rebuilt and re-probed:
  - all seven openings now 0.0% material through the full 400 mm of wall;
  - jambs at x 11250 / 12750 and the head above z = GF+2400 still 100% solid, so nothing is over-cut;
  - model volume 835 -> 830 m3 (5.1 m3 of masonry that had never been removed);
  - GFA 407 m2, footprint 196 m2, coverage 28% and every room area unchanged -- this touches fabric only, not the schedule;
  - the re-cut GF plan now shows both wall faces broken with clean 400 mm reveals at the entrance, and A-201 picks it up automatically because it imports VILLA_PLAN_GF.dxf.

Worth doing at the same time: these are through-holes only -- no frame, threshold or door leaf -- so at the next level of detail the entrance still reads as a hole rather than a door in elevation.

### Upheld 52

REAL -- I could not refute the substance, though several of the reviewer's specific numbers and their proposed fix are wrong.

VERIFIED IN villa_3d.py:
- Lines 174-177: voids x 8000-9000 (WW_X1..LV_X0) and 15000-16000 (LV_X1..EW_X0), y 12200-18300 (WG_Y0-300 .. WG_Y1+300), z 400-10300 (GF-SLAB .. RF+SLAB+PARAPET). So 1,000 wide x 6,100 long x 9,900 tall. H/W = 9.9 to parapet top, 7.8 from ground-floor level (900) to roof soffit (8700). The project's OWN research file (VILLA_RESEARCH.md line 145) says a two-storey villa court wants 5-7 m width for H/W 1.1-1.6. The slots are off that target by a factor of 5-7.
- Roof (line 165) spans y 9500-24000; the cut starts at y 12200, so 2,700 mm of slab + parapet bridges the slot's south end. CONFIRMED.
- Openings audit (lines 237-258): the only voids in the wing zone are the LV south glazing (x 9200-14800, y 9200-12800), the FF south band (y 12200-12900), and the two wing south windows (x 4200-6800, 17200-19800, y 12200-12800). Nothing faces x 8000/9000/15000/16000 over y 12500-18000. At ground floor the slots are bounded by four blind 400 mm walls for 3.6 m. CONFIRMED -- they light no room.
- VILLA_VIEW_AERIAL_SW.png shows exactly the reviewer's read: two rectangles punched in a continuous roof plate, stopping short of the front edge. VILLA_ELEV_S.png shows the parapet band running unbroken across all 18 m -- the slots do not cut the silhouette, so the docstring's "slots between the wings and the central volume" is not delivered in the primary elevation.
- Cost the reviewer did not name: the four slot flanks add 172 m2 of external wall (4 x 5.5 x 7.8 m), east/west facing, in a hot-dry climate, serving nothing.

TWO CONSEQUENTIAL DEFECTS THE REVIEWER MISSED:
- The cut leaves two unguarded 1.0 x 6.1 m holes in an occupied roof deck (there is a roof pavilion and a 1,100 parapet) with no upstand, no guarding, no waterproofing return.
- At the slot base the ground slab is absent over y 15400-18000, so 2.6 m2 per slot of the semi-basement interior is open straight to the sky down a 13.1 m shaft -- no slab, no edge beam, no drainage.

WHERE THE REVIEWER IS WRONG (matters for the fix, not the verdict):
1. "never open to sky along its length" -- false. The full 6,100 mm of the cut IS open to sky; what bridges is the roof's 3.0 m south overhang, leaving 2,700 mm of plate across the south END. The conclusion (punched holes, not splits) stands; the statement does not.
2. "12.2 m2 a floor" -- the recoverable enclosed area is 11.0 m2/floor (2 x 1.0 x 5.5). The 6.1 m figure includes 2 x 300 mm of overshoot outside any footprint.
3. "Zero openings in any of the four walls facing each slot" -- true at ground, FALSE at first floor, and the truth is worse. FF_FOOT (line 140-142) has no rectangle over x 9000-15000, y 12900-18000, so from z 4500 to 8700 the living volume's east and west flanks ARE NOT MODELLED AT ALL. The double-height family living room is currently open to weather on both sides, 5.5 x 4.2 m each, straight into the slots and out to the sky. The slots therefore do connect to a room -- by omission, not by design.
4. The proposed x-ranges are asymmetric on a parti whose whole subject is a symmetric comb about a central water axis: centres at 8700 and 16300, i.e. -3,300 and +4,300 from AXIS 12000. Both also cut into the 6.0 m living volume -- 7800-9600 removes its entire west wall plus 200 of interior; 15400-17200 leaves its east wall standing free as a 400 mm fin.
5. Widening to 1,800 costs a further 17.6 m2 over two floors, taking GFA from 407 to ~389 m2 against a 418 m2 brief it is already 11 m2 short of. The reviewer proposes making the area problem worse while criticising wasted area. And 1:5.7 is still a shaft, with two full-height glass walls 1.8 m apart facing each other -- formal dining looking into family living at 1.8 m.
6. "the roof's front edge (y 9000/11000)" -- the roof edge is y 9500.

**Corrected fix:**

Do not widen. Fill the slots at ground floor, keep them at first floor and roof, and glaze them. This recovers area instead of spending it, drops H/W from 9.9 to 3.7, and fixes the aerial.

GROUND FLOOR (z 900-4500) -- delete the void below the first-floor slab:
- Raise the slot voids' base from GF-SLAB (400) to FF (5000).
- GF_FOOT wings become (3000, 12500, 9000, 18000) and (15000, 12500, 21000, 18000); keep the LV rectangle, so the merged footprint is one 18.0 x 5.5 m band and the offset gives a single ring at 3000/21000/12500/18000.
- Reinstate the living volume's flanks as explicit 400 mm RC walls (they carry the 6 m roof span and flank a 7.30 m void): add to PARTS_GF (9000, 12900, 9400, 18400) and (14600, 12900, 15000, 18400), full ground height, each with a 1,200 x 2,700 opening if dining/study are to connect to the living volume.
- Result: formal dining 3400-9000 x 12900-18250 = 5.60 x 5.35 = 29.9 m2, study the same (both are 22.5 m2 now; research target for a formal dining is 28-35). Ground 196 -> 207 m2; GFA 407 -> 418 m2 = 4,500 sq ft, exactly the brief. Coverage 207/696 = 29.7%, still inside 27-32%.
- The two 2.6 m2 holes into the semi-basement close automatically; the ground slab becomes continuous over the basement except the intended 5.0 x 4.0 sunken court.

FIRST FLOOR + ROOF (z 5000-10300) -- keep the slots on the same grid lines, x 8000-9000 and 15000-16000 (symmetric at +/-3,500 from AXIS 12000), y 12500-18000:
- Height to roof soffit is now 3,700 mm -> H/W 3.7, a slot that works instead of a maintenance shaft. Every extra 100 mm of width comes out of a wing bedroom or out of a living volume already 6.0 m wide against 7.30 m clear height -- do not take it.
- Glaze the wing flanks: voids (7600, 12900, 8000, 18000) and (16000, 12900, 16400, 18000) at z 5300-8300 -- 5.1 x 3.0 m each, making guest 1 and guest 2 dual-aspect (they have one south window each today). East/west orientation is self-shaded by the 1 m slot.
- Close the living volume's flanks, currently missing: build x 9000-9400 and 14600-15000, y 12900-18000, z 4500-8700 as full-height structural glazing in a 400 mm reveal. This both encloses a room that is presently open to weather and makes each slot the light source for the top of the double-height volume -- the only version of AGi's "patios developed three-dimensionally" this plan can actually deliver.
- Extend the roof cut only, x 8000-9000 and 15000-16000, y 9500-18000, z 8700-10300, so the 2,700 mm bridge disappears and the plate reads as three plates over three masses.
- Return the 250 mm parapet around all three exposed sides of each roof opening at 1,100 mm high -- the roof is occupied (pavilion + stair head).
- Floor each slot on the first-floor slab in white pebble per F.LOT, tanked warm-roof build-up, fall 1:80 to a 100 mm outlet.
- Stop the slot void at y 18000, not 18300: at present it oversails 300 mm of the north bar's 400 mm south wall, leaving a 100 mm wall stub at each slot head on both floors.

FALLBACK if the client wants no slot at all: delete both entirely (WW_X1 = 9000, EW_X0 = 15000, wings and LV merged on both floors), recovering 22.0 m2 over two storeys and 172 m2 of blind envelope -- but then the upper mass must be articulated some other way, because the south elevation becomes an unbroken 18 m block.

### Upheld 53

I tried to refute this and could not. Every number reproduces from villa_3d.py.

VERIFIED FACTS
1. POOL_Y1 = 12500.0 (line 95) is identical to WG_Y0 = 12500.0 (line 86), the villa's south face. Delta = 0. The pool's north water edge IS the building line.
2. Pool shell = blk(POOL_X0-400, POOL_Y0-400, ..., POOL_X1+400, POOL_Y1+400, POOL_TW), i.e. x 9100..14900, y 2600..12900, z -1100..700. The 400 mm coping band y 12500..12900 sits inside the building footprint, under the south wall of the living volume (x 9000..15000). The ground slab is z 400..900 over that same footprint, so the coping and the slab overlap z 400..700 -- a real 300 mm solid-on-solid clash, not a rounding artefact.
3. FFL = GF = 900; POOL_TW = 700; POOL_FL = -700. Step down 200 mm, then 1400 mm of water.
4. The structural-glazing void (lines 238-239) is x 9200..14800 = 5600 mm wide, z 1000..4300. It removes the entire south wall of the family living room across 5.6 m. Beyond that plane there is water, no deck, no threshold, no guard.
5. Surrounds, shell face to boundary-wall inner face (BW = 350): west 8750, east 8750, south 2250. The catch-basin void is y 1600..2600 (1000 wide) with invert -900, leaving 1250 mm between wall face and trench, and the trench is modelled uncovered.
6. Rear zone inside the wall is 12150 mm; the shell takes 10300 mm of it. Nothing paved is modelled anywhere on the site -- the only ground-level solids are the boundary walls, the pool shell, the front rill band and the porch.
7. Research is explicit and is being violated: VILLA_RESEARCH.md:307-308 "Pool surround: 1.2 m min on back sides, 1.5 m where people walk, 3.5-4.5 m on the lounging side." Line 304-305 also budgets a lounge terrace 3.5-4.5 m and dining 4.5-5.0 x 5.0-6.0; line 274 allocates "pool+deck 100-120" m2 of open ground. Provided: 0.

I also checked the two readings that might have rescued it, and neither does. (a) "It is fixed glazing, so water-to-glass is deliberate, like the Myrtles." Even granting that, the Court of the Myrtles pool is a shallow basin with a paved margin, and research line 148 puts an axial reflecting pool at 50-150 mm deep -- this is 1400 mm. And the design still fails, because then the ground floor has no door to the garden at all: the only other south openings (x 4200..6800 and 17200..19800) have 450 mm sills, and the remaining entrances are north (guest) and east (service). (b) "Paving just is not modelled in a massing model." That does not help either, because the pool shell physically occupies the rear zone right up to the building line -- there is no room a terrace could occupy, which is the actual defect.

Two further consequences the reviewer did not mention, both confirming the pool block was never reconciled: the module docstring (line 32) claims "the swimming pool proper at 12.0 x 4.0 m", but the code builds 5.0 x 9.5 -- 9.5 m is below the 12 m lap threshold at VILLA_RESEARCH.md:188 and 5.0 m is outside the 3.5-4.5 m width band. And the spill/basin void (lines 269-270) at y 1600..2600 does not intersect the shell at y 2600..12900 at all, and there is no terrain solid for it to cut, so the "overflow edge + catch basin" the sheet annotates is a modelling no-op.

The reviewer's diagnosis is right, but their proposed fix has two defects of its own, corrected below: their pool at x 5150..18150 centres on 11650, 350 mm off the AXIS = 12000 that the rill is supposed to meet at right angles; and their 134 m2 terrace plus 52 m2 pool = 186 m2 of hard landscape blows the research's 100-120 m2 pool+deck allowance and leaves roughly 82 m2 of garden against the 150-200 m2 the research wants. They also leave the levels untouched, which reproduces a 200 mm single step along the pool edge -- forbidden outright at VILLA_RESEARCH.md:369, "Never a single step in an open terrace" -- and leave the basin as an open trench.

**Corrected fix:**

Rotate the pool through 90 degrees, centre it on the axis, and insert a raised terrace. The rear zone is 12,150 mm inside the boundary wall (y 350 to the villa's south face at 12500) and the corrected stack fills it exactly:

  terrace 4,800 + coping 400 + water 4,000 + coping 400 + garden 2,550 = 12,150

POOL (villa_3d.py lines 94-98)
  POOL_X0, POOL_X1 = 6000.0, 18000.0   # 12.0 m lap, centred on AXIS = 12000
  POOL_Y0, POOL_Y1 = 3300.0, 7300.0    # 4.0 m wide
  POOL_TW = 880.0                      # deck-level, flush with the terrace
  POOL_FL = -520.0                     # 1.4 m constant depth
  BASIN_D = 300.0                      # covered basin, grate flush with garden
  Shell (400 coping ring): x 5600..18400, y 2900..7700, z -820..880.
  Pool 12.0 x 4.0 = 48.0 m2 = 6.9% of plot -- exactly the research target at
  VILLA_RESEARCH.md:187-190, and it finally makes the code agree with its own
  docstring line 32. Centre x = 12000, dead on AXIS, so the rill meets it square.

SURROUNDS (all measured shell face to boundary-wall inner face)
  west 5,250 | east 5,250 (symmetric; research 3.5-4.5 m lounging side)
  south/rear 2,550 (research 1.2 m min back, 1.5 m walk; also clears the 45 deg
    load-spread zone, which wants 0.9-1.5 m, and the 1.5 m zoning setback)
  north = the terrace, 4,800

TERRACE (new)
  TER_X0, TER_X1 = 4600.0, 19400.0
  TER_Y0, TER_Y1 = 7700.0, 12500.0     # abuts pool coping and villa south face
  TER_FL = 880.0
  14.8 x 4.8 = 71.0 m2. Takes the research's lounge (3.5-4.5 m deep) and dining
  (4.5-5.0 deep x 5.0-6.0 wide) side by side. Pool + deck = 119 m2, inside the
  100-120 m2 allocation at VILLA_RESEARCH.md:274; main garden lands at ~170 m2,
  inside the 150-200 m2 band.

LEVELS -- this is what removes the fall hazard
  FFL 900 | terrace 880 | top water 880 | invert -520 | garden 0.
  The 5.6 m opening becomes a sliding door with a 20 mm threshold drop over a
  200 x 100 recessed grated channel across the full width, membrane returning to
  150 mm each side (VILLA_RESEARCH.md:377-379). You step out onto 4.8 m of level
  terrace, not into water. Lower the glazing void sill from GF+100 to GF so the
  opening reaches the floor.
  The pool is deck-level on its north long side: water flush with the terrace,
  20 mm slot into a 100 x 100 gutter, which also drains the terrace. That is the
  detail at VILLA_RESEARCH.md:193-196 and it is what makes the water read as a
  mirror from the living room.
  The south long side is the waterwall: 880 mm free fall to the garden -- inside
  the 600-900 mm raised-pool band at VILLA_RESEARCH.md:21-23 and 370-373 -- into a
  900 mm wide basin at y 2000..2900, invert -300, closed with a walk-on grate
  flush with the garden. No open trench. Garden from basin to wall face 1,650 mm.
  Terrace to garden: two flights at the terrace ends, 1,200 mm wide, 7 risers at
  126 mm, 350 going, 2R+G = 601 -- inside the 100-150 / 300-400 / 550-700 bands and
  never a single step (VILLA_RESEARCH.md:368-369).

AXIS
  Extend the rill: 500 mm wide on x 11750..12250, running the 4,800 mm south from
  the living-room threshold across the terrace to meet the pool's north coping at
  right angles. Channel 150 mm deep, water at 880 over a dark screed (research
  line 148: 50-150 mm, 75 standard). Gate to rill to hall to double-height volume
  to rill to pool now reads as one uninterrupted line.

CONSEQUENTIAL EDITS
  - The 300 mm shell-into-slab clash disappears: shell max y = 7700 is clear of
    the slab, which starts at y = 12500.
  - The 3.0 m cantilever now shades the terrace (y 9500..12500, 3.0 m of the
    4.8 m depth) instead of the water. In the Gulf that is the better outcome --
    update the docstring line 37, which still says "shading the water's edge".
  - Rebuild the spill: the current basin void (lines 269-270) never touched the
    shell, so model the weir as an actual notch in the shell's south rail.
  - Trim the two light-slot voids (lines 174-177) to start at y = WG_Y0 rather
    than WG_Y0 - 300, or they will nick a 1.0 x 0.3 m notch out of the terrace
    slab at each slot.
  - villa_sheets.py picks the pool up from v3.POOL_*, so the plan follows, but
    add the terrace, the steps, the rill extension and the basin grate to the
    site linework at lines 69-85.

### Upheld 54

Real, and understated. I could not refute any of it; checking the geometry made it worse.

VERIFIED BY MEASUREMENT (villa_3d.py, and by intersecting probe boxes with the built solid):

1. The void ratios are right. North face x3000-21000 by street-to-parapet 0-10300 = 18.0 x 10.3 = 185.4 m2, and the only cut anywhere in it is the 1.5 x 2.4 guest door at line 248 -> 3.6 m2 = 1.9%. West 11.5 x 10.3 = 118.5 m2 with one 4.4 x 0.65 clerestory (line 245-247) = 2.4%. East 4.7%. South 23.8%. All four figures reproduce exactly.

2. Kitchen and majlis have zero external openings, as claimed. Show kitchen = north-bar interior x3400-8425, y18400-23600 = 26.1 m2; women's majlis = x15575-20600, y18400-23600 = 26.1 m2. Enumerating every V.append in the openings block: the two clerestory slots are at z 7800-8450, i.e. FIRST floor, so they light bedroom 3 and the master, not the kitchen and majlis below. Neither ground room is touched by any cut. The majlis's only daylight is borrowed through a 1.2 m door from the hall, and the hall's own only light is the 1.5 m front door.

3. WORSE THAN THE REVIEWER KNEW: none of the openings they credit actually exist. Walls are WALL=400 thick, but every external cut uses the pattern blk(..., FACE-300, ..., FACE+300, ...) -- 300 mm of penetration into a 400 mm wall. I probed the inner 100 mm of each: front door, the 5.6 x 3.3 structural glazing to the garden, both wing windows at ground, both at first floor, and the service door all come back 100.0% SOLID (controls behave correctly: the two clerestory slots read 0.0% solid, a blank wall reads 100.0%). Every one is a 300 mm blind niche with a 100 mm skin of concrete behind it. The author knew the correct pattern -- line 240-241 is the single cut that adds WALL to its depth -- and applied it to exactly one of eight openings. So the true figures are: north 0% void, east 0%, south 0%, west 2.4% (the two clerestory slots, 5.72 m2, are the entire glazed area of the villa). The reviewer's "bunker with a glass face" is generous; as modelled it is a bunker.

4. The reviewer's proposed fix does not survive contact with the plan. Their majlis court at x15600-20600 collides with the existing 1.2 m pedestrian gate at x15400-16600 (line 285) -- the arrival route would run through the women's majlis's private court. Their kitchen court "4.0 x 2.5 at x 0-3000" is self-inconsistent (x0-3000 is 3.0 m, and BW=350 leaves 2.65 m clear, not 2.5 or 4.0), and a punched west window is the worst orientation in the Gulf -- VILLA_RESEARCH.md section 2 says east/west cannot be shaded by horizontals. Their claimed outcome (north ~9%, west ~10%) also over-reads: the correct arithmetic is 7.8% and 10.9%.

Not a matter of taste: a blank street wall is a legitimate parti here (Wall House, Interlude House, both in the research), but those pair blankness with internal courts, and this villa's only voids are two 1.0 m slots that stop short of the north bar entirely. A 26 m2 principal reception room with no daylight and no openable area fails the habitable-room light/ventilation minimum in essentially every code (typically glazed >= 1/10 of floor area, openable >= 1/20), and the research doc's own stack-ventilation rule (inlet >= 1/10 of floor area). Severity: I would call it high rather than fatal -- the parti, GFA, coverage and setting-out grid all survive the fix untouched -- but the factual claims are all correct.

**Corrected fix:**

Three parts. Part A is a bug fix and must come first, or nothing else is visible.

A. MAKE THE EXISTING OPENINGS PENETRATE (8 lines in villa_3d.py). Each cut must span the full 400 mm wall, not 300. Key it to WALL so it cannot drift again:
  line 238-239 -> V.append(blk(LV_X0+200, WG_Y0-CANT-300, GF+100, LV_X1-200, WG_Y0+WALL+100, GF+3400))
  line 243     -> V.append(blk(x0, WG_Y0-300, GF+450, x1, WG_Y0+WALL+100, GF+3100))
  line 244     -> V.append(blk(x0, WG_Y0-300, FF+450, x1, WG_Y0+WALL+100, FF+2700))
  line 248-249 -> V.append(blk(AXIS-750, NB_Y1-WALL-100, GF, AXIS+750, NB_Y1+300, GF+2400))
  line 257-258 -> (delete; replaced in C)
This alone restores south to 44.0/185.4 = 23.8% and makes the front door a door.

B. MAJLIS: north court in the front setback -- the reviewer's location, three corrections.
 B1. Move the pedestrian gate onto the water axis first, or the court is unbuildable: line 285 becomes V.append(blk(11400, PLOT_D-BW-200, STREET, 12600, PLOT_D+200, 2200)). This clears x15600+ for the court and fixes a second defect free of charge -- the scheme's stated Casa Merida move is an uninterrupted line from the entrance door to the pool, but the gate at x16000 is 4.0 m off the rill and front door at AXIS=12000. Pull the rill head back to y27800 (PLOT_D-1200) so the gate opens onto a 500 mm stone threshold, not into water.
 B2. Court x15600-21000 (5.4 m, butting the house's NE corner), y24000-27000 (3.0 m, not 2.5) = 16.2 m2, entirely in the 5.0 m front setback, zero GFA. Depth 3.0 not 2.5 because privacy must not depend on the boundary wall: build the court's own screen as a freestanding 350 mm stone wall at 2,700 high on line y27000, leaving a 1,300 mm planted strip to the boundary wall's inner face at y28650. A freestanding garden wall set back 1.3 m is not a boundary wall, so it escapes the 1.8-2.0 m Gulf front-wall cap that VILLA_RESEARCH.md section 4 records -- the reviewer's fix leans on a 2.4 m front wall that may not be permitted, over the most privacy-sensitive room in the house.
   S.append(blk(15600, 27000, STREET, 21000, 27350, 2700))   # screen, north
   S.append(blk(15600, 24000, STREET, 15950, 27350, 2700))   # screen, west
   S.append(blk(21000, 24000, STREET, 21350, 27350, 2700))   # screen, east, with a 900 mm maintenance door
 B3. Glazing 4,000 x 2,700 full-height in the majlis north wall, centred on the room (clear span 15575-20600, centre 18088):
   V.append(blk(16100, NB_Y1-WALL-100, GF, 20100, NB_Y1+300, GF+2700))
   = 10.8 m2, 41% glazing-to-floor on a north face behind a 2.7 m screen at 3.0 m: no direct summer gain, pure sky light. Structure: 400 x 500 RC beam over, soffit at GF+2700 so it reads as the head reveal, not a downstand. Court finish: 5.4 x 3.0 cannot take a tree (research minimum 4 x 4 with 1.0-1.2 m soil), so a 3.0 x 1.2 m still water table at 75 mm on a black slab against the screen wall, plus one multi-stem in a 1.2 m raised bed on the west wall.

C. KITCHEN: west service court, full length, and give the existing fins a job.
 C1. Court x350-3000 clear (2.65 m -- the boundary wall takes 350 of the 3.0 m setback), y18400-23600 (5.2 m) = 13.8 m2: bins, condenser bank, gas, drying, louvred gate at its north end.
 C2. Not a punched window. A 3,000 x 2,400 opening with a 900 mm sill (worktop height, so the elevation reads as a band):
   V.append(blk(HX0-300, 19800, GF+900, HX0+WALL+100, 22800, GF+3300))
   = 7.2 m2, 28% glazing-to-floor; specify two operable leaves to clear the 1/20 openable minimum.
 C3. Extend the brise-soleil over it -- line 261-263, range(9) -> range(18), carrying the fins from y12800 to y23180. Today those nine fins stand in front of a completely blank wall shading nothing (visible in VILLA_ELEV_W.png); extended, they shade the new west window and the west clerestory, which is what section 2 of the research demands for a west face.
 C4. Service entrance relocated to where it belongs, and made to penetrate:
   V.append(blk(HX0-300, 18700, GF, HX0+WALL+100, 19900, GF+2400))   # 1.2 m door, kitchen west wall
   V.append(blk(-200, 20200, STREET, 550, 21300, 2100))              # 1.1 m gate, west boundary wall
   The existing service door is not only blind, it is at y18700-19800 on the east wall -- inside the women's majlis. The docstring claims it reaches the kitchen without crossing guest space; as modelled it delivers staff into the majlis, at the opposite end of the building from the kitchen.

RESULT: north 14.4/185.4 = 7.8% void with a 3.0 m deep shadow across the majlis bay; west 12.9/118.5 = 10.9% behind a fin screen; south 23.8%; east stays a 2.4% stone plane, which is now honest -- it faces a neighbour across 3.0 m and holds the master suite. GFA, 28% coverage and the setting-out grid are untouched; both courts are in setback land.

TWO THINGS THIS FIX DOES NOT SOLVE, flagged rather than papered over: (i) with the kitchen west and the majlis east, the coffee run still crosses the entrance hall, which VILLA_RESEARCH.md section 5 calls the one thing a Gulf plan must avoid -- the real answer is a 900 mm servery along the north wall into the majlis's west partition, at the cost of 900 mm off the depth of a north bar that is only 5.2 m clear; (ii) the 2,700 mm screen walls sit in the front setback and some authorities treat anything over 2.4 m as a structure -- verify, consistent with the research doc's own caveat that its setback and wall-height figures are expected ranges, not a code citation.

### Upheld 55

CONFIRMED -- I could not refute it. Checked against the geometry, not the prose.

1. The service void is at villa_3d.py:257-258: blk(HX1-300, NB_Y0+700, GF, HX1+300, NB_Y0+1800, GF+2400) with HX1=21000, NB_Y0=18000 -> x 20700-21300, y 18700-19800, z 900-3300. The north-bar east wall band is x 20600-21000 (footprint 3000-21000 inset by WALL=400), so this is a door in the east wall at y 18700-19800.
2. That y range is inside the north bar (NB_Y0=18000; interior 18400-23600), north of the majlis|study partition at y 18250-18400 (line 193). The north bar's east room is x 15575-20600 x y 18400-23600 = 26.13 m2, which villa_sheets.py:31 labels WOMEN'S MAJLIS (and the room area printed, 26.1 m2, matches exactly). So the service door does open directly into the women's majlis, with no lobby, corridor or partition between - the east room has only two other doors, to the hall (line 197) and to the study (line 200).
3. Kitchen is at the far west: x 3400-8425 (villa_sheets.py:28). 20600 - 8425 = 12,175 mm. Confirmed.
4. No dirty kitchen and no pantry exist. The GROUND schedule has seven rooms, none of them service. The semi-basement is a single undivided 142 m2 void (lines 128-132) with zero partitions - and, separately, no stair reaches it at all (the only stair, lines 232-235, runs GF->FF), so the basement the docstring relies on is currently unreachable.
5. The design contradicts its own sourced brief. Docstring lines 46-48 claim "service on the east boundary reaching the dirty kitchen without crossing guest or family space". VILLA_RESEARCH.md:348-354 is explicit: "service (separate side-boundary door to dirty kitchen and laundry without crossing guest or family space)... The service route must reach the majlis for coffee without crossing family living - on a small plot that means a short service corridor behind the show kitchen with a discreet door into the majlis", and line 323 requires "dirty/wet kitchen w/ own external door 12-18; pantry 4-6". The model delivers the inverse of all three.

This is not taste. In a villa whose brief is women's majlis only, the tradesman's door opening into the one room where women receive guests unveiled is a programme failure, and it is measurable from the source.

Two corrections to the reviewer, which change the remedy:
- Their proposed fix (mirror the north bar) is wrong-handed. The vehicle gate (x 3800-8300, 4.5 m) and car porch (x 3500-10500) are WEST; the 1.2 m pedestrian guest gate (line 285, x 15400-16600) is EAST. Mirroring puts the women's majlis behind the driveway and the kitchen at the guests' gate. It also breaks the one adjacency the plan gets right - kitchen over formal dining, linked by the door at x 5000-6200 in the y 18250-18400 wall (line 199) - since the moved kitchen would open into the STUDY instead; and it slides kitchen extract under the master suite (villa_sheets.py:39-41) rather than under Bedroom 3. Their own fix is also self-defeating: with the majlis moved west, a "service corridor along the east boundary to a discreet leaf into the majlis" would have to cross the full 6.85 m hall. The east/west zoning is right; the service door is on the wrong side of the house.
- Secondary bug found while checking: both entrance voids under-cut their wall. The service void spans x 20700-21300 against a 20600-21000 wall, leaving a 100 mm leaf standing across the opening; the guest entrance (line 248, y 23700-24300 against a 23600-24000 wall) does the same. As modelled these are 300 mm blind niches, not doors.

**Corrected fix:**

Keep the east/west zoning (it matches the gates). Move the service, and build the service rooms the docstring already promises.

1. SERVICE DOOR -> KITCHEN'S WEST WALL (villa_3d.py:257-258)
   delete: V.append(blk(HX1-300, NB_Y0+700, GF, HX1+300, NB_Y0+1800, GF+2400))
   add:    V.append(blk(HX0-500, 22400, GF, HX0+500, 23400, GF+2400))
   -> x 2500-3500, cutting the full 400 mm west wall (3000-3400); 1000 mm clear leaf, head 2400, into the NW corner of the show kitchen, 200 mm clear of the north wall for the frame.
   Also fix the guest door: line 248, change NB_Y1-300 to NB_Y1-500 so it cuts the whole 23600-24000 wall.

2. SERVICE GATE + WEST ALLEY (new, boundary block)
   V.append(blk(-200, 25400, STREET, 550, 26600, 2100))
   -> 1.2 m gate through the west boundary wall (x 0-350) at y 25400-26600, in the front setback. Delivery run: gate -> 2.65 m west alley (boundary inner face x 350 to building face x 3000) -> south 2.0 m -> service door. It never enters the car court, never crosses the rill/axis (x 11750-12250), never passes the majlis or the pedestrian gate. It also clears the brise-soleil fins, which sit at x 2300-2750 only between y 12800-17780.

3. DIRTY KITCHEN 15.1 m2 IN THE SEMI-BASEMENT, under the show kitchen
   The ground floor has no spare area for it: west room 26.1 + west wing 22.5 = 48.6 m2 against a research requirement of 36-52 m2 for the kitchen suite alone, so a same-level dirty kitchen would cost the formal dining. Put it where design basis 2 already says service goes - the 142 m2 basement is completely empty.
   DIRTY KITCHEN  x 3400-7600, y 20000-23600 = 4200 x 3600 = 15.12 m2 (research band 12-18)
   plus laundry / dry store / staff room + WC / plant across the remaining basement.

4. SERVICE STAIR - the basement currently has none
   Straight flight, 1000 mm wide, against the west basement wall: x 3400-4400, y 15400-20000. Rise GF (+900) to basement floor (-2800) = 3700 mm; 20 risers @ 185, 19 goings @ 240 = 4560 mm run. Its head opens in the kitchen's SW corner - slab opening x 3400-4400 x y 18400-20000 = 1.6 m2 only, since the rest of the flight sits under the dining. Show kitchen 26.1 -> 24.5 m2, still inside the research band 20-28.

5. COFFEE TO THE MAJLIS WITHOUT CROSSING THE AXIS
   900 x 900 dumbwaiter shaft x 15675-16575, y 22700-23600, from the basement dirty kitchen up into a serving niche at the majlis NW corner. Majlis 26.1 -> 25.3 m2, still inside the women's-majlis band 25-35. Feed it with a 1200 mm basement service corridor along y 22400-23600 running east from the dirty kitchen. Tray traffic - the repeated crossing the research objects to - then runs vertically and back-of-house instead of across the entrance hall at x 12000.

6. MAJLIS OWN ENTRY (why the majlis belongs east)
   V.append(blk(18100, 23500, GF, 19100, 24200, GF+2400))
   -> 1000 mm discreet leaf in the majlis north wall (y 23600-24000), 6.1 m off the axis. Women guests arrive at the existing east pedestrian gate (x 15400-16600) and enter the majlis without entering the house. This is the Gulf convention and it is the argument against mirroring the bar.

Net effect: service door 0 m from the show kitchen instead of 12.175 m; dirty kitchen 15.1 m2 instead of 0; nothing from the service route enters the majlis, the hall or the entrance axis; the kitchen-over-dining and majlis-over-study stacking is untouched.

### Upheld 56

CONFIRMED, with two of the reviewer's numbers wrong and one wrong premise -- but the defect itself stands and is decisive.

WHAT I VERIFIED IN THE SOURCE (villa_3d.py)
- Line 140-142: FF_FOOT's fourth rectangle is (LV_X0, WG_Y0-CANT, LV_X1, WG_Y0+WALL) = (9000, 9500, 15000, 12900), and it goes through shell() with every other first-floor rectangle. shell() does ring = fp - offset(fp, -400), and because the four rectangles are geometrically disjoint the offset is applied face-by-face: the cantilever gets its own closed 400 mm wall ring on all four sides, floor at 5.000 (first slab, z 4500-5000) and ceiling at 8.700 (roof slab underside). That is a 3.70 m high enclosed room, not a slab.
- Disjointness is exact. Cantilever x 9000-15000; west wing x 3000-8000; east wing x 16000-21000; north bar y 18000-24000; and fp_ff contains nothing at x 9000-15000, y 12900-18000 (that is the double-height void). Clear gaps: 1.0 m west, 1.0 m east, 5.1 m north. Zero circulation connections. The stair (lines 232-235) is at x 13000-14600, y 18700-21420 -- in the north bar, nowhere near it.

WHAT THE DERIVED DRAWINGS SHOW (I parsed them, not the PNGs alone)
- VILLA_PLAN_FF.dxf, segments in the south zone: outer loop 9000/15000 x 9500/12900, inner 9400/14600 x 9900/12200, with 200 mm return nibs at x 9200 and 14800. Independent closed figure; no segment links it to anything.
- VILLA_SECTION_AA.dxf on the axis: soffit 9500->12500 at z 4500; the south face runs SOLID from 4500 to 10300; box floor 5000, ceiling 8700; the only opening in the box is in its NORTH wall (z 5300-7900), i.e. it faces the interior void, not the pool. The box therefore has a blank 4.2 m wall (4500-8700) facing the water.
- A-202 renders it as an unlabelled walled box sitting on the pool; villa_sheets.py FIRST lists seven rooms and does not include it, so it carries no name and no area on the sheet.
- VILLA_VIEW_POOL_EYE.png: the centre bay -- the double-height family living volume, the whole point of the scheme -- reads as a blank panel from the head of the ground glazing to the roof, while the two wings show stacked windows.

CONSEQUENCES THE REVIEWER GOT RIGHT
1. 18.0 m2 of unreachable space is booked as GFA: line 293 ct = area(LV_X0, WG_Y0-CANT, LV_X1, WG_Y0) feeds ff = nb+ww+ew+ct (line 295). The published first floor 181.0 m2 and GFA 407 m2 / 4,381 sq ft are overstated by 18 m2 (4.4%).
2. The double-height glazing is defeated. The ground opening (lines 238-239) runs z 1000-4300 only; the upper opening (lines 240-241, z 5300-7900) is cut in the box's north wall, so the tall room's upper light opens into a sealed, unlit 13.5 m2 void. Glass to the pool stops at 4.3 m in a room described as 7.30 m clear.
3. The shading move is redundant at that scale anyway: VILLA_PLAN_ROOF.dxf shows the roof plate and parapet running the full 18 m width at y 9500 (3000,9500 -> 21000,9500), so a continuous 3.0 m overhang already exists at 8.700. The box adds nothing the roof does not, and costs the view.

WHERE THE REVIEWER IS WRONG (does not save the design)
- "Floating, disconnected" overstates the solid geometry. The box's north wall (y 12500-12900) stands directly on the ground-floor south wall of the living volume below (z 900-4500), and its top is monolithic with the roof plate, which runs continuously back to the north bar. It is a properly supported cantilever; what it lacks is ACCESS, not support. That distinction matters for the fix -- the box walls are currently propping the south edge of the roof plate, so deleting them has a structural consequence the proposed fix does not mention.
- "Soffit 4.1 m above pool water" is wrong: soffit 4.500, top water POOL_TW 700, so 3.80 m.
- "12.5 m void to the north" is wrong: 12500 is the coordinate WG_Y0, not a distance. The void is y 12900 to 18000 = 5.1 m.
- The proposed fix's own z range is wrong: "extrude at FF..FF+SLAB" = 5000-5500 would float the slab 500 mm above the first-floor level. In this model the floor plate occupies GF+GF_CH..FF = 4500..5000.

VERDICT: an enclosed 13.5 m2 room, 3.70 m high, with four walls, a floor, a roof and no door, counted as GFA and drawn unlabelled over the pool, is not a matter of taste. It is the defect the reviewer says it is.

**Corrected fix:**

CORRECTED FIX -- cantilever becomes a slab, not a room. All in villa_3d.py unless noted.

1. Line 140-142 -- drop the fourth rectangle:
   FF_FOOT = ((HX0, NB_Y0, HX1, NB_Y1), (WW_X0, WG_Y0, WW_X1, WG_Y1),
              (EW_X0, WG_Y0, EW_X1, WG_Y1))

2. After line 160 (first slab) -- add the cantilever as bare slab at the CORRECT level, GF+GF_CH..FF = 4500..5000, not FF..FF+SLAB:
   # 3.0 m shading cantilever over the pool: SLAB ONLY, no enclosure.
   S.append(blk(LV_X0, WG_Y0 - CANT, GF + GF_CH, LV_X1, WG_Y0 + WALL, FF))
   # 15 x 15 drip groove, 40 mm back from the free edge
   V.append(blk(LV_X0, WG_Y0 - CANT + 40, GF + GF_CH,
                LV_X1, WG_Y0 - CANT + 55, GF + GF_CH + 15))
   Slab 6000 x 3400 on plan, 3000 mm clear projection south of the wall face at y 12500, 500 mm root (taper to 250 at the tip on the detail; keep 500 in the model). Root moment ~50 kNm/m (11 kN/m2 x 3.0^2 / 2), taken by the 400 mm wall below at y 12500-12900 x 9000-15000, which is tied at both ends into the two 400 mm flank cross-walls at x 9000-9400 and 14600-15000, y 12500-18000 -- a U-shaped fixed root, ample for a 3.0 m cantilever.

3. Line 238-239 -- take the glazing head up to the soffit (was GF+3400 = 4300):
   V.append(blk(LV_X0 + 200, WG_Y0 - CANT - 300, GF + 100,
                LV_X1 - 200, WG_Y0 + 300, GF + GF_CH))
   Lower leaf 1000 -> 4500, 3.5 m, dying into the cantilever soffit.

4. Delete lines 240-241 (the FF opening in the box's north wall). With the box gone it cuts nothing. The south face of the living volume above z 5000 is then open by absence, so the glass reads 1000 -> 8200 (7.2 m), interrupted only by the 500 mm slab band at 4500-5000 -- which is exactly the shadow line the move is for. The 3.0 m soffit sits at 3.80 m above top water.

5. Lines 293-295 -- stop booking unreachable area as GFA:
   ct = area(LV_X0, WG_Y0 - CANT, LV_X1, WG_Y0)   # covered soffit, NOT GFA
   gf, ff = nb + ww + ew + lv, nb + ww + ew
   and print ct on its own line as "cantilever soffit 18.0 m2 (covered, excluded from GFA)".
   Corrected figures: ground 196.0 / first 163.0 / roof 30.0 -> GFA 389 m2 = 4,187 sq ft. The 407 m2 / 4,381 sq ft currently printed is 18 m2 optimistic. If the 418 m2 brief number must be held, recover it deliberately (deepen the roof pavilion, or extend a wing) rather than by counting a room no one can enter -- flag that as a separate decision.

6. Structure -- replace what the box walls were doing. Those walls currently prop the south edge of the roof plate at x 9000-15000. Once deleted, that plate spans y 18400 -> 9500 (5.9 m plus a 3.0 m overhang), with flank continuity to the wings only through the 2.7 m strips at y 9500-12200 that bridge the light slots. Add two 400 x 700 upstand beams at x 9000-9400 and 14600-15000, y 9500-18400, hidden inside the 1100 mm parapet at z 9200-9900: L/d = 8900/1200 = 7.4, comfortable. CODE GOTCHA: the model is built as (Part() + S) - V, and the parapet void blk(HX0+250, WG_Y0-CANT+250, RF+SLAB, HX1-250, NB_Y1-250, RF+SLAB+PARAPET) = x 3250-20750, y 9750-23750, z 9200-10300 would erase them if appended to S. Add them after the boolean:
   model = (Part() + S) - V
   model = model + upstands

7. villa_sheets.py -- the cantilever now sits below both plan cuts, so it will vanish from A-201 and A-202. Add it back as an overhead line on both sheets, dashed, with a note:
   p.box(v3.LV_X0, v3.WG_Y0 - v3.CANT, v3.LV_X1, v3.WG_Y0, "<dashed overhead layer>")
   p.text("RC CANTILEVER SOFFIT OVER  SSL +4.500  3.0 m PROJECTION", ...)
   The existing chain p.dim_v(v3.WG_Y0 - v3.CANT, v3.NB_Y1, 0, 2200) still measures from y 9500 and stays valid. FIRST needs no new row -- the box was never scheduled, which is itself how the orphan went unnoticed.

REJECT the reviewer's alternative ("if a first-floor room over the pool is wanted, extend the east or west wing south to y=9500 and cantilever from there"). The wings are separated from x 9000-15000 by the 1.0 m light slots, so extending them south does not reach the bay; and any bridge across the 5.1 m void at y 12900-18000 would floor over the double-height living volume, killing the 7.30 m clear space and the 1:3.0 compression release that are the scheme's primary move. The slab is the right answer -- the tall glass to the water is worth more than 13.5 m2 of room.

SEPARATE DEFECT SPOTTED WHILE CHECKING FIRST-FLOOR ACCESS (not part of this criticism, worth its own look): the stair at lines 232-235 makes 16 risers x 244 = 3904 mm, landing at z 4804, against a floor-to-floor of FF - GF = 4100 mm. It stops 196 mm short of the first floor. It needs 17 risers at 241.2 mm.

### Upheld 57

REAL -- every figure reproduces exactly from villa_3d.py, and the substantive claims are geometry, not taste.

ARITHMETIC CONFIRMED. Boundary wall BW=350 → inside face 23.30 x 28.30 = 659.4 m2. Footprint nb 108 + ww 27.5 + ew 27.5 + lv 33 = 196.0 (28.2%). Open ground 463.4. Rear zone 23.30 x 12.15 = 283.1. Pool shell blk(9100,2600 → 14900,12900) clipped at the building line = 5.8 x 9.9 = 57.4. Basin void 5.8 x 1.0 = 5.8. Garden 219.9, splitting as west lawn (x 350-9100) 8.75 x 12.15 = 106.3, east lawn 106.3, south link 5.8 x 1.25 = 7.25. All exact.

THE SEVERANCE IS REAL AND IS WORSE THAN STATED. POOL_Y1 = 12500 is identical to WG_Y0, the outer face of the living-volume wall; the shell (to y=12900) actually laps 400 mm under the wall. So the water touches the house -- there is no route round the north end of the pool at all. The only rear-garden link between the two lawns is the 5.8 x 1.25 m strip at y 350-1600, hard against the 2.4 m boundary wall with the 1.0 m x 900 mm deep catch-basin trench along its inner edge. (The reviewer's "effectively disconnected" is slightly overstated -- there is also a ~45 m detour out through a 2.65 m side strip, round the arrival court and back -- but that is not a garden connection.)

"TERRACE 0 m2" IS CORRECT AT GROUND LEVEL. Nothing in the model provides a dry outdoor surface adjoining a habitable room. The 3.0 m cantilever (FF_FOOT, y 9500-12500) oversails water for its whole length. The Baja shelf sits at the house end (blk(9500,10300 → 14500,12500), top +400 = 300 mm depth), so stepping through the structural glazing puts you 200 mm down onto the water surface and into 300 mm of pool. The pool is raised 700 with no coping walk on any side: north 0 mm (building), south 0 mm (crest → basin), east/west a 700 mm blind shell face to a lawn 700 below. Research §4 requires "pool surround 1.2 m min on back sides, 1.5 m where people walk, 3.5-4.5 m on the lounging side" and "lounge terrace 3.5-4.5 m; dining for 8-10 4.5-5.0 deep x 5.0-6.0 wide". The design meets none of it. (Fair caveat: there is a large roof terrace at +9200; the defect is at ground level, adjoining the living room.)

THE WATERWALL CLAIM UNDERSTATES THE PROBLEM. The basin void spans x 9100-14900, y 1600-2600 -- i.e. it lies along the pool's 5.0 m SHORT south end, not a long side. From a standing eye in the living room (y≈14000, z=2500) the sightline grazes the crest at (2600, 700) with slope 0.158 and lands on the boundary wall at z=345: the basin, the ledge and the entire 700 mm sheet are hidden below the crest. You see zero millimetres of falling water -- not "end-on", but the back of it. The 700 mm raise, justified in the module docstring as the whole answer to research finding #1, buys a spectacle visible only from the 1.25 m dead strip against the wall.

DOCUMENTARY CORROBORATION IN THE FILE ITSELF. villa_3d.py:19-20 states the pool "overflows one long side as a waterwall" -- the model spills the short end. Line 32 states the pool terminates "at 12.0 x 4.0 m" -- the model is 5.0 x 9.5. The rationale was never revisited when the pool was rotated and reproportioned, which is exactly how the short-end spill and the zero surround got in.

WHERE THE REVIEWER IS WRONG. (a) Symmetry per se is not the defect -- a central axial pool flanked by two garden strips is the Court of the Myrtles parti the scheme cites and the research endorses; the defect is that the pool jams against the house at one end and the basin at the other, so the flanks cannot be walked between. (b) The proposed 23.3 x 5.75 = 134 m2 terrace is too much: it leaves ~100 m2 of garden, below the 150-200 m2 target the finding cites two sentences earlier. (c) "Turn the overflow to face north so the waterwall is read from the living room" does not work as written. With the terrace flush at the ground-floor level +900 and the pool crest at +700, the crest sits 200 mm BELOW the terrace plane, so the whole sheet is again invisible from inside; the reviewer's fix only works if the terrace is dropped to garden level, which puts 7 risers between a 6 m structural glass wall and its own terrace -- the opposite of a luxury threshold. The correct move is to abandon the one-sided waterwall for research option (a), the deck-level perimeter overflow, "the correct answer for a flat walled site".

**Corrected fix:**

Rotate the pool east-west and convert it to a deck-level perimeter overflow flush with the ground floor. The rotation is forced, not preferred: the rear zone is only 12.15 m deep, so a north-south pool that is ≥10 m long (research: below 8 m is a plunge pool) mathematically cannot leave a terrace. It does not kill the axis -- it terminates it in a 12.0 m broad face of mirror-flat water instead of a 5.0 m end, which is what actually reads from a 6.0 m glass wall, and it is the Interlude House / Vienna Way read (pool seen broadside across a court from a double-height glass wall) the scheme already cites.

GEOMETRY (villa_3d.py constants)
  POOL_X0, POOL_X1 = 6000.0, 18000.0        # 12.0 m, centred on AXIS 12000
  POOL_Y0, POOL_Y1 = 4200.0, 8000.0         # 3.8 m  -> 45.6 m2 = 6.6% of plot
  POOL_TW = 900.0                            # dead level with GF, not 700 above garden
  POOL_FL = -500.0                           # 1.4 m constant depth, unchanged
Pool 12.0 x 3.8 = 45.6 m2 sits inside research §3 (10-14 x 3.5-4.5; "45-50 m2 is right"), gives a true 12 m lap length the present 9.5 m pool cannot, and a 3.2:1 proportion against the current 1.9:1.

THE PLINTH (terrace + pool as one level at +900, flush with the living-room floor)
  x 4800-19200 (14.40 m) x y 2800-12500 (9.70 m) = 139.7 m2
  Pool surrounds: north 4.50 m (the terrace, y 8000-12500) -- meets both "lounge 3.5-4.5" and "dining 4.5-5.0 deep"; south 1.40 m (>1.2 min on back sides); east/west 1.20 m each. Deck 94.1 m2.
  Terrace proper x 6000-18000 x y 8000-12500 = 54.0 m2: dining 6.0 x 4.5 = 27 m2 west of the axis, lounge 6.0 x 4.5 = 27 m2 east.
  The existing 3.0 m cantilever (x 9000-15000, y 9500-12500) now shades 18.0 m2 of TERRACE rather than 18 m2 of water -- worth far more at this latitude. Update the docstring line 41; the cantilever's stated purpose changes.
  Threshold: zero step from the living room. Upstand 75 mm with a recessed linear channel, membrane returning to 150 mm adjacent.
  Plinth edge: 900 mm stone face to the garden on the south and both ends -- the research's "raised deck 450-900 mm" giving a seat-height edge and concealing the gutter and tank.

WATER DETAIL (replaces the short-end waterwall)
  Deck-level perimeter overflow on all four sides, water dead level with the deck: 20 mm slot, gutter 75 x 75 min falling 1:48, drop pipes 90 mm dia at 1.5 m centres, 38 mm vents, bond beam 550 mm wide extending 600 down, edge tile 9.5 mm granite with a bevelled leading arris laid falling away. The read is the MIRROR, not a vanishing edge -- do not claim a vanishing edge, the plinth only drops 900 mm and the research wants 1.2-1.8 m.
  Level tolerance ±0.8 mm over the whole 31.6 m perimeter. This single number decides whether the pool works; set with a laser at the pour and again at tiling.
  Balance tank 2.0 x 1.2 x 1.6 m deep (~3,800 L, against a 40.7 L/m2 minimum of 1,860 L, sized for a 31.6 m gutter in transit) set under the terrace on the axis at y≈9500, invert −600, i.e. 1.5 m below the water line for gravity fill and flooded suction, clear of the basement (BS_Y0 = 15000). Pipe run to the basement plant room 6-8 m, inside the 15 m limit -- note the present arrangement would blow past 15 m if the pool alone were moved south.
  Baja shelf relocated to the east end: x 16000-18000 (2.0 m front-to-back) x y 4200-8000 (3.8 m along the end), top +600 = 300 mm depth. Meets research 250-350 deep / 1.8-2.5 / 2.5-4.0.
  Delete the spill/basin void entirely (the blk(POOL_X0-400, POOL_Y0-1400, …) line): with a perimeter overflow there is no open trench, which is what removes the severance.

THE GARDEN -- one continuous L wrapping the plinth on three sides, 143.4 m2
  west bay  x 350-4800  (4.45) x y 350-12500 (12.15) = 54.1 m2
  east bay  x 19200-23650 (4.45) x 12.15            = 54.1 m2
  south band x 4800-19200 (14.40) x y 350-2800 (2.45) = 35.3 m2
  Continuous at ground level, no trench, no dead end. Reached from the terrace by a 3.0 m wide flight on the axis at the plinth's south edge: 7 risers at 129 x 344 (2R+G = 601, inside the 600-650 ideal), plus a second flight in the west bay for service and pool maintenance.
  Commit both bays: a 4.0 x 4.0 m tree court with 1.0-1.2 m soil depth in each (4.45 m clear, so it fits), sited at y ≈ 5000-9000 on the living room's diagonal sightlines and framing both ends of the pool. Trees at 4-5 m are also what gives the mirror something to hold: at 3.8 m deep in the viewing direction the pool reflects elements up to roughly its own depth in apparent height, so a 4 m tree reads fully and the 7.3 m glass wall reads only in part -- accept that, or do not sell the reflection of the facade.
  45° load-spread: the plinth's south face at y = 2800 leaves 2.45 m clear of the inner boundary-wall face, well beyond the 0.9-1.5 m the research requires, so the shell no longer needs the raise to justify its footing clearance.

HONEST AREA ACCOUNTING (rear zone 283.1 m2, unchanged)
  before: pool + basin 63.2 | deck 0 | garden 219.9 as 106.3 + 106.3 + 7.2
  after:  pool 45.6 | deck 94.1 | garden 143.4 continuous
  Against research §4 (pool+deck 100-120, main garden 150-200) the fix lands pool+deck at 139.7 (≈20 over) and garden at 143.4 (≈7 under). Both are marginally outside the band, and that is the correct trade on a 12.15 m deep rear zone: 94 m2 of usable, cantilever-shaded terrace is worth more than 84 m2 of lawn that has no terrace, no tree, no route to its twin and nothing to look at.

ALSO FIX IN THE SAME PASS
  Docstring line 19-20 "overflows one long side as a waterwall into a visible basin" and line 32 "12.0 x 4.0 m" are both stale against the model and must be rewritten to match -- the short-end spill and the zero pool surround got in precisely because the rationale was never re-checked after the pool was rotated.
  Cost note, so the client is not surprised: research puts a knife-edge perimeter overflow at up to the cost of the rest of the pool again, against +20-40% for a one-sided ed

### Upheld 58

REAL -- the floor hole is confirmed exactly; the "sealed shaft" half of the claim is false, and the proposed fix is worse than the defect.

VERIFICATION METHOD. I built the model from C:\Users\asdfv\autocad-mcp\villa_3d.py and boolean-intersected it with a 300 mm probe box sitting inside the ground slab (z 500-800) over each scheduled room rectangle from C:\Users\asdfv\autocad-mcp\villa_sheets.py, then divided the resulting volume by the probe height. That returns real slab area per room, not linework.

CONFIRMED (the fatal part):
  FAMILY LIVING   sched 28.60 m2   real 13.60 m2   MISSING 15.00 m2
  GUEST WC        sched  3.65 m2   real  2.75 m2   MISSING  0.90 m2
  every other ground room  sched == real
The reviewer's 15.00 m2 is exact. CT (line 104-105, x 9500-14500 y 15400-19400) cut BASE_FL to GF+200 removes the ground slab (400-900) over its whole 20 m2; 15.00 m2 of that lands in the living room rectangle (9400,12900-14600,18400) and 0.90 m2 in the guest WC, which the reviewer missed. Drop is GF 900 to BASE_FL -2800 = 3.70 m, unguarded.

TWO CONSEQUENCES THE REVIEWER MISSED:
1. The stair launches from nothing. Probe over x 13000-14600, y 18700-19400: slab under the stair start 0.07 m2 of 1.12 m2; first tread at z 900-1000 is 0.02 m2 of 1.12 m2. The court void (top 1100) eats tread 0 and the slab beneath it, so the only route to all four bedrooms starts in mid-air over the 3.7 m drop.
2. The guest-WC east partition (line 190, 10400-10550 x 18400-20400) is cut through its bottom 200 mm where the court passes under it -- it floats.

DRAWING-INVISIBILITY CONFIRMED. Grepping the court's y=19400 edge across all eight output DXFs in C:\Users\asdfv\OneDrive\Desktop\Villa: 0 occurrences everywhere except VILLA_SECTION_AA.dxf (4). The GF plan cuts at GF+1200=2100 and the court tops at 1100, so it cannot appear. It is also absent from VILLA_PLAN_BASEMENT.dxf -- at BASE_FL+1200 the court is indistinguishable from the basement void it opens into, so it has no walls to cut. The court therefore appears on exactly one of eight drawings, and that one contradicts the plan and the schedule. The docstring claim that plan/section/elevation "cannot disagree" does fail here.

WHERE THE CRITICISM IS WRONG -- the room is NOT a sealed shaft:
  LV west flank x 9000-9400, y 12900-18000, z 4600-8600: 0.000 m3 solid of 8.160 m3
  LV east flank x 14600-15000, same extents:            0.000 m3 solid of 8.160 m3
  LV to hall, y 17900-18100, z 1500-4000:               0.00 m2 solid of 1.04 m2
Ground-floor walls stop at GF+GF_CH=4500 and fp_ff excludes the LV bay, so there are no side walls at all above 4.5 m. The volume is open for its full 5.1 m length x 4.2 m height on BOTH long sides straight into the two 1.0 m light slots, which are cut clean through roof slab and parapet to the sky (lines 174-177), and it is open northward to the entrance hall as intended. Daylight is the one thing this room is not short of.
The south-wall half IS a real bug, but a different one: the glazing void (line 238) ends at WG_Y0+300 = 12800 while the wall's inner face is at 12900. Probed: y 12800-12900 is 100% solid across the full 5.2 m opening. The same 100 mm skin is left by the dining and study windows (line 243). Only the first-floor void (line 240) uses WG_Y0+WALL+300 and actually penetrates.

THE PROPOSED FIX IS WORSE. I built it. Court at x 16400-20600 y 19000-23000 sits inside WOMEN'S MAJLIS (15575-20600 x 18400-23600):
  WOMEN'S MAJLIS  sched 26.13 m2   real 9.33 m2   MISSING 16.80 m2
It moves a 15 m2 hole out of the living room and puts a 16.8 m2 hole in the one room the brief names explicitly. Its second half is also wrong dimensionally: LV_X0+400 to LV_X1-400 is 5.2 m, not 6.0 m, and GF to RF is 7.8 m of unbraced glass removing both corners of the volume that the 3.0 m cantilever lands on.

BONUS: build() prints "DH volume 7.30 m clear" from (RF-SLAB-GF). The roof soffit is at RF=8700 and the floor at GF=900, so the clear height is 7.80 m and the compression ratio is 1:3.25, not 1:3.0. The reviewer's 7.8 m is right and the script's own print is wrong.

**Corrected fix:**

Three changes, all in C:\Users\asdfv\autocad-mcp\villa_3d.py. Change 1 is verified by rebuild; changes 2-3 follow from the same probes.

1. MOVE THE COURT OUT OF THE FOOTPRINT ALTOGETHER, to the front garden on the service side. Not into the majlis.
   Lines 104-105:  CT_X0, CT_X1 = 17200.0, 21000.0
                   CT_Y0, CT_Y1 = 24000.0, 26800.0
   Court 3.8 x 2.8 = 10.6 m2, floor at BASE_FL -2800, open to the sky at STREET 0.0 -> 2.80 m deep, aspect 1:1.00 (the original 5.0 x 4.0 at 3.7 m was 1:0.93, so no loss of daylight geometry). It sits against the basement's existing north wall, so the basement is lit through that wall rather than through a hole in the living room.
   Rebuilt and probed: every ground-floor room now returns sched == real. FAMILY LIVING 28.60/28.60, GUEST WC 3.65/3.65, MAJLIS 26.13/26.13. Basement interior becomes a true 141.0 m2 (17.2 x 8.2), so the "basement 142 m2 excl. sunken court" print at line 306 must change to that figure plus a separate 10.6 m2 external court.
   Replace line 132 (the court cuts nothing now -- it is in the garden and needs its own retaining box):
       S.append(blk(CT_X0 - 300, CT_Y0, BASE_FL - 400, CT_X1 + 300, CT_Y1 + 300, STREET))
       V.append(blk(CT_X0, CT_Y0 - 500, BASE_FL, CT_X1, CT_Y1, STREET + 400))
       V.append(blk(CT_X0 + 400, BS_Y1 - WALL - 300, BASE_FL + 100,
                    CT_X1 - 400, BS_Y1 + 300, BASE_FL + 2600))   # glazed wall to basement
   That last void is a 3.0 x 2.5 m glazed opening (x 17600-20600, z -2700 to -200) through the basement's north wall; basement clear is 3.2 m so it fits with a 500 head. Add a 1100 mm guard/planter to the court's three exposed garden sides.
   Clearances checked: 0.60 m clear of the pedestrian gate void (x 15400-16600), 2.65 m clear of the east boundary wall inner face (23650), 1.85 m clear of the north boundary wall inner face (28650), 4.55 m clear of the rill, no overlap with the car porch. The 1.85 m north clearance is less than the 2.8 m excavation depth, so the north retaining wall carries the boundary-wall footing surcharge -- the same 45-degree load-spread condition the raised pool already answers. Confirm local rules permit a below-grade lightwell in the 5.0 m front setback. Service routing is a bonus: the service entrance is already on the east boundary at HX1, y 18700-19800, so staff reach the court stair and the basement without crossing guest or family space.

2. FIX THE 100 MM SKIN -- do not delete the south wall. Change the three ground-floor south voids from WG_Y0 + 300 to WG_Y0 + WALL + 300 (12800 -> 13200), matching what the first-floor void at line 240 already does:
   line 239:  LV_X1 - 200, WG_Y0 + WALL + 300, GF + 3400
   line 243:  blk(x0, WG_Y0 - 300, GF + 450, x1, WG_Y0 + WALL + 300, GF + 3100)
   The living room then gets a real 5.6 x 3.3 m opening onto the pool (x 9200-14800, z 1000-4300) that keeps a 200 mm return of wall at each end, instead of a 5.2 x 7.8 m unbraced glass wall under the 3.0 m cantilever.

3. ADD THE FLOOR-PLATE AUDIT -- as a boolean probe, not a second section. A section at GF+50 returns edges you then have to reassemble into faces; intersecting a 300 mm probe with each scheduled rectangle gives the area directly:
       def floor_audit(model, rooms, z_floor, allow={}):
           for name, x0, y0, x1, y1, kind in rooms:
               got  = model & blk(x0, y0, z_floor - 400, x1, y1, z_floor - 100)
               a    = (got.volume if got else 0.0) / 300.0 / 1e6
               full = (x1 - x0) * (y1 - y0) / 1e6
               gap  = full - a - allow.get(name, 0.0)
               if gap > 0.05:
                   raise AssertionError(f"{name}: schedule {full:.2f} m2, "
                                        f"real floor {a:.2f} m2, {gap:.2f} m2 missing")
   Call it for GROUND at GF and FIRST at FF. The first floor needs allow={"LANDING": 5.12} -- the landing legitimately loses 1.6 x 3.2 m to the stairwell void at line 235, and that was the only first-floor discrepancy my run reported, which is the correct answer. Add a companion assertion that the bottom stair tread has slab under it, since the current court also removed that.

### Upheld 59

Confirmed on every count by direct arithmetic on villa_3d.py.

COURT IS INSIDE THE FOOTPRINT. CT = x 9500-14500, y 15400-19400 (lines 104-105), cut BASE_FL(-2800) to GF+200(1100) (line 132). Decomposed against the ground footprint: 13.0 m2 inside the living-volume block (LV x 9000-15000, y 12500-18000), 7.0 m2 inside the north bar (x 3000-21000, y 18000-24000), 0.0 m2 outside. The whole 20 m2 is under the building.

FAMILY LIVING IS HOLED. Schedule rect 9400-14600 x 12900-18400 = 28.6 m2; court intersection 5.0 x 3.0 = 15.0 m2 = 52.4%, dropping 900 - (-2800) = 3.70 m, with no guarding modelled. villa_sheets.py:33 books the full 28.6 m2. derive() cuts the GF plan at GF+1200 = 2100, above the void top of 1100, so a horizontal section cannot show the hole; the rendered A-201 shows a continuous floor labelled 28.6 m2 and no court anywhere on the sheet. The reviewer under-counted: the court also removes 0.9 m2 of the guest WC floor (x 9500-10400, y 18400-19400) and the bottom 200 mm of its east partition (10400-10550, 18400-20400).

STAIR. Tread 0 (x 13000-14600, y 18700-18870, z 900-1144): x-overlap with the void 1500 of 1600 mm, z-overlap 200 of 244 mm. Treads 1-3 sit wholly over the void, tread 4 over 20 of its 170 mm. Confirmed.

ZERO DAYLIGHT. The roof slab (line 165) spans x 3000-21000, y 9500-24000 at z 8700-9200 and covers 20.0 of 20.0 m2 of the court. The 1.0 m light slots are at x 8000-9000 and 15000-16000; the court's x-range 9500-14500 misses the nearer by 500 mm. The only sky access to the basement anywhere is two accidental 1.0 x 0.3 m slivers (0.6 m2) where the slots overrun the north bar. It is a fully roofed shaft, which voids research finding 2 (VILLA_RESEARCH.md:58-60, 341). Stronger than the reviewer knew: the south "structural glazing" void (line 238) spans y 9200-12800 against a ring wall whose inner face is at 12900, leaving a 100 mm unpierced skin; the two wing windows (line 243) repeat the identical 100 mm residue. So even borrowed light is blocked as modelled.

NO ACCESS. The only stair is the 16-tread run at lines 232-234, GF 900 to 4804. No lift, no ramp, nothing reaches BASE_FL. 142 m2 unreachable. (Collateral: that run lands 196 mm below FF=5000 and uses 244 mm risers against the research's own 100-180 cap, VILLA_RESEARCH.md:156.)

Not taste, not a rendering artefact: a 15 m2 unguarded 3.7 m hole in the principal ground-floor room, a stair tread cut away over 94% of its width, a sunken courtyard with a slab over it, and an inaccessible basement.

The reviewer's own proposed fix is internally inconsistent and should not be adopted verbatim: a court at y 7500-11500 cannot glaze a basement shrunk to y 18000-24000; y 9500-11500 of that option is under the roof plate, which spans the full 18 m width (x 3000-21000), not just the living volume as they assume; and the forecourt option at x 16000-21000, y 24400-28400 stands 400 mm clear of the basement's north wall (so it glazes nothing) and leaves only 250 mm to the north boundary wall's inner face at 28650.

**Corrected fix:**

Three edits. The court must leave the footprint entirely, the basement must grow an arm to reach it, and the section must gain the vertical circulation it never had.

1. BASEMENT RETREATS OUT FROM UNDER THE LIVING ROOM AND GROWS A SOUTH ARM
   BS_X0, BS_X1 = 3000, 21000 ; BS_Y0, BS_Y1 = 18000, 24000   (was 15000)
   BSA_X0, BSA_X1 = 17000, 21000 ; BSA_Y0, BSA_Y1 = 9500, 18000   (new arm)
   Main body 18.0 x 6.0 = 108.0 m2 gross, internal 17.2 x 5.2 = 89.4 m2, wholly under the north bar. Arm 4.0 x 8.5 = 34.0 m2 gross, internal 3.2 x 8.5 = 27.2 m2 (no wall where it meets the main body at y 18000). Total 142.0 m2 gross - the same figure the script already prints - and ~116 m2 internal against a net requirement of 63 m2 (maid+bath 15, laundry 10, store 8, plant 16, pool plant 14, VILLA_RESEARCH.md:339-341) plus stair 10.7, lift 2.7 and ~18 of lobby/corridor = 94 m2. Nothing sits under FAMILY LIVING (x 9400-14600, y 12900-18400): its 28.6 m2 floor bears on ground and villa_sheets.py:33 becomes true.
   The arm's west wall at x 17000 stands 400 mm clear of the 45-degree spread cone from the pool shell (shell east face 14900, base -1100; cone reaches x 16600 at -2800) - the check the research demands at VILLA_RESEARCH.md:240-243.
   Terrace over the arm at y 9500-12500 sits at +400, not grade, so the arm keeps 3.20 m clear throughout: two 250 mm risers down from GF +900, two 200 mm risers down to the garden (never a single step in an open terrace, VILLA_RESEARCH.md:368).

2. THE COURT BECOMES A REAL COURT, IN OPEN GROUND, OPEN TO SKY
   CT_X0, CT_X1 = 17000, 21000 ; CT_Y0, CT_Y1 = 4500, 9500  -> 4.00 x 5.00 = 20.0 m2
   Cut BASE_FL-300 (-3100, for a 150 mm white-pebble bed, falls and a pumped sump for a 1-in-100-year storm) up to STREET (z = 0) - terminating at grade, NOT at GF+200. Depth below grade 2.80 m (research band 2.7-3.3 m); 4.0 x 5.0 clears the 4 x 4 minimum and hits the 5-6 m "facing the glazing" ideal (VILLA_RESEARCH.md:374-376).
   It is genuinely unroofed: the roof plate starts at y 9500, so it stops exactly on the court's north lip - the 3.0 m overhang shelters the head of the glazing while the court keeps full sky. It sits in the south-east lawn (pool shell ends x 14900; cantilever bar ends x 15000), clear of everything.
   Glaze the arm's south wall full height: opening x 17400-20600 (3.20 m), sill -2800, head -350, i.e. 2.45 m. Model it as V.append(blk(BSA_X0+WALL, BSA_Y0-300, BASE_FL+50, BSA_X1-WALL, BSA_Y0+WALL+100, -350)) - note the +100 past the 9900 inner face, so this opening does not repeat the 100 mm unpierced skin that afflicts the three ground-floor openings at lines 238 and 243.
   North-facing glazing onto a sunlit white-pebble floor is the correct orientation, not a compromise - it is the F.LOT detail the research cites.
   Guarding: 1.10 m frameless glass balustrade set 300 mm back on the three garden sides, so the guard does not shade the court.
   Second means of escape, in the court and parallel to the glass so it obstructs nothing: open external switchback along the court's south edge, footprint x 17000-21000 by y 4500-6800 (4.00 x 2.30 m), 20 risers at 140 mm = 2800, going 340 (2R+G = 620, inside the research's 600-650), two 1.10 m flights with a 1.20 m half-landing at the west end. Leaves 4.00 x 2.70 m of planted court directly in front of the glazing.
   Plan the arm accordingly: maid's room + bath and laundry at the south end on the glazing; plant, tanks and pool plant north, in the dark, beside the service entrance. Served rooms get the light; servant rooms do not need it.

3. THE VERTICAL CIRCULATION THAT IS MISSING
   Replace lines 232-235 with a three-storey core in the strip x 10550-15425, y 18400-20550 plus its projection into the hall:
   - Stair core x 12350-14850 (2.50 m = two 1200 flights + 100 well), y 18400-22680 (4.28 m = 11 x 280 + 1200 landing).
     GF -> FF: rise 4100, 24 risers at 170.8 mm, going 280 (research: going >= 280, riser 100-180, luxury 170). This also repairs the existing run, which lands at 4804 - 196 mm short of FF - on 244 mm risers.
     GF -> BASEMENT: rise 3700, 22 risers at 168.2 mm, going 280, two flights of 11 (10 x 280 + 1200 = 4000 mm, inside the same 4.28 m core), descending directly beneath the up-flight.
   - Lift shaft 1600 x 1700 clear (VILLA_RESEARCH.md:327) at x 10650-12250, y 18500-20200: 100 mm clear of the guest WC east wall at 10550, 200 mm clear of its north wall at 20400, 100 mm clear of the stair core. Pit 1.5 m -> -4300. Serves -2800 / +900 / +5000; 3.6 m overrun to +8600, 100 mm under the roof slab soffit at 8700, so it does not break the G+1+roof line. The roof pavilion keeps its own stair head.
   - Basement arrival lobby at -2800 under the hall, corridor east to the arm, west to plant.
   The core takes 5.3 m2 out of the 20.9 m2 entrance hall, leaving 15.6 m2 clear; schedule it as hall + open stair 26.3 m2, inside the research's 18-30 m2 band. If a clear 18 m2 is wanted, move the majlis partition (15425/15575) 600 mm east.

4. DRAWING CORRECTIONS - without these the defect stays invisible
   A horizontal section can never show a hole below its cut plane, so the court must be drawn, not derived: add it to villa_sheets.py as a hatched void with "SUNKEN COURT -2.80" and a dashed line of the roof overhang. Add the basement plan to SHEETS - VILLA_PLAN_BASEMENT.dxf is generated at line 352 and then never sheeted, which is precisely why 142 m2 with no stair went unnoticed. Update the area print: with the court now outside the footprint it is no longer deducted, so base = area(BS) + area(BSA) = 108 + 34 = 142 m2, and the court is reported separately as 20 m2 of external sunken court.

### Upheld 60

CONFIRMED -- I could not refute it, and the checked geometry is slightly worse than the reviewer states.

VERIFIED FROM THE SOURCE (C:\Users\asdfv\autocad-mcp\villa_3d.py:231-235):

    for i in range(16):
        S.append(blk(13000, 18700 + i * 170, GF + i * 244,
                     14600, 18870 + i * 170, GF + (i + 1) * 244))
    V.append(blk(13000, 18700, GF + GF_CH, 14600, 21900, FF))

Each step block is 170 mm deep in y and 244 mm tall, and consecutive blocks step 170 in y -- so going = 170, rise = 244, zero nosing overlap. Pitch = atan(244/170) = 55.13 deg. 2R+G = 658. Levels from lines 69-78: BASE_FL -2800, GF +900, FF +5000, RF+SLAB +9200. 16 x 244 = 3904 against FF - GF = 4100, so the top tread is 196 mm below the landing. This is not taste: VILLA_RESEARCH.md:156-157 sets going >= 280 (luxury 300-320), riser 100-180 (luxury 170), max 30 deg. 244/170 fails every one, and it fails IBC (max riser 196 / min tread 254) and Part K (max rise 220, min going 220, max pitch 42 deg) as well.

WORSE THAN CLAIMED: the void is y 18700-21900 (3200) but the run is only 16 x 170 = 2720, ending at y 21420. So the first-floor slab is removed for a further 480 mm PAST the top tread. At the head of the flight there is a 1600 x 480 mm unguarded hole straight down to the ground floor -- the arrival is not merely 196 mm low, there is no floor in front of it at all.

NO OTHER VERTICAL CIRCULATION: grep over villa_3d.py, villa_sheets.py, plan_dxf.py, villa_3d_native.py, villa_load_all.py returns exactly one stair (plan_dxf.py:66 STAIR belongs to the earlier house_* project and is never referenced by villa_sheets.py). Basement (BS x 3000-21000, y 15000-24000, floor -2800, 142 m2): the only opening in the ground slab is the sunken-court void CT (x 9500-14500, y 15400-19400) and it contains no stair or ramp. Roof: I checked every void box against the roof slab under the pavilion (z 8700-9200, x 9000-15000, y 19000-24000) -- intersection volume is 0 for all five. The pavilion floor is solid; the 30 m2 pavilion is unreachable. No lift anywhere, on a four-level house (-2.80 / +0.90 / +5.00 / +9.20).

The research the design was built from asks for exactly what is missing: VILLA_RESEARCH.md:327 "Stair per floor 14-18 m2; lift shaft 1.6 x 1.7 m internal, 1.5 m pit, 3.6 m overrun", :333 ground "stair+lift 18", :337 roof "stair head + lift overrun 16".

It is also visible in the delivered set: derive() cuts the ground plan at z = 2100, which slices exactly one step block, so A-201 shows the stair as a single 1.6 x 0.17 m sliver in the entrance hall with no up-arrow. villa_sheets.SHEETS produces no basement and no roof sheet at all, so the missing access is never drawn.

CORROBORATION of the reviewer's "reachable GFA 359": the first-floor cantilever piece in FF_FOOT (x 9000-15000, y 9500-12900, the 18 m2 'ct' term at line 293) is a disconnected island in the union footprint -- the light slots at x 8000-9000 and 15000-16000 separate it from both wings, so shell() rings it as a sealed box with no floor connection either.

ONE SUB-CLAIM I DO REFUTE: "no vehicle access" to the basement is not a defect. The scheme deliberately parks in a covered porch in the front setback (lines 250-256, PORCH 7.0 x 4.0, with the reasoning stated: the north bar is 5.2 m deep internally and a two-car garage needs 5.5-6.5 m). The basement is staff and plant only, so it needs people-access, not a ramp. Everything else in the criticism stands.

The reviewer's own proposed fix also needs correcting twice: 24 x 171 = 4104, 4 mm out -- the same class of bug -- so the rise must be computed as (FF-GF)/24 = 170.833, not hardcoded; and their 1.4 m flights give a 2.8 x 5.0 m core, which does not fit the north bar's 5.2 m internal depth once an arrival landing is added. 1.2 m flights at 2.4 x 4.6 do.

**Corrected fix:**

ONE STACKED HALF-TURN CORE SERVING ALL FOUR LEVELS, PLUS A LIFT.

1. Core footprint, identical at every level: x 13025-15425, y 19000-23600 (2400 x 4600 = 11.0 m2 per floor). Two 1200 mm flights back to back with a closed well (west half 13025-14225 = up-flight, east half 14225-15425 = down-flight, same handedness at every storey so a tread and the soffit above it are always ~3.7 m apart). East face lands on the existing hall|majlis partition at x 15425; west face clears the 1500 mm axial corridor (x 11250-12750 from the front door) by 275 mm, so the entrance-to-pool perspective survives untouched.

2. Flights -- going 300 throughout, nosing 25, rise computed from the level difference, never typed:
   BASEMENT -2800 -> GROUND +900 (3700): 22 risers x 168.18 mm, 2 flights of 11, run 10 x 300 = 3000, pitch 29.3 deg, 2R+G = 636. Half-landing -950 at y 22000-23600.
   GROUND +900 -> FIRST +5000 (4100): 24 risers x 170.83 mm, 2 flights of 12, run 11 x 300 = 3300, pitch 29.7 deg, 2R+G = 642. Half-landing +2950 at y 22300-23600.
   FIRST +5000 -> ROOF +9200 (4200): 24 risers x 175.00 mm, 2 flights of 12, run 3300, pitch 30.3 deg, 2R+G = 650. Half-landing +7100 at y 22300-23600.
   Core depth needed = 3300 + 1300 landing = 4600, exactly the 4600 provided.

3. Slab voids, all x 13025-15425, y 19000-23600: ground slab z 400-900, first slab z 4500-5000, roof slab z 8700-9200. The arrival landing at each level is the plate immediately SOUTH of y 19000. Balustrade the full stairwell.

4. First-floor arrival landing -- pull the double-height void's north edge back from y 18000 to y 16800: V.append(blk(LV_X0+WALL, WG_Y0, GF+GF_CH, LV_X1-WALL, 16800, FF)). The void becomes x 9400-14600, y 12500-16800 = 5.2 x 4.3 = 22.4 m2, still 7.30 m clear; the recovered 1.6 m strip is a gallery over the living room and gives a 2200 mm deep arrival landing (y 16800-19000) at the head of the stair. Without this the landing is only 700 mm deep and the stair is still unusable.

5. Roof -- extend the pavilion to PV = (9000.0, 18400.0, 15400.0, 24000.0) so the stair head and its landing are enclosed: 6.4 x 5.6 = 35.8 m2 (research 5 wants stair head + lift overrun 16, roof pantry/WC 8, store 9 ~ 33). GFA 407 -> 413 m2, still inside the 418 m2 brief.

6. Lift -- shaft 1900 x 2000 structural / 1600 x 1700 internal (VILLA_RESEARCH.md:327), at x 8575-10475, y 21600-23600, stopping -2800 / +900 / +5000 / +9200. Pit floor -4300 (local deepening below the -3200 basement slab). Specify an MRL lift with overrun <= 2900 so the head stays inside the 3.0 m pavilion (9200 + 2900 = 12100 < 12200); otherwise express a 600 mm upstand. This displaces two things, both improvements: the guest WC moves to x 8575-10475, y 18400-20500 (4.0 m2, up from 3.6 and now matching the research's 4 m2), and the hall->kitchen door moves to x 8425-8575, y 20700-21400. Stair 11.0 + lift 3.8 = 14.8 m2 per floor, inside the research's 14-18.

7. Escape -- with one stair plus a lift, enclose the core at basement level as a fire-rated shaft with a self-closing door. The sunken court cannot be the second escape as modelled: CT (x 9500-14500, y 15400-19400, void to +1100) sits UNDER the ground floor and punches a 20 m2 hole through the ground slab in the middle of the family living room, so it sees no sky. Open it to the sky (or relocate it) before relying on it -- a separate defect worth its own fix.

8. Assert it in build() so this cannot recur:
   GOING = 300.0
   for z0, z1, n in ((BASE_FL, GF, 22), (GF, FF, 24), (FF, RF + SLAB, 24)):
       rise = (z1 - z0) / n
       assert abs(n * rise - (z1 - z0)) < 1e-9, "risers must close the level"
       assert 100.0 <= rise <= 180.0, rise
       assert GOING >= 280.0
       assert math.degrees(math.atan2(rise, GOING)) <= 32.0
       assert 550.0 <= 2 * rise + GOING <= 700.0
   plus a reachability check that every slab (ground, first, roof) carries a void inside the core footprint, and that each level's arrival landing is at least 1200 x 2400 of solid plate.


### Refuted (kept for the record)

**1.** REFUTED. The setting-out grid exists and the evidence cited is not evidence of setting-out.

1. A clean plan grid is present. X lines are all on 1000: 3000/8000/9000/15000/16000/21000, giving bays 5000/1000/6000/1000/5000 = 18000, symmetric about x=12000. Y lines are all on 500: 3000/12500/18000/24000. Derived objects sit on it: pool 9500-14500 centred on the axis; roof pavilion 9000-15000 on exactly the living-volume bay below; sunken court 15400-19400 = gridline 15000 + 400 wall, 4000 deep; porch 24400-28400 = gridline 24000 + 400, 4000 deep.

2. The reviewer's evidence list is component thicknesses, not setting-out lines. A 600 module never demanded a 600 wall - the reviewer concedes exactly this in their own fix ("keep the 400 mm wall as structure but set out from face lines"). Faces i

**2.** Both headline assertions in the title are factually wrong against the model, and the proposed fix is arithmetically self-contradictory.

1) "It aligns with nothing" -- false. The pool is POOL_X0/X1 = 9500/14500, POOL_Y0/Y1 = 3000/12500 (villa_3d.py lines 94-95). Checking every alignment the criticism says is absent:
   - Centred on AXIS. Midpoint (9500+14500)/2 = 12000 = AXIS (line 91), which is also the dead centre of the 24 m plot, the centre of the guest entrance void (AXIS±750, line 248), the centre of the rill (lines 273-276) and the centre of the roof pavilion PV = 9000..15000 (line 107). The whole scheme is symmetric about x=12000: WW 3000-8000, slot 8000-9000, LV 9000-15000, slot 15000-16000, EW 16000-21000.
   - It matches the sunken courtyard exactly. CT_X0, CT_X1 = 9500, 14500 (

**3.** The factual evidence is inverted. The claim is that the opening void "overshoots 300 mm on both sides of a 400 mm wall" so the glazing plane is flush with or outside the external face. Check the actual numbers.

WG_Y0 = 12500 and the exterior (garden/pool) is at LOW y, so the south wall band runs y 12500 (outer face) to 12900 (inner face). The wing windows on lines 242-244 are cut `WG_Y0 - 300` to `WG_Y0 + 300` = y 12200 to 12800. The first 300 mm of that void (12200-12500) is in open air outside the building and removes nothing. Inside the wall the void runs 12500 to 12800 and STOPS 100 mm short of the inner face. Reveal = 300 mm, not 0. The void overshoots on ONE side only -- the outside, where there is nothing to cut. Same for the GF structural glazing (void ends 12800), the guest entra

**4.** REFUTED -- the criticism rests on a misread of the geometry, and the half that survives is taste.

1. THE SLOT IS NOT A FOUR-SIDED SHAFT, SO 1:9.9 IS THE WRONG NUMBER. Lines 174-177 cut the voids from y = WG_Y0 - 300 = 12200 to WG_Y1 + 300 = 18300. The wings and the living volume start at WG_Y0 = 12500, so the cut begins 300 mm SOUTH of the building's south face and nothing is built at x 8000-9000 (or 15000-16000) south of y 12500 at any level: GF_FOOT and FF_FOOT (lines 138-142) cover 3000-8000, 9000-15000 and 16000-21000 only, and the FF cantilever rect starts at x = 9000. The slot's south end is therefore an open face 1000 wide x 8300 tall (grade +400 to the roof soffit at RF = 8700), and the top is an open 1.0 x 6.1 m sky aperture. That is 14.4 m2 of aperture on a 60 m3 void, open on t

**5.** REFUTED. The criticism reads the south elevation as a flat plane. It is not -- it is a three-plane composition with 3.0 m of depth, and the reviewer's two central assertions ("no dominant void, no dominant solid" and "the only asymmetry is accidental") are both false against the model.

WHAT IS ACTUALLY IN THE FRONT PLANE (y = 9500, i.e. 3.0 m forward of the wings at y = 12500):
1. The roof slab and parapet, `blk(HX0, WG_Y0-CANT, RF, HX1, NB_Y1, RF+SLAB)` and the parapet above it (lines 165-166): x 3000-21000, front face at y 9500, z 8700-10300. That is a continuous 18.0 m x 1.6 m horizontal band across the ENTIRE elevation, cantilevered 3.0 m. Critically, the two light slots (lines 174-177) are cut only from y 12200 northward, so they do not break this band -- the top 1600 mm reads as one

**6.** REFUTED. Two of the four evidence points are factually wrong about the model, and the other two are either a taste rule invented for the occasion or an inherent property of orthographic projection.

1. "Deeper than it projects / 0.71:1" -- the raw numbers are right (front plane y=9500, soffit z=4500, wall top z=8700 = 4200 mm storey, flush roof slab + parapet to z=10300 = 5800 mm total), but the ratio is measured wrong and the rule is fabricated. A cantilever's "depth" is its structural depth, not the height of the room sitting on it: villa_3d.py line 73/160 gives SLAB = 500 mm over a 3000 mm projection = span/depth 6.0, which sits inside the Eurocode band the research quotes (VILLA_RESEARCH.md line 129-132: basic 8, "3 m RC cantilever -> ~215-375 mm effective depth", "2.5-3.5 m is the vil

**7.** The measurement is correct; the diagnosis is not. Confirmed by running the coordinates: pool shell is x 9100-14900, y 2600-12900, z -1100 to +700 (villa_3d.py lines 266-267 -- not 192-193, which are PARTS_GF partitions); the LV ground slab is x 9000-15000, y 12500-18000, z 400-900 (line 155 via fp_gf). Overlap is exactly 5800 x 400 x 300 mm. But that overlap is not a collision -- it is a coincidence of two elements that are one element in construction, and three things show it is intentional rather than accidental:

1. THE OVERLAP IS EXACTLY THE BUILDING'S OWN WALL ZONE. The LV footprint rect is y 12500-18000; shell() offsets it inward by WALL=400, so the building's south wall occupies y 12500-12900 with its outer face on 12500. POOL_Y1 is set to 12500 -- the same number as WG_Y0 -- so the

**8.** The arithmetic is right and the conclusion drawn from it is wrong.

WHAT IS CONFIRMED. Line 165 gives the roof slab blk(3000, 9500, 8700, 21000, 24000, 9200) and line 166 the parapet to 10300; FF_FOOT line 142 gives the cantilever box rect (9000, 9500, 15000, 12900). Both front faces sit at y = WG_Y0 - CANT = 9500. Offset 0 mm, across a parapet top at 10.3 m. That much is true.

WHY IT IS NOT A DEFECT.

1. The reviewer has mis-identified what the cantilever reads against. It is not the roof -- it is the ground floor and the wings. The GF footprint (line 138) puts every south face at y = 12500, and the structural glazing (lines 238-239, x 9200-14800, z 1000-4300) sits in that wall. The box face at 9500 therefore stands 3,000 mm proud of the glass below it, under a soffit at z = 4500, i.e. 3

**9.** REFUTED. The load-bearing sentence of the evidence -- "the centre bay's only distinction is that it is 1.0 m wider" -- is false against villa_3d.py. The model differentiates the centre five separate ways, three of which are exactly the payments the reviewer says symmetry demands (a differentiated centre, a change of material, a change of aperture):

1. APERTURE. Wings (lines 242-244): two punched openings 2.60 x 2.65 m and 2.60 x 2.25 m, ~35% WWR on a solid plane. Centre (lines 238-241): structural glazing 5.60 x 3.30 m running the full clear width of the room, plus a separate 5.60 x 2.60 m band at first floor. That is a solid-vs-void reversal, not a 1.0 m width difference.
2. SECTION. Centre is 7.30 m clear double height (RF-SLAB-GF); wings are two stacked storeys at 3.6 / 3.2 m. The elev

**10.** REFUTED. The reviewer's arithmetic on the vessel is right; the method that generates the demand is wrong, and the two conclusions that follow from it collapse.

1. THE 6% MARGIN IS A SIGN ERROR. The 2,744 L demand adds five terms as if they all pulled the level the same way. They do not. Bather displacement (560 L) and shutdown film drawdown (238 L) are SURPLUS -- they push water INTO the tank and consume headroom. Backwash (1,570 L) is a DEFICIT -- it takes water OUT and consumes drawdown room. Transit water is one of each (out at start, back at stop). You cannot sum them into one one-directional demand. The signed peak-to-peak swing is high (+560, 8 bathers, pumps running) to low (−1,570, backwash) = 2,130 L against 2,900 L working = 36% margin, not 6%. Set the running level ~300 mm down

**11.** Refuted. The criticism is arithmetically checkable against villa_3d.py and it fails on its own numbers.

**1. It missed the Baja shelf -- which is the entire reason the cantilever lands where it does.**
Line 271-272: `S.append(blk(POOL_X0, POOL_Y1 - 2200, POOL_FL, POOL_X1, POOL_Y1, POOL_TW - 300))` = x 9500-14500, y 10300-12500, top z +400. That is a 5.0 x 2.2 m sun shelf, 11.0 m2, in 300 mm of water, at the NORTH end -- hard against the house. The cantilever runs y 9500->12500 (`FF_FOOT` line 142, `WG_Y0 - CANT` to `WG_Y0 + WALL`). The shelf sits entirely inside the cantilever's footprint, with 3.8 m clear from water surface (+700) to soffit (+4500).

So the claim "the cantilever shades water instead of people" is false. It shades a 11 m2 shallow lounging shelf -- the element VILLA_RESEAR

**12.** REFUTED. The criticism's load-bearing claim -- "the volume is lit only from the bottom... Apertures above 4.30 m: zero" -- is false in the model. It is an artifact of reading section A-A alone, which is cut on the plane x = AXIS = 12000, i.e. straight down the middle of the bay and parallel to the two light slots, so it is the one drawing that geometrically cannot show the volume's side lighting.

WHAT THE MODEL ACTUALLY DOES ABOVE 4.50 m (C:\Users\asdfv\autocad-mcp\villa_3d.py)
- Lines 174-177 cut two 1.0 m slots (x 8000-9000 and 15000-16000, y 12200-18300) from z = GF-SLAB all the way through RF+SLAB+PARAPET -- i.e. through the roof slab and parapet, open to the sky for their full 6.1 m length.
- The bay's ground walls (walls_gf, line 153) stop at GF+GF_CH = 4500. FF_FOOT (lines 140-142)

**13.** REFUTED. Three of the criticism's load-bearing claims are false against the model, and the proposed fix lands on ground that does not exist.

1. "All of them see the back of the weir: a blank 700 mm rim" -- geometrically impossible. The spill face is a vertical plane at y=2600 facing SOUTH. A south-facing vertical surface is self-occluded from every eye north of it, at any height; nobody in the house sees a "blank 700 mm rim," because the rim's outer face is hidden behind its own top edge. What they see is the water plane running to a knife edge. And the 700 mm raise makes that edge work here: from the living-room glazing standing (eye z=2500, y=12900) the crest hides 4,006 mm of ground beyond it; seated 3 m into the room, 7,162 mm. Only 2,250 mm of ground exists between crest and boundary

**14.** REFUTED. I ran a point-in-solid classifier (OCC BRepClass3d_SolidClassifier) over the built model rather than reading the source, and four of the criticism's five load-bearing claims are false.

1. "No opening in the whole model faces a slot ... they do not light one square metre of anything" -- FALSE above +4.5 m. FF_FOOT (villa_3d.py:140-142) contains no rectangle covering x 8000-16000 at y 12900-18000, so there is no first-floor wall between the double-height living volume and either slot. Classifier at y=15000: the LV west wall line x=9200 is SOLID at z=2500 but void at z=4750, 6000 and 8000; same for the east wall line x=14800; the west wing's east wall x=7800 is SOLID at all three. So from +4.50 m to the roof soffit at +8.70 m the living volume is fully open to both slots along their

**15.** REFUTED on all four legs. The basin in `villa_3d.py` (BASIN_D=900, the void at x 9100..14900, y 1600..2600, z -900..+640) is 5.8 x 1.0 m in plan = 5.80 m2, and the reviewer's own arithmetic is right -- it is the premises that fail.

1. THE 6% MARGIN IS MANUFACTURED BY STACKING WORST CASES ON BOTH SIDES OF THE LEDGER. VILLA_RESEARCH.md §Catch basin gives ranges, and the reviewer takes the top of every one on the demand side and the bottom on the supply side. Backwash: research says "backwash 500-1,500 L"; the reviewer uses 1,570 L (1.0 m filter, 4 min), above the research's own ceiling -- a 0.9 m filter (research allows 0.9-1.2 m) at 3 min is 954 L. Freeboard and cut-out: research says "freeboard 150-250 mm + low-level cut-out 150-200 mm"; the reviewer deducts 200+200, the maximum of both. 

**16.** The arithmetic is correct but the conclusion does not follow. Verified in villa_3d.py: line 165 puts the roof slab front at y = WG_Y0 - CANT = 9500 across the full HX0-HX1 = 18,000 mm, and the FF_FOOT living-volume rect on line 142 puts the cantilever box front at y = 9500 as well. Offset is genuinely 0 mm, and the light-slot voids (lines 174-177) start at y = 12200, so the roof does stay solid for the front 2,700 mm across all 18.0 m and the top edge is unbroken. Parapet top is RF + SLAB + PARAPET = 10,300. All confirmed. What is wrong is the leap from that to "fatal".

1. THE SCHEME'S DEEPEST REVEAL IS 3,000 MM, NOT 0 MM, AND THE REVIEWER COUNTED IT AS ONE OF THE "TWO PLANES". Below the box the ground-floor face sits at y = 12500 (wall) / 12800 (structural glazing, the void on line 238 c

**17.** I built the model and classified points against the solid rather than reading the source. The reviewer's plan geometry is right, their interpretation of it is wrong on all three counts, and their fix does not fit the plot.

(b) is the load-bearing claim and it is false. `villa_3d.py:271` places a Baja shelf across the FULL pool width at the HOUSE end -- `blk(POOL_X0, POOL_Y1-2200, POOL_FL, POOL_X1, POOL_Y1, POOL_TW-300)` = x 9500-14500, y 10300-12500, top +400 in water at +700. That is 5.0 m wide x 2.2 m front-to-back in 300 mm of water, sitting inside the cantilever zone (9500-12500). VILLA_RESEARCH.md line 253 asks for "Sun/Baja shelf: 250-350 mm deep, 1.8-2.5 m front-to-back, 2.5-4.0 m along one end... doubles as mirror surface and lounging zone, best value-for-money element in a luxury

**18.** The criticism's descriptive half is accurate, but the load-bearing claim in its EVIDENCE is factually wrong about the model, and that wrong claim is the entire argument.

WHAT THE REVIEWER GETS RIGHT (all confirmed in villa_3d.py):
- HX0/HX1 = 3000/21000, 18.0 m centred in 24.0 m. South bays 5.0 / 1.0 / 6.0 / 1.0 / 5.0 (WW 3000-8000, slot, LV 9000-15000, slot, EW 16000-21000).
- Both wings y 12500-18000, both GF-to-RF, windows at x 4200-6800 and 17200-19800 (lines 242-244) -- an exact mirror about AXIS 12000.
So yes, the south elevation is mirror-symmetric. The reviewer concedes symmetry is legitimate, so this alone is taste, not defect.

WHAT THE REVIEWER GETS WRONG -- the claim doing all the work:
"the centre bay's only distinction is that it is 1.0 m wider and its cantilever is flush wi
