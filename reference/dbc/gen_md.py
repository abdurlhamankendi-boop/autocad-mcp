"""Write dubai-villa-rules.md from dubai_villa_rules.json plus the audit findings."""
import json

SRC = r"C:\Users\lsire\.claude\skills\architectural-cad\references\dubai_villa_rules.json"
OUT = r"C:\Users\lsire\.claude\skills\architectural-cad\references\dubai-villa-rules.md"

d = json.load(open(SRC, encoding="utf-8"))
rules = d["rules"]

ORDER = [
    ("scope", "Scope"), ("accessibility", "Accessibility"), ("site_levels", "Site levels"),
    ("height", "Height and storeys"), ("setbacks", "Setbacks"), ("projections", "Projections"),
    ("annex", "Annexes"), ("areas", "GA, GFA and coverage"), ("roof", "Roof and roof structures"),
    ("basement", "Basements"), ("room_sizes", "Room sizes"), ("ceiling_heights", "Clear heights"),
    ("doors", "Doors"), ("windows_daylight", "Windows and daylight"), ("circulation", "Corridors and ramps"),
    ("stairs", "Stairs"), ("handrails", "Handrails"), ("guards", "Guards and parapets"),
    ("glazing_safety", "Glazing safety"), ("vehicle_access", "Site and vehicle access"),
    ("parking", "Parking and garages"),
    ("sanitary", "Sanitary"), ("ventilation", "Ventilation"), ("pool", "Private swimming pool"),
    ("waste", "Waste storage"), ("envelope_energy", "Envelope and energy"), ("fire", "Fire"),
    ("drainage", "Rainwater, sewage and soakaways"), ("utilities", "Utilities: metering, water storage, plant"),
    ("boundary_walls", "Boundary walls"),
]
assert {c for c, _ in ORDER} == {r["category"] for r in rules}, "category missing from ORDER"


def ref_cell(r):
    s = f"{r['dbc_ref']}, p.{r['pdf_page']} / {r['printed_page']}"
    extra = []
    for q in r.get("also_quotes", []):
        tag = f"p.{q['pdf_page']} / {q['printed_page']}"
        if q["pdf_page"] != r["pdf_page"] and tag not in extra:
            extra.append(tag)
    if extra:
        s += " (also " + ", ".join(extra) + ")"
    return s


def check_cell(r):
    c = r["villa_design_check"]
    s = c["status"]
    if c["check"]:
        s += f" ({c['check']})" if not c["check"].isdigit() and "/" not in c["check"] else f" #{c['check']}"
    if c["note"]:
        s += f": {c['note']}"
    return s.replace("|", "/")


def design_cell(r):
    c = r["current_design"]
    s = c["status"]
    if c["note"]:
        s += f": {c['note']}"
    return s.replace("|", "/")


L = []
w = L.append
w("# Dubai Building Code 2021: rules for a private villa")
w("")
w(f"Source: *{d['source']['title']}*, {d['source']['pages']} pages, "
  f"[{d['source']['url'].split('/')[-1]}]({d['source']['url']}), local copy `{d['source']['file']}`, "
  f"retrieved {d['source']['retrieved']}.")
w("")
w("The machine-readable source is `dubai_villa_rules.json` in this folder: "
  f"{len(rules)} rules. Each has numeric `values` with units, the `dbc_ref`, `pdf_page` "
  "(1-based index into the PDF) and `printed_page` (the page label), plus a verbatim quote. Some rules carry "
  "`also_quotes` from further pages and a `note`. Every quote, including the `also_quotes`, was machine-checked "
  "against its page by `autocad-mcp/reference/dbc/build_rules.py`. A `note` records a reading the DBC does "
  "not state outright, a discrepancy in the DBC, or a value read from a figure drawing whose dimension text is "
  "not in the PDF text layer (K-PARK-03 door widths, K-MTR-01 letter meanings). "
  "Page citations below use the form **p.PDF / printed**.")
