import datetime as dt, math, pathlib, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0,".")
from research.swing.swing_rules import gotobi_days
from research.ticks import load_ticks
from research.tools.gotobi_holidays import no_fix_days
T=pathlib.Path(sys.argv[1]); P=("USDJPY","EURJPY","GBPJPY"); UTC=dt.timezone.utc
HOL=no_fix_days(range(2020,2027))
OFF=[-60,-30,-15,-10,-7,-5,-4,-3,-2,-1,-0.5,0.2,0.5,1,2,3,5,10]
def ms(d,h,m,s=0.0): return int(dt.datetime(d.year,d.month,d.day,tzinfo=UTC).timestamp()*1000+(h*3600+m*60+s)*1000)
f=defaultdict(dict); c=defaultdict(dict); fx918={}
for s in P:
    for d in gotobi_days(dt.date(2020,1,1),dt.date(2026,10,8)):
        if d in HOL: continue
        tk=load_ticks(s,d,d,T)
        if not len(tk): continue
        def at(t):
            i=int(np.searchsorted(tk.ts,t,side="right"))-1
            return None if i<0 or t-tk.ts[i]>300000 else (tk.bid[i],tk.ask[i])
        p0=at(ms(d,0,55)); e0=at(ms(d,2,55))
        if not p0 or not e0: continue
        for o in OFF:
            p=at(ms(d,0,55,o)); q=at(ms(d,2,55,o))
            if p: f[o][(s,d)]=(p[0]-p0[0])*100
            if q: c[o][(s,d)]=(e0[1]-q[1])*100
        if d==dt.date(2026,9,18):
            fx918[s]={k:at(ms(d,*k)) for k in [(0,54),(0,55),(2,54),(2,55),(2,56)]}
def mt(x):
    n=len(x); m=float(np.mean(x)); sd=float(np.std(x,ddof=1)); return n,m,m/(sd/math.sqrt(n))
def pd_(cells,ys):
    g=defaultdict(list)
    for (s,d),v in cells.items():
        if d.year in ys: g[d].append(v)
    return [sum(v)/len(v) for v in g.values()]
for name,ys in (("2020-2024",range(2020,2025)),("2025",[2025]),("2026",[2026]),("2020-2026",range(2020,2027))):
    print(f"\n{name}: tau  fix(1 chiều) t | đóng short t | tổng 2xfix+đóng t (n ngày)")
    for o in OFF:
        a=mt(pd_(f[o],ys)); b=mt(pd_(c[o],ys))
        tot={k:2*f[o][k]+c[o][k] for k in f[o] if k in c[o]}
        t=mt(pd_(tot,ys))
        print(f"  {o:+6.1f} {a[1]:+6.2f} {a[2]:+5.1f} | {b[1]:+6.2f} {b[2]:+5.1f} | {t[1]:+6.2f} {t[2]:+5.1f} ({t[0]})")
print("\n18/09/2026:",{s:{k:(round(v[0],3),round(v[1],3)) for k,v in x.items()} for s,x in fx918.items()})
y=pd_({k:2*f[-60][k]+c[-60][k] for k in f[-60] if k in c[-60]},[2026])
y2=sorted(y); print("2026 đến 08/10, tổng sớm 60s:",mt(y)); print("bỏ ngày cao nhất:",mt(y2[:-1]))
