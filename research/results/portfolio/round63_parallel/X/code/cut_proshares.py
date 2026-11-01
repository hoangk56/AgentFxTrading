"""Copy ProShares UVXY / SVXY / VIXY / VIXM NAV-AUM history (round 34 E raw download) cut at < 2025-01-01.
Output: research/data/cboe_vx/proshares/<T>.csv with date (ISO), nav, shares_000, aum. Nothing after 2024 is kept."""
import csv, datetime as dt, sys
SRC = sys.argv[1]
DST = '/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/cboe_vx/proshares'
for t in ('UVXY', 'SVXY', 'VIXY', 'VIXM'):
    rows = []
    with open('%s/%s.csv' % (SRC, t), newline='') as f:
        for r in csv.DictReader(f):
            try:
                d = dt.datetime.strptime(r['Date'], '%m/%d/%Y').date()
            except Exception:
                continue
            if d >= dt.date(2025, 1, 1):
                continue
            try:
                rows.append((d.isoformat(), float(r['NAV']), float(r['Shares Outstanding (000)']),
                             float(r['Assets Under Management'])))
            except Exception:
                continue
    rows.sort()
    with open('%s/%s.csv' % (DST, t), 'w') as f:
        f.write('date,nav,shares_000,aum\n')
        for r in rows:
            f.write('%s,%.8f,%.3f,%.2f\n' % r)
    print(t, len(rows), rows[0][0], rows[-1][0])
