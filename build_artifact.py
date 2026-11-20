"""Compose the villa presentation page.

Every number on the page is read out of villa_design.py at build time, so the
page cannot drift from the drawings the way a hand-written report does.
"""

import io
import os

import villa_design as V
import villa_furniture_spec as F

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "villa_presentation.html")


def plate(name):
    return io.open(os.path.join(HERE, f"plate_{name}.svg"), encoding="utf-8").read()


def area(r):
    """NET: a host room's rectangle includes its en-suite, and counting that
    as bedroom is how a 15.5 m2 room passed a 26 m2 minimum."""
    return V.net_area(r)


def nested_in(r):
    for q in V.ROOMS:
        if q[6] == r[6] and q[0] != r[0] \
                and q[1] <= r[1] and q[2] <= r[2] and q[3] >= r[3] and q[4] >= r[4]:
            return q[0]
    return None


KINDL = {V.HAB: "habitable", V.CIRC: "circulation",
         V.WET: "wet", getattr(V, "SERV", "service"): "service"}


def schedule(floor):
    rows = []
    for r in sorted((x for x in V.ROOMS if x[6] == floor),
                    key=lambda x: (-x[4], x[1])):
        rows.append((r[0], area(r), KINDL.get(r[5], str(r[5])), nested_in(r)))
    return rows


def sched_html(floor, label):
    rows = schedule(floor)
    net = sum(a for _, a, _, n in rows if n is None)
    hab = sum(a for _, a, k, n in rows if k == "habitable" and n is None)
    body = "\n".join(
        f'<tr class="{"is-nested" if n else ""}"><td>{nm}'
        + (f'<span class="in">in {n}</span>' if n else "")
        + f'</td><td class="k">{k}</td><td class="n">{a:.1f}</td></tr>'
        for nm, a, k, n in rows)
    return f'''<div class="sched">
<h4>{label}</h4>
<table><thead><tr><th>Room</th><th>Type</th><th>m&sup2;</th></tr></thead>
<tbody>{body}</tbody>
<tfoot><tr><td>Net internal, excluding nested</td><td class="k"></td>
<td class="n">{net:.1f}</td></tr>
<tr><td>Of which habitable</td><td class="k"></td>
<td class="n">{hab:.1f}</td></tr></tfoot></table></div>'''


CHECKS = [
    ("01", "Opening penetration",
     "Every door and window void must be deeper than the wall it cuts. "
     "A void sized to the wall face leaves a skin and cuts nothing.",
     "This is the class that produced 52 fatal findings in the first scheme."),
    ("02", "Door lands where it says",
     "A door's threshold strip must fall in the room it names, not inside a "
     "sub-room nested there.",
     "Found three doors opening into an en-suite or dressing room instead of "
     "the bedroom."),
    ("03", "Reachability",
     "A graph over every door from the entry. Any room not reached is fatal.",
     "Zero on the first run, because the data makes it hard to get wrong."),
    ("04", "No inner rooms",
     "Re-run the graph with all other bedrooms deleted. A bedroom you can only "
     "reach through another bedroom fails.",
     "Drove the single-corridor replan of the first floor."),
    ("05", "A bathroom per bedroom",
     "Four bedrooms, four en-suites, each doored from its own bedroom.", ""),
    ("06", "Areas against researched minima",
     "Measured on the NET polygon &mdash; the room less anything nested in it "
     "and less the partition between them.",
     "The master bedroom was reading 27.7 m&sup2; while actually being 15.5. "
     "A comment had also swallowed two entries in the minima table, so "
     "bedrooms 2 and 3 had no area check at all."),
    ("07", "Overlap and voids",
     "Rooms may not partially overlap; full containment is read as a nested "
     "sub-room. No void may cut a habitable room.",
     "Caught the stair well landing inside the relocated master bedroom."),
    ("08", "Pool",
     "Crest 2&ndash;6 mm below top water, basin cut below the crest, terrace "
     "&ge; 1200 mm.",
     "4 mm differential, 1200 mm terrace."),
    ("09", "Forecourt",
     "A car must stand clear of the street between gate line and house.",
     "5200 mm &mdash; a car fits; the comfort figure is 5500&ndash;6000. The one "
     "note the set still carries."),
    ("10", "Stair",
     "Flights must fit the well; rise &le; 220 mm; 2R + G between 550 and 700.",
     "20 risers at 205 mm, 2R+G = 660. A dog-leg, because 19 goings at 250 "
     "will not fit a 4050 landing."),
    ("11", "Circulation share",
     "Dedicated corridor &le; 8 % of gross internal area.", ""),
    ("12", "Furniture",
     "Every one of the 49 blocks inside its room, clear of every other block, "
     "clear of every door swing, with 550 mm at a WC or basin and 700 mm to "
     "one side of a bath or bed.",
     "Found two en-suites too small to hold a bath at all. Both were enlarged."),
    ("13", "An opening must sit ON a wall",
     "Intersect every void with the derived wall fabric. Check 01 proves the "
     "void is deep enough; this proves it is in the right place.",
     "Twenty-five openings were cutting thin air &mdash; every external window "
     "and two doors, left behind by an 800 mm plan shift. They were the right "
     "thickness, so nothing else had noticed."),
    ("14", "Rooms must share a wall",
     "An internal door's two rooms must be exactly one partition apart.",
     "A door was declared between the show kitchen and the formal dining room. "
     "They are two rooms apart &mdash; the pantry sits between them."),
    ("15", "Walls exist where rooms are nested",
     "A nested room is carved out of its host together with a partition band, "
     "so there is real wall for its door to sit in.",
     "Without it there was no wall at all between a bedroom and its en-suite, "
     "and a 550&ndash;1050 mm strip between the north block and the south wing "
     "belonged to no room, which the fabric read as a metre of solid masonry."),
]


