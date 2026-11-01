"""Parse full ISD station-years -> npz: METAR/SPECI obs (utc s, temp F int) and SOD daily max/min F (LST date).
Usage: python -I isd_parse.py ISD_RAW_DIR OUT_DIR"""
import sys, os, gzip, re, datetime as dt, numpy as np
STATIONS = {"NY": ("725053-94728", -5), "CHI": ("725340-14819", -6), "AUS": ("722540-13904", -6), "MIA": ("722020-12839", -5)}
RE_MAX = re.compile(r"24 HR MAX TEMP \(F\):(.{3})")
RE_MIN = re.compile(r"24 HR MIN TEMP \(F\):(.{3})")
def parse(raw, out):
    for city, (sid, off) in STATIONS.items():
        ts, tf, sod = [], [], {}
        for y in range(2005, 2025):
            p = f"{raw}/{sid}-{y}.gz"
            if not os.path.exists(p): continue
            with gzip.open(p, "rt", errors="replace") as f:
                for line in f:
                    if len(line) < 93: continue
                    rtype = line[41:46]
                    t = dt.datetime.strptime(line[15:27], "%Y%m%d%H%M").replace(tzinfo=dt.timezone.utc)
                    if rtype.startswith("SOD"):
                        m = RE_MAX.search(line); n = RE_MIN.search(line)
                        lst = (t + dt.timedelta(hours=off)).date()
                        try:
                            mx = int(m.group(1).strip()) if m else None
                            mn = int(n.group(1).strip()) if n else -999
                        except ValueError:
                            mx = None
                        if mx is not None: sod[lst.isoformat()] = (mx, mn)
                        continue
                    if rtype not in ("FM-15", "FM-16"): continue
                    tc, q = line[87:92], line[92]
                    if tc == "+9999" or q not in "01459ACIMPRU": continue
                    c = int(tc) / 10.0
                    ts.append(int(t.timestamp())); tf.append(int(np.floor(c * 1.8 + 32 + 0.5)))
        o = np.argsort(ts, kind="stable")
        days = sorted(sod)
        np.savez(f"{out}/isd_{city}.npz", ts=np.array(ts, np.int64)[o], tf=np.array(tf, np.int16)[o],
                 sod_day=np.array(days), sod_max=np.array([sod[d][0] for d in days], np.int16),
                 sod_min=np.array([sod[d][1] for d in days], np.int16), off=off)
        print(city, len(ts), "obs", len(days), "SOD days", days[:1], days[-1:])
if __name__ == "__main__":
    parse(sys.argv[1], sys.argv[2])