w("")
w("How the code is organised:")
w("")
w("- **Part K (pdf 671-842) is standalone for villas** (K.4, p.696 / K 26). Rules from Parts B and C apply "
  "only where Part K cross-references them. Part C states it does not apply to villas (p.158 / C 8).")
w("- **The DCR or affection plan overrides Part K** on setbacks, height, projections and parking "
  "(K.5.1, K.5.2.2, K.5.2.4, K.5.2.5.1, K.5.6.4). Part K's numbers are the defaults and minimums.")
w("- In the \"villa_design.py\" column, `#N` is the check number in `validate()` / `checks_brief()`. "
  "**new check needed** means the rule can be computed from the design data, though some checks first need "
  "a constant declared, such as ROAD_EDGE, a stair width or the pool barrier. **not checkable** means the rule is "
  "a specification, MEP or road-context item that the plan data does not hold.")
w("")
w("## Rules by category, and how villa_design.py checks them")
for cat, title in ORDER:
    rs = [r for r in rules if r["category"] == cat]
    w("")
    w(f"### {title}")
    w("")
    w("| ID | Rule | DBC ref, page | villa_design.py | Current design |")
    w("|---|---|---|---|---|")
    for r in rs:
        rule = r["rule"] + (f" *({r['condition']})*" if r["condition"] else "")
        w(f"| {r['id']} | {rule.replace('|', '/')} | {ref_cell(r)} "
          f"| {check_cell(r)} | {design_cell(r)} |")
    notes = [r for r in rs if r.get("note")]
    if notes:
        w("")
        for r in notes:
            w(f"- **{r['id']} note:** {r['note']}")

w("")
w("## Current design vs DBC")
w("")
w("Constants as read from `autocad-mcp/villa_design.py` on 2026-09-26. The metrics came from "
  "`reference/dbc/dbc_audit.py`, which imports the module read-only. Each item below is a non-compliance of "
  "the current constants. Items marked *conditional* depend on something the design does not yet declare. "
  "Items marked *interpretation* rest on a reading the DBC does not state outright; the reading is given.")
