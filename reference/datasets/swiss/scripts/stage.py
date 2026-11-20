"""Stream geometries.csv out of the zip into a slim SQLite table (no walls/railings/columns)."""
import zipfile, io, csv, sqlite3, os, sys, time
csv.field_size_limit(1 << 30)
ZIP = r"C:\Users\lsire\autocad-mcp\reference\datasets\swiss\swiss-dwellings-v3.0.0_geometries.zip"
DB = sys.argv[1]
if os.path.exists(DB):
    os.remove(DB)
con = sqlite3.connect(DB)
con.execute("PRAGMA journal_mode=OFF"); con.execute("PRAGMA synchronous=OFF")
con.execute("""CREATE TABLE g(apt TEXT, unit TEXT, floor TEXT, plan TEXT, area_id TEXT, et TEXT, st TEXT,
               usage TEXT, geom TEXT, elev REAL, height REAL)""")
z = zipfile.ZipFile(ZIP)
fh = io.TextIOWrapper(z.open(z.infolist()[0]), encoding='utf-8', newline='')
r = csv.reader(fh)
hdr = next(r)
ix = {h: i for i, h in enumerate(hdr)}
KEEP_OPEN = {'DOOR', 'ENTRANCE_DOOR', 'WINDOW'}
KEEP_FEAT = {'TOILET', 'SHOWER', 'BATHTUB', 'SINK', 'KITCHEN', 'STAIRS', 'WASHING_MACHINE', 'ELEVATOR'}
buf = []; n = 0; t0 = time.time()
for row in r:
    apt = row[ix['apartment_id']]
    if not apt:
        continue
    et = row[ix['entity_type']]; st = row[ix['entity_subtype']]
    if et == 'separator':
        continue
    if et == 'opening' and st not in KEEP_OPEN:
        continue
    if et == 'feature' and st not in KEEP_FEAT:
        continue
    def f(x):
        try: return float(x)
        except ValueError: return None
    # apartment_id is only unique per site (Zenodo record description) -> key on site_id:apartment_id
    buf.append((row[ix['site_id']] + ':' + apt, row[ix['unit_id']], row[ix['floor_id']], row[ix['plan_id']], row[ix['area_id']], et, st,
                row[ix['unit_usage']], row[ix['geometry']], f(row[ix['elevation']]), f(row[ix['height']])))
    if len(buf) >= 50000:
        con.executemany("INSERT INTO g VALUES (?,?,?,?,?,?,?,?,?,?,?)", buf); n += len(buf); buf.clear()
con.executemany("INSERT INTO g VALUES (?,?,?,?,?,?,?,?,?,?,?)", buf); n += len(buf)
con.commit()
con.execute("CREATE INDEX ix_apt ON g(apt)")
con.commit()
print('rows staged', n, 'secs', round(time.time() - t0, 1))