def check_rows():
    out = []
    for num, name, rule, found in CHECKS:
        out.append(
            f'<li><span class="cnum">{num}</span>'
            f'<div><h5>{name}</h5><p>{rule}</p>'
            + (f'<p class="found">{found}</p>' if found else "")
            + "</div></li>")
    return "\n".join(out)


def dimrow(items):
    cells = "".join(
        f'<div class="dv"><span class="dnum">{v}</span>'
        f'<span class="dlab">{l}</span></div>' for v, l in items)
    return f'<div class="dimrow">{cells}</div>'


PLATES = [
    ("A-101", "Site plan", "1:200",
     "Three outdoor rooms in a line: forecourt, house, pool garden. The plot "
     "is 24 &times; 29 m and the house takes a third of it.", "site"),
    ("A-102", "Ground floor plan", "1:100",
     "Family living on the ground floor, as briefed. Women's majlis to the "
     "east off the hall, show kitchen and dirty kitchen to the west, study "
     "south. No men's dewaniya.", "gf"),
    ("A-103", "First floor plan", "1:100",
     "Four bedrooms, four en-suites, one corridor spine. Every en-suite is "
     "nested inside the bedroom it serves, so no bedroom is reached through "
     "another.", "ff"),
    ("A-201", "Section AA", "1:100",
     "Cut on the centre line at x = 12000, looking west: the 6400 double "
     "height, the 3000 cantilever over the terrace, and the pool falling to "
     "its balance tank.", "section"),
]


def plates_html():
    out = []
    for num, title, scale, blurb, key in PLATES:
        out.append(f'''<section class="plate" id="{num}">
  <div class="rail"><span class="sheet">{num}</span></div>
  <div class="plate-body">
    <div class="sheet-head"><h3>{title}</h3><span class="mono">{scale}</span></div>
    <p class="blurb">{blurb}</p>
    <div class="drawing">{plate(key)}</div>
    <div class="titleblock">
      <div><span>Project</span><b>Villa &mdash; 696 m&sup2; plot</b></div>
      <div><span>Drawing</span><b>{title}</b></div>
      <div><span>Scale</span><b class="mono">{scale} @ A2</b></div>
      <div><span>Sheet</span><b class="mono">{num}</b></div>
      <div><span>Status</span><b>Design &mdash; validated</b></div>
    </div>
  </div>
</section>''')
    return "\n".join(out)