w("")
FAILS = [
    ("Stair riser 205 mm > 180 mm max",
     "FF2FF 4100 / RISERS 20 = 205. The DBC range is 100-180 mm, so at least 23 risers of 178.3 mm are needed. "
     "Check 9 passes it because it allows 220 mm and applies a 2R+G 550-700 rule, which the DBC does not contain.",
     "K.5.5.2.3, p.711 / K 41"),
    ("Stair tread 250 mm < 280 mm min",
     "STAIR_GOING = 250.", "K.5.5.2.3, p.711 / K 41"),
    ("Stair well too short for a compliant dog-leg",
     "With 23 risers the longest flight has 12 risers (11 treads x 280 = 3080 mm), plus a landing of at least 1000 mm, "
     "giving 4080 mm. The well is 3400 deep (STAIR y 19200-22600). Its 2100 width also leaves exactly "
     "2 x 1050 for two flights of at least 1000 mm each, with no room for a gap or a central wall.",
     "K.5.5.2.2 p.710 / K 40; K.5.5.2.4 p.712 / K 42"),
    ("Roof parapet 1100 mm < 1200 mm guard (conditional: accessible roof)",
     "PARAPET = 1100. The design declares an RF level with a roof pavilion, and accessible roofs need "
     "K.5.2.5.2 guards of at least 1200 mm.",
     "K.5.2.8.3 p.705 / K 35; K.5.2.5.2 p.701 / K 31"),
    ("Pool too deep at its shallowest point",
     "POOL_TW - POOL_FL = 1400 mm at constant depth. The shallow area must be 850-1200 mm at its shallowest point.",
     "K.5.8.2.2, p.722 / K 52"),
    ("No continuous 1.2 m pool deck",
     "The south edge is the weir (400) and catch basin (y 1600-2800), so there is no walkway. On the north, "
     "TERRACE = 1200 is measured from the water to the facade and includes the 400 mm pool wall, so the deck "
     "excluding coping is about 800 mm. Check 7 tests only the north TERRACE >= 1200.",
     "K.5.8.2.4, p.723 / K 53"),
    ("Operable windows beside the pool with sill 900 < 1200 mm (conditional: operable)",
     "The GF south windows share the pool terrace: Family Living (x 9600-14400, facing the water 1.2 m away), "
     "Formal Dining and Study. WIN_SILL = 900 for all windows. Either make them fixed or raise the sill "
     "to 1200.", "K.5.8.2.1, p.722 / K 52"),
    ("Fins inside the west side setback",
     "FIN_ARRAYS x 2300-2750, z 0-8700: 2.3 m from the west boundary against the 3 m SB_SIDE. They project "
     "700 mm from the wall face and start at ground. The DBC allows only fencing, landscape and hardscape, basements, "
     "pergolas and light parking shades, internal roads, parking and annexes in the setback. Decorative projections "
     "are limited to 300 mm and must be at least 2.7 m above FFL, and projections must be at least 3 m from a "
     "neighbouring plot. Check 19 misses this because it tests room outlines only.",
     "K.2.2 p.674 / K 4; K.5.2.4 p.698 / K 28 and p.700 / K 30; K.5.2.5.1 p.700 / K 30"),
    ("Forecourt parking 4650 mm deep < 5.5 m (interpretation: conservative reading)",
     "The GF north face is at y 24000 and the boundary wall inner face at 28650. Table K.7 gives an open single "
     "garage 3.0 x 5.5 m. Applying it to an uncovered forecourt bay is a conservative reading, not a stated rule: "
     "K.5.6.4 requires \"parking areas (covered or uncovered)\" but sets no bay size for a villa with two bays or "
     "fewer, and Table K.7 is headed \"Garage minimum dimensions\". The reading is defensible because the K.2.2 "
     "Garage definition covers structures \"which may or may not include a roof\" (p.675 / K 5), and Figure K.39 "
     "draws the open garage with dashed sides. Part B's bays (5.0 m in plots under 30 m) apply only above two bays "
     "(K.5.6.4), though 4650 would fail them too. Check 8 already reports FATAL, but against a 5000 threshold, "
     "and the porch overlaps the house.",
     "K.5.6.4 p.720 / K 50; Table K.7 and Figure K.39, p.721 / K 51; K.2.2 p.675 / K 5 (B.7.2.4 p.86 / B 66)"),
    ("Roof pavilion breaks the roof-structure setback (conditional: if built)",
     "PV y1 = 23600, while the FF north face (roof edge) is at 23200. The pavilion overhangs by 400 mm instead of "
     "standing 1.5 m back, and it is not a stair or lift room, so the exemption does not apply. "
     "Its 16% of roof area is within the 50% cap.",
     "K.5.2.8.3, p.705 / K 35"),
]
for i, (t, body, ref) in enumerate(FAILS, 1):
    w(f"{i}. **{t}.** {body} ({ref})")
w("")
w("Not yet verifiable, because the design has no data for them. Each needs a declaration and then a check:")
w("")
w("- **Guards at raised landings and voids.** The entrance and service landings are 900 mm above ground, "
  "more than the 760 mm trigger, and so are the FF edges of the double-height volume, the stair void and the "
  "sunken court. All need guards of at least 1200 mm (K.5.2.5.2 p.701 / K 31; K.5.5.2.6 p.714 / K 44).")
w("- **Gate level.** No road-edge level is declared, and STREET = 0 doubles as the forecourt level. The gate must "
  "be at least 300 mm above the road edge (K.5.2.1 p.697 / K 27). Height is measured from the same datum "
  "(K.5.2.2).")
w("- **Pool barrier.** No fence is modelled. If the house and the 2.4 m boundary wall are the barrier, every door "
  "into the pool garden needs an audio alarm or a self-closing, self-latching leaf (K.5.8.2.3 p.723 / K 53).")
w("- **Housekeeper rooms, waste store and bathroom fixture clearances.** These rooms are not placed yet. Once "
  "they are: maid and driver rooms need at least 5.5 m2, 2.1 m and 8% glazing; provide two 240 l bins with "
  "150 mm clearances; and WCs and basins need 400 mm to the side wall, 750 mm between centres and 750 mm "
  "clear in front (p.706, p.709, p.722, p.724-725).")
w("- **Pool plant room (required, because the pool is built).** The pool's treatment water must come from a "
  "dedicated break tank with a booster pump set, both in a pool filtration plantroom (K.10.2.3.2 p.824 / K 154). "
  "Backwash goes to the public drain where approved, or else through an attenuation tank, and never to a septic "
  "tank (K.10.3.5, K.10.3.6(c) p.837 / K 167). REQUIRED lists one 4 m2 \"plant\" room, and it is not placed.")
w("- **Cold-water tank and pump room.** Storage for at least 24 h of demand, in a conditioned space that is not "
  "exposed to the outdoor climate (K.10.2.5 p.825-826 / K 155-156). The pump set goes beside the tank in an "
  "internal room (K.10.2.4 p.824 / K 154). If the tank room goes on the roof, it is a roof structure and so "
  "falls under the 50% cap and the 1.5 m setback (K-ROOF-02/03). That last point is a reading of K.5.2.8.3, "
  "not a DBC statement.")
w("- **Electricity meter cabinet in the boundary wall.** DEWA metering sits recessed in the compound wall: "
  "600 x 800 mm plus a 250 mm gland box, 200 mm deep, bottom at least 800 mm and top at most 1,800 mm above "
  "ground. It must be at least 2 m from the water meter (K.9.1.5.1 and Figure K.69, p.770-771 / K 100-101). "
  "The 2.4 m wall, which check 8 takes as 350 mm thick, can take it, but no cabinet is placed.")
w("- **Roof and court drainage.** Roofs fall between 1/70 and 1/50, and a parapet roof needs emergency "
  "overflows (K.10.3.4.3 p.837 / K 167). The roof is modelled flat with PARAPET 1100 and no scuppers. The "
  "sunken court (1.0 x 5.0 m = 5 m2, open to sky) is under the 16 m2 limit, so it needs a floor drain "
  "connected to a gully or stack. Rainwater pipes discharge above ground, never to the sewer, and where "
  "possible at least 2 m from the building (same page).")
w("- **Semi-basement (conditional: BS_* is declared at FL -2800 with no rooms).** If it is built, it needs a "
  "sump pit at least 1 m below the lowest inlet with duty/standby pumps (K.10.3.3.3 p.834 / K 164), "
  "self-contained emergency lighting (K.10.5.1 p.841 / K 171), and a 1,000 mm enclosed exit stair (K-BSMT-04).")
w("- **Sewage (conditional: no public sewer).** A holding tank of at least 25 m3. RC tanks at least 1 m from "
  "buildings and boundary walls (brick tanks 3 m), at least 3 m from any water tank, and outside the 5.5 m "
  "vehicular-access setback. Soakaways at least 3 m from footings and boundary walls and 1 m from the septic "
  "tank (K.10.3.6-K.10.3.7, p.837-840 / K 167-170).")
w("- **Windows facing neighbours.** W and E windows stand exactly 3.0 m from the side boundaries, which meets "
  "the setback. They may face a neighbouring plot only if the external fire-spread limits are also met. Those "
  "limits are in UAE FLSC Ch. 1, not in the DBC. K.5.2.4 also requires villas to be separated or to have "
  "fire-rated exterior walls (K.5.4.2.1(d) p.709 / K 39; K.5.2.4 p.698 / K 28). The design does not say which "
  "boundaries are neighbours.")
w("- **Full-height glazing.** There is no SLIDE opening today. A future full-height panel on FF, or at GF over "
  "a drop of more than 760 mm with no landing, must contain over the whole panel because it spans 800 mm "
  "(K.7.6.2 p.739-740 / K 69-70). Any skylight or glazed roof must be laminated with post-breakage containment "
  "(K.7.6.3 p.740 / K 70).")