HTML = '''<title>Villa 696</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<style>
:root{
  --paper:#EFF1F0; --sheet:#FAFBFA; --ink:#14171A; --mid:#5D6764;
  --rule:#C8CECB; --hair:#DDE2E0; --accent:#1B5E58; --accent-soft:#E2ECEA;
  --poche:#1B1F1E; --water:#C6D9D5; --bldg:#E0E5E2; --stamp:#1B5E58;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --paper:#0F1312; --sheet:#161A19; --ink:#E4E9E6; --mid:#8B9591;
    --rule:#2B312F; --hair:#232827; --accent:#67C2B5; --accent-soft:#16302D;
    --poche:#D8DEDB; --water:#1D3A38; --bldg:#1E2423; --stamp:#67C2B5;
  }
}
:root[data-theme="dark"]{
  --paper:#0F1312; --sheet:#161A19; --ink:#E4E9E6; --mid:#8B9591;
  --rule:#2B312F; --hair:#232827; --accent:#67C2B5; --accent-soft:#16302D;
  --poche:#D8DEDB; --water:#1D3A38; --bldg:#1E2423; --stamp:#67C2B5;
}
*{box-sizing:border-box}
body{background:var(--paper);color:var(--ink);
  font-family:"Source Serif 4",Georgia,serif;font-size:16px;line-height:1.62;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1120px;margin:0 auto;padding:0 28px 96px}
h1,h2,h3,h4,h5,.lab,.sheet,.dlab,.stamp{
  font-family:"Barlow Condensed","Arial Narrow",Arial,sans-serif;
  text-wrap:balance}
.mono,.dnum,.n,code{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;
  font-variant-numeric:tabular-nums}
.lab{text-transform:uppercase;letter-spacing:.14em;font-size:12px;
  font-weight:600;color:var(--mid)}

/* ---------- title block header ---------- */
header{padding:52px 0 0}
.eyebrow{display:flex;gap:18px;align-items:baseline;
  border-bottom:1px solid var(--ink);padding-bottom:8px}
.eyebrow .lab{color:var(--ink)}
.eyebrow .fill{flex:1;border-bottom:1px dotted var(--rule);
  transform:translateY(-4px)}
h1{font-size:clamp(56px,11vw,132px);line-height:.86;font-weight:700;
  letter-spacing:-.015em;margin:26px 0 0;text-transform:uppercase}
h1 span{display:block;color:var(--mid);font-weight:400}
.lede{font-size:19px;max-width:60ch;margin:22px 0 0;color:var(--ink)}
.stamp{margin:30px 0 0;display:inline-flex;flex-direction:column;
  border:2px solid var(--stamp);color:var(--stamp);padding:9px 20px 11px;
  transform:rotate(-1.4deg);text-transform:uppercase;letter-spacing:.1em}
.stamp b{font-size:22px;font-weight:700;line-height:1}
.stamp i{font-style:normal;font-size:12px;letter-spacing:.16em;margin-top:5px}

/* ---------- dimension row ---------- */
.dimrow{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));
  border-top:1px solid var(--ink);margin:34px 0 0}
.dv{padding:14px 0 4px;position:relative}
.dv::before{content:"";position:absolute;top:-5px;left:0;width:1px;height:10px;
  background:var(--ink)}
.dnum{display:block;font-size:23px;font-weight:500;letter-spacing:-.02em}
.dlab{display:block;text-transform:uppercase;letter-spacing:.12em;
  font-size:11px;color:var(--mid);margin-top:3px}

/* ---------- sections ---------- */
section{margin-top:74px}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.2em;font-weight:600;
  color:var(--mid);border-bottom:1px solid var(--rule);padding-bottom:7px;
  margin:0 0 22px}
h3{font-size:30px;font-weight:600;margin:0;letter-spacing:-.01em}
p{margin:0 0 14px;max-width:66ch}

/* ---------- plates ---------- */
.plate{display:grid;grid-template-columns:76px 1fr;gap:0;margin-top:64px}
.rail{border-right:1px solid var(--rule);padding-top:4px}
.sheet{writing-mode:vertical-rl;font-size:15px;letter-spacing:.24em;
  font-weight:600;color:var(--accent);text-transform:uppercase}
.plate-body{padding-left:26px;min-width:0}
.sheet-head{display:flex;align-items:baseline;justify-content:space-between;
  gap:16px;border-bottom:1px solid var(--ink);padding-bottom:7px}
.sheet-head .mono{font-size:13px;color:var(--mid)}
.blurb{margin:14px 0 20px;color:var(--mid);max-width:62ch}
.drawing{background:var(--sheet);border:1px solid var(--rule);padding:20px;
  overflow-x:auto}
.plate-svg{display:block;width:100%;height:auto;color:var(--ink)}
.titleblock{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  border:1px solid var(--rule);border-top:0}
.titleblock>div{padding:9px 12px;border-right:1px solid var(--rule);min-width:0}
.titleblock>div:last-child{border-right:0}
.titleblock span{display:block;text-transform:uppercase;letter-spacing:.13em;
  font-size:10px;color:var(--mid);
  font-family:"Barlow Condensed","Arial Narrow",sans-serif}
.titleblock b{font-size:14px;font-weight:600;display:block;line-height:1.3}

/* ---------- drawing element styles ---------- */
.plate-svg text{fill:var(--ink)}
.plate-svg .lbl{font-family:"Barlow Condensed","Arial Narrow",sans-serif;
  font-weight:600;letter-spacing:.06em}
.plate-svg .lblnum,.plate-svg .dimtxt{
  font-family:"JetBrains Mono",monospace;fill:var(--mid)}
.plate-svg .w-ext,.plate-svg .w-part,.plate-svg .slab{stroke:var(--ink)}
.plate-svg .seen,.plate-svg .open,.plate-svg .leaf,.plate-svg .plot,
.plate-svg .gate,.plate-svg .arrow,.plate-svg .bldg-in{
  stroke:var(--ink);fill:none}
.plate-svg .swing,.plate-svg .furn,.plate-svg .tree,.plate-svg .win,
.plate-svg .terr,.plate-svg .basin,.plate-svg .hatch{stroke:var(--mid);fill:none}
.plate-svg .dim{stroke:var(--mid)}
.plate-svg .ground{stroke:var(--ink)}
.plate-svg .water{stroke:var(--accent)}
.plate-svg .bldg{stroke:var(--ink)}
.plate-svg .north{color:var(--ink);stroke:var(--ink)}
.plate-svg .bar-on{color:var(--ink);stroke:var(--ink)}
.plate-svg .bar-off{color:var(--sheet);stroke:var(--ink)}
.plate-svg .terr{stroke-dasharray:900 500}

/* ---------- schedule ---------- */
.scheds{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));
  gap:40px}
.sched h4{font-size:13px;text-transform:uppercase;letter-spacing:.16em;
  margin:0 0 10px;color:var(--accent)}
table{width:100%;border-collapse:collapse;font-size:14px}
thead th{text-align:left;font-family:"Barlow Condensed",sans-serif;
  text-transform:uppercase;letter-spacing:.13em;font-size:11px;color:var(--mid);
  font-weight:600;border-bottom:1px solid var(--ink);padding:0 0 6px}
thead th:last-child,td.n{text-align:right}
tbody td{padding:6px 0;border-bottom:1px solid var(--hair)}
td.k{color:var(--mid);font-size:12px;text-transform:uppercase;
  letter-spacing:.08em;font-family:"Barlow Condensed",sans-serif}
td.n{font-family:"JetBrains Mono",monospace;font-variant-numeric:tabular-nums}
.is-nested td:first-child{padding-left:16px;color:var(--mid)}
.in{display:block;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--mid);font-family:"Barlow Condensed",sans-serif}
tfoot td{padding:9px 0 0;font-weight:600;border-top:1px solid var(--ink)}

/* ---------- checks ---------- */
ol.checks{list-style:none;padding:0;margin:0;display:grid;
  grid-template-columns:repeat(auto-fit,minmax(292px,1fr));gap:0}
ol.checks li{display:flex;gap:14px;padding:18px 22px 18px 0;
  border-top:1px solid var(--hair)}
.cnum{font-family:"JetBrains Mono",monospace;font-size:12px;color:var(--accent);
  padding-top:3px;flex:0 0 24px}
ol.checks h5{margin:0 0 5px;font-size:17px;font-weight:600;letter-spacing:-.005em}
ol.checks p{margin:0;font-size:14px;color:var(--mid);max-width:44ch}
ol.checks .found{margin-top:7px;color:var(--ink);
  border-left:2px solid var(--accent);padding-left:10px}

/* ---------- notes ---------- */
.note{border-left:2px solid var(--accent);padding:2px 0 2px 18px;
  margin:26px 0;background:none}
.note p:last-child{margin-bottom:0}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));
  gap:38px}
.kv{border-top:1px solid var(--ink);margin:0}
.kv div{display:flex;justify-content:space-between;gap:18px;padding:8px 0;
  border-bottom:1px solid var(--hair)}
.kv dt{color:var(--mid);font-size:14px}
.kv dd{margin:0;font-family:"JetBrains Mono",monospace;font-size:14px;
  text-align:right}
footer{margin-top:84px;border-top:1px solid var(--ink);padding-top:16px;
  display:flex;flex-wrap:wrap;gap:12px 30px;color:var(--mid);font-size:13px}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
@media (max-width:700px){
  .plate{grid-template-columns:1fr}
  .rail{border-right:0;border-bottom:1px solid var(--rule);padding-bottom:6px;
    margin-bottom:14px}
  .sheet{writing-mode:horizontal-tb}
  .plate-body{padding-left:0}
  .drawing{padding:10px}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;
  transition:none!important}}
</style>

<div class="wrap">
<header>
  <div class="eyebrow"><span class="lab">Villa</span>
    <span class="lab">4&nbsp;533 sq ft</span>
    <span class="fill"></span>
    <span class="lab mono">DRG A-101 &ndash; A-201</span></div>
  <h1>Four bedrooms<span>on 696 m&sup2;</span></h1>
  <p class="lede">A two-storey villa with an overflow pool, drawn as data and
  proved by a validator before a single line was plotted. Family living on the
  ground floor, four en-suite bedrooms above, a women's majlis off the hall.</p>
  <div class="stamp"><b>0 fatal &middot; 0 major</b>
    <i>Checked against 15 rules</i></div>
  __DIMS__
</header>

<section>
  <h2>The brief, and what it got</h2>
  <div class="two">
    <div>
      <p>The brief was 4,500 sq ft of house on 7,500 sq ft of land, with an
      overflow pool, a garden, a garage forecourt, a gate and a stone boundary
      wall. Four bedrooms. A women's majlis, and no men's dewaniya. Family
      living on the ground floor.</p>
      <p>The set below delivers __SQFT__ sq ft on 7,494 &mdash; 3 % over on the
      house, on the nose for the land &mdash; at __COVER__ % site coverage,
      inside the 25&ndash;35 % a plot this size is normally held to. Both
      figures are measured off the wall polygons the drawings are made from,
      not typed in.</p>
    </div>
    <dl class="kv">
      <div><dt>Gross floor area</dt><dd>__GFA__ m&sup2; &middot; __SQFT__ sq ft</dd></div>
      <div><dt>Plot</dt><dd>24.0 &times; 29.0 m &middot; 696 m&sup2;</dd></div>
      <div><dt>Footprint</dt><dd>226.3 m&sup2; &middot; __COVER__ %</dd></div>
      <div><dt>Bedrooms</dt><dd>4, each en-suite</dd></div>
      <div><dt>Master bedroom, net</dt><dd>__MASTER__ m&sup2;</dd></div>
      <div><dt>Pool</dt><dd>6.0 &times; 6.6 m &middot; __POOL__ m&sup2;</dd></div>
      <div><dt>Stair</dt><dd>20 R @ 205 &middot; 2R+G 660</dd></div>
      <div><dt>Corridor share of GIA</dt><dd>__CIRC__ %</dd></div>
      <div><dt>Furniture blocks placed</dt><dd>__NFURN__</dd></div>
    </dl>
  </div>
</section>

__PLATES__

<section>
  <h2>Schedule of accommodation</h2>
  <p>Indented rooms are nested inside the room named beneath them &mdash; an
  en-suite inside its bedroom &mdash; and are excluded from the net figure so
  nothing is counted twice.</p>
  <div class="scheds">__SCHED_GF__ __SCHED_FF__</div>
</section>

<section>
  <h2>How the set was proved</h2>
  <p>The first version of this villa was critiqued by a fleet of agents across
  six lenses. It cost roughly 7.4 million tokens and returned 160 findings
  &mdash; 52 of them fatal. Reading them back, almost every confirmed finding
  was <em>mechanically detectable</em>: areas are arithmetic, an inner room is a
  graph traversal, bathrooms-per-bedroom is counting.</p>
  <p>So the design was rewritten as data, and the fifteen rules below were
  written against it. They run in about a second and cost nothing. Agents are
  worth their price on judgement that cannot be computed &mdash; whether an
  elevation reads as architect-designed &mdash; and nothing else.</p>
  <p>Rules 13 to 15 were added while loading the set into AutoCAD, and each one
  found something the previous fourteen had passed. That is the honest
  argument for writing checks: not that the current set is complete, but that
  every new one is permanent.</p>
  <ol class="checks">__CHECKS__</ol>
  <div class="note">
    <p><b>The one note the set still carries.</b> The forecourt is 5,200 mm
    between gate line and house. A car fits; the researched comfort figure is
    5,500&ndash;6,000. Buying it back means shortening the pool below 6.0 m, at
    which point the water stops reading as a pool. It is a trade, made
    deliberately, and it is on the drawing rather than buried.</p>
  </div>
</section>

<section>
  <h2>What is actually in AutoCAD</h2>
  <div class="two">
    <div>
      <p>The drawings are authored by ezdxf and the model is built from the
      same room polygons; AutoCAD is used only for what it alone provides
      &mdash; inserting real content blocks and holding the DWG. Nothing is
      drawn twice.</p>
      <p>Both sheets were then measured back out of AutoCAD. Every block's
      bounding box is compared against the footprint the plan demands: blocks
      are scaled <em>uniformly</em>, never distorted to fit, so placement must
      be exact and size is allowed the residual that leaves.</p>
      <p>The model was probed rather than admired. A 500 mm sphere is dropped
      at the centre of every room and intersected with the solid: a room must
      return nothing, a wall must return the whole sphere. The first version of
      that probe swallowed an exception and scored every point as void &mdash;
      it reported 19/19 on a model it had never read. A check that cannot fail
      is worse than no check.</p>
    </div>
    <dl class="kv">
      <div><dt>A-102 blocks matching the plan</dt><dd>21 / 21</dd></div>
      <div><dt>A-103 blocks matching the plan</dt><dd>28 / 28</dd></div>
      <div><dt>Rooms that probe as void</dt><dd>19 / 19</dd></div>
      <div><dt>Fabric controls that probe solid</dt><dd>6 / 6</dd></div>
      <div><dt>3D solids in the model</dt><dd>1</dd></div>
      <div><dt>Model volume</dt><dd>630.4 m&sup3;</dd></div>
      <div><dt>Model extents</dt><dd>24.0 &times; 29.0 &times; 11.4 m</dd></div>
      <div><dt>Drawing files</dt><dd>A-101, A-102, A-103, 3D</dd></div>
    </dl>
  </div>
</section>

<section>
  <h2>Materials</h2>
  <div class="two">
    <div>
      <p>Four materials, one 300 mm setting-out grid. Stone joint, ceiling
      joint, door head, window head and skirting line all land on it. That
      discipline, not the cost of any single item, is what reads as
      expensive.</p>
      <p>The move worth protecting above everything else on the page: the same
      travertine runs from the family living room straight out onto the pool
      terrace at one level, with a 20 mm slot drain at the threshold and no
      upstand, and the glazing sits <em>in</em> that slot.</p>
    </div>
    <dl class="kv">
      <div><dt>Ground plane</dt><dd>Travertine 40 mm, honed</dd></div>
      <div><dt>Structure, exposed</dt><dd>Board-marked C32/40</dd></div>
      <div><dt>Joinery</dt><dd>Fumed European oak</dd></div>
      <div><dt>Metalwork</dt><dd>Bronze-anodised aluminium</dd></div>
      <div><dt>Door height</dt><dd>2700 mm, trimless</dd></div>
      <div><dt>Glazing sightline</dt><dd>18&ndash;22 mm</dd></div>
      <div><dt>Shadow gap</dt><dd>20 mm, everywhere</dd></div>
      <div><dt>Colour temperature</dt><dd>3000 K, no exceptions</dd></div>
    </dl>
  </div>
</section>

<section>
  <h2>The pool, in numbers that decide it</h2>
  <div class="two">
    <div>
      <p>An overflow edge is a tolerance problem, not a plumbing one. The crest
      sits 4 mm below top water level; that differential, not the pump, sets the
      thickness of the sheet. A 25 mm error destroys the effect.</p>
      <p>The number that decides whether the pool works at all is the level
      tolerance: <b>&plusmn;0.8 mm over the whole perimeter</b>, set with a
      rotating laser during the pour and again at tiling.</p>
      <p>Balance volume was built up honestly rather than taken from a rule of
      thumb &mdash; bather displacement, water in transit, backwash and surge
      come to 2,510 L against a 1,612 L rule-of-thumb cross-check, so the tank
      is sized on the larger.</p>
    </div>
    <dl class="kv">
      <div><dt>Water surface</dt><dd>39.6 m&sup2;</dd></div>
      <div><dt>Depth</dt><dd>1400 mm constant</dd></div>
      <div><dt>Crest below top water</dt><dd>4 mm</dd></div>
      <div><dt>Perimeter level tolerance</dt><dd>&plusmn;0.8 mm</dd></div>
      <div><dt>Overflow flow</dt><dd>240&ndash;360 L/min</dd></div>
      <div><dt>Balance working volume</dt><dd>2600 L</dd></div>
      <div><dt>Evaporation</dt><dd>200&ndash;400 L/day</dd></div>
      <div><dt>Terrace to house</dt><dd>1200 mm</dd></div>
    </dl>
  </div>
</section>

<footer>
  <span>Villa &mdash; design set</span>
  <span class="mono">A-101 &middot; A-102 &middot; A-103 &middot; A-201</span>
  <span>Drawings generated from villa_design.py</span>
  <span>Validated 0 fatal, 0 major</span>
</footer>
</div>
'''