w("")
w("Compliant as it stands:")
w("")
w("- **Setbacks:** 5/3/3 m for the rooms, against Table K.1's 3 m.")
w("- **Height:** 12.7 m to the pavilion top, under the 16 m cap. The design has 2 storeys.")
w("- **Clear heights:** 3.6 m on GF, 3.2 m on FF and 3.0 m in the annex, against the 2.7 m minimum.")
w("- **Room sizes:** every habitable room is at least 16.3 m2 and has a clear rectangle of at least 3.2 m, "
  "against 10.5 m2 and 3 m.")
w("- **Kitchens:** the dirty kitchen is 7.1 m2 with a 2.55 m minimum dimension, against 5.4 m2 and 1.8 m.")
w("- **Doors:** clear widths are about 950 mm or more, and about 850 mm into wet rooms, against 915 and 710 mm.")
w("- **Glazing:** at least 16% of floor area in every habitable room, against 10%.")
w("- **Window sills:** 900 mm, which is the minimum.")
w("- **Corridor:** 1.7 m wide, against 1.0 m.")
w("- **External steps:** 180 mm risers, 300 mm treads and 1200 mm landings.")
w("- **Other:** the GF sprinkler trigger is not reached (GA 193 against 1500 m2), and the boundary wall is 2.4 m, "
  "under Part B's 3 m cap.")
w("")
w("## DBC K.5.2.3 annex citation: confirmed, with two corrections")
w("")
w("The citation is to the right clause, K.5.2.3 \"Annexes\", on **p.698 / K 28**. It appears in the "
  "villa_design.py constants comment (lines 39-41) and in check 18 (lines 1077-1090). The annex may stand on "
  "the plot boundary: \"It is permitted to build annexes to residential villas/townhouses without any "
  "setback\". The clause's three numbers are also right:")
w("")
w("- (a) at least **1.5 m** between the annex and the main villa;")
w("- (d) a maximum height of **5.5 m**;")
w("- (c) an area of at most **60%** of the main building's GA.")
w("")
w("Two corrections to check 18:")
w("")
w("1. **Wrong basis for the 60% cap.** K.5.2.3(c) says the annex area \"shall not exceed 60% of the main "
  "building gross area (GA)\". GA is measured *inside* the exterior walls (K.5.2.6, p.702 / K 32, and the K.2.2 "
  "definition, p.675 / K 5). Check 18 instead compares external outlines at line 1087, "
  "`ax.area > 0.6 * villa.area` with `villa = outline('GF')`, which gives a cap of 135.8 m2 today. That basis "
  "is wrong whichever way GA is read.")
w("")
w("   **What the cap should be is a reading, not a certainty.** Neither K.5.2.6 nor the K.2.2 definition says "
  "how GA aggregates over several floors, and the DBC does not say how the annex's own area is measured. The "
  "*likely* reading sums the villa's GA over its floors, 193.3 (GF) + 142.5 (FF) = 335.8 m2, which gives a cap "
  "of about **201 m2**, with the annex measured the same way (its own GA inside its exterior walls). The "
  "conservative bound takes GF GA only, 0.6 x 193.3 = **116 m2**. A check should use 201 m2 and flag an "
  "annex between 116 and 201 m2 as depending on that reading.")
w("2. **Missing condition.** K.5.2.3(b) requires an annex either to be \"attached to plot boundary\" or to "
  "follow the K.5.2.4 building setbacks. Check 18 only tests that the annex lies inside the plot (line 1089), "
  "so it would pass an annex floating 1 m off the boundary.")
w("")
w("Related points:")
w("")
w("- The DBC gives no datum for the 5.5 m annex height. K.5.2.2 measures building heights from the approved road "
  "edge level, so measure from ROAD_EDGE, not STREET. The current annex, 150 + 3000 + 500 + 1100 = 4750 mm, "
  "passes either way.")
w("- The 1.5 m separation also appears in K.5.2.4 as a general rule for any two buildings on a standalone-villa "
  "plot (p.698 / K 28).")
w("- Plot coverage counts annexes (K.5.2.7, p.703 / K 33).")
w("")
w("## Check changes, in priority order")
w("")
w("1. **Check 9:** replace `rise > 220` and 2R+G with riser 100-180 and tread of at least 280 (K-STR-03, K-STR-05). "
  "Add a declared stair width of at least 1000 (K-STR-01). Replace the 1100 half-landing with a landing of at "
  "least 1000 that is no narrower than the stair (K-STR-09).")
w("2. **Check 1:** test door *clear* width, at least 915 generally and at least 710 for bathrooms and WCs, "
  "instead of the 700-1800 structural opening (K-DOOR-01, K-DOOR-02).")
w("3. **Check 19:** include FIN_ARRAYS, SHADES and roof structures, not just room outlines (K-SB-04, K-SB-05, "
  "K-PRJ-01 to K-PRJ-04).")
w("4. **Check 7:** add pool depth 850-1200 at the shallow point, a 1.2 m deck all round excluding coping, "
  "a sill of at least 1200 for operable windows beside the pool, and a declared barrier (K-POOL-01 to K-POOL-09).")
w("5. **Check 18:** use the GA basis, with a cap of 0.6 x summed villa GA (about 201 m2) and a flag between "
  "116 and 201 m2 where the result depends on the reading. Add the boundary-or-setback test (K-ANX-03, K-ANX-04).")
w("6. **Check 8:** raise the parking depth to 5500. This is the conservative Table K.7 reading; K.5.6.4 gives "
  "no size for two or fewer uncovered bays (K-PARK-03).")
w("7. **New checks:**")
w("   - Guard and parapet height of at least 1200 wherever the drop exceeds 760 (K-GRD-01, K-GRD-02, K-ROOF-01, "
  "K-SGR-01).")
w("   - Roof structures: at most 50% of the roof and set back 1.5 m (K-ROOF-02, K-ROOF-03).")
w("   - A 3 m clear dimension for habitable rooms (K-ROOM-01).")
w("   - Glazing of at least 10% of floor area (K-WIN-01).")
w("   - Clear heights of at least 2.7 and 2.3 m (K-CH-01, K-CH-02).")
w("   - A corridor width of at least 1.0 m (K-COR-01).")
w("   - Gate and height datums (K-GATE-01, K-HGT-01).")
w("   - The WWR band that sets the glazing specification (K-ENV-02).")
w("   - Fixture clearances in villa_furniture_spec (K-SAN-03 to K-SAN-05).")
w("   - Whole-panel containment for any SLIDE on FF, or at GF over a drop of more than 760 mm (K-GLZ-01).")
w("8. **New declarations, then checks:**")
w("   - A pool plant room with break tank and booster set (K-POOL-11).")
w("   - A conditioned tank and pump room (K-WTR-01, K-WTR-02); if it is on the roof, include it in the 50% and "
  "1.5 m roof checks.")
w("   - A meter cabinet in the boundary wall, at least 2 m from the water meter (K-MTR-01, K-MTR-02).")
w("   - Roof falls, parapet overflows and a floor drain in the sunken court (K-RAIN-01 to K-RAIN-03).")
w("   - Sewer connection or septic/soakaway, with their distances (K-SEP-01, K-SEP-02, K-SOAK-01).")
w("   - If BS_* is built: a sump pit and emergency lighting (K-BSMT-05, K-BSMT-06).")
w("   - Which boundaries are neighbours, for K-WIN-09 and K-PRJ-04.")
w("")
w("## Not covered by the DBC")
w("")
w("A search of all 843 pages found no rule on these topics. Where the brief's own numbers, such as 2R+G or "
  "the 0.6 x height shading depth, stand in for them, label them as practice, not code.")
w("")
for n in d["not_covered"]:
    w(f"- {n}")
w("")
open(OUT, "w", encoding="utf-8").write("\n".join(L))
print("written", OUT, len(L), "lines")