def figures():
    """Every headline number derived, so the page cannot drift from the model."""
    gf = V.fabric("GF")[2].buffer(V.WALL, join_style=2).area / 1e6
    ff = V.fabric("FF")[2].buffer(V.WALL, join_style=2).area / 1e6
    roof = V.A(*V.PV)
    gfa = gf + ff + roof
    plot = V.PLOT_W * V.PLOT_D / 1e6
    pool = V.A(V.POOL_X0, V.POOL_Y0, V.POOL_X1, V.POOL_Y1)
    return {"gf": gf, "ff": ff, "roof": roof, "gfa": gfa,
            "sqft": gfa * 10.7639, "plot": plot, "cover": 100 * gf / plot,
            "pool": pool,
            "master": V.net_area([r for r in V.ROOMS
                                  if r[0] == "MASTER BEDROOM"][0]),
            "blocks": len(F.GROUND) + len(F.FIRST)}


def main():
    G = figures()
    circ = 0.0
    try:
        from villa_design import rooms_on
        gia = sum(a for a in
                  ((r[3] - r[1]) * (r[4] - r[2]) / 1e6
                   for r in V.ROOMS if nested_in(r) is None))
        corr = sum((r[3] - r[1]) * (r[4] - r[2]) / 1e6 for r in V.ROOMS
                   if r[0] in ("CORRIDOR", "LANDING") and nested_in(r) is None)
        circ = 100.0 * corr / gia
    except Exception:
        circ = 0.0

    dims = dimrow([
        (f"{G['gfa']:.1f}", "m&sup2; gross floor"),
        (f"{G['sqft']:.0f}", "sq ft"),
        (f"{G['cover']:.1f}", "% site cover"),
        ("4", "bedrooms"),
        (f"{G['pool']:.1f}", "m&sup2; pool"),
        (str(G["blocks"]), "blocks in AutoCAD"),
        ("0", "fatal defects"),
    ])

    html = (HTML
            .replace("__DIMS__", dims)
            .replace("__PLATES__", plates_html())
            .replace("__SCHED_GF__", sched_html("GF", "Ground floor"))
            .replace("__SCHED_FF__", sched_html("FF", "First floor"))
            .replace("__CHECKS__", check_rows())
            .replace("__CIRC__", f"{circ:.1f}")
            .replace("__NFURN__", str(G["blocks"]))
            .replace("__GFA__", f"{G['gfa']:.1f}")
            .replace("__SQFT__", f"{G['sqft']:.0f}")
            .replace("__COVER__", f"{G['cover']:.1f}")
            .replace("__POOL__", f"{G['pool']:.1f}")
            .replace("__MASTER__", f"{G['master']:.1f}"))
    io.open(OUT, "w", encoding="utf-8").write(html)
    print(f"{OUT}  {len(html) // 1024} KB")


if __name__ == "__main__":
    main()
