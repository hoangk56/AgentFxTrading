import sys, csv; sys.path.insert(0,'.')
import numpy as np, carry as C
syms=[l.strip() for l in open(sys.argv[1]) if l.strip()]
P=C.load_panel(syms); U,rank=C.universe(P,N=30)
cfg=dict(L=7,th_in=0.10,th_out=0.0,K=10)
c3={}
for r in csv.DictReader(open('../../trades_C3_gotobi_jpy_basket.csv')):
    k=r['t_out_utc'][:10]; c3[k]=c3.get(k,0)+float(r['r'])
for era in ('IS','VAL'):
    d0,d1=C.era_slice(P,era); y=C.years(P['days'][d0:d1])
    for name,kw in (('base',{}),('cost1.5',{'cost_mult':1.5}),('late1d',{'lag':1})):
        b,eps=C.simulate(P,U,rank,d0=d0,d1=d1,**cfg,**kw); st=C.stats(b)
        print(era,name,'ann %.2f%% vol %.2f%% SRa %.2f tNW %.2f dd %.2f%% eps %d'%(100*st['ann'],100*st['vol'],st['sharpe_a'],st['t_nw'],100*st['maxdd'],len(eps)),
              {int(k):round(100*b[y==k].sum(),2) for k in np.unique(y)})
    b,eps=C.simulate(P,U,rank,d0=d0,d1=d1,**cfg)
    print('  drop top5 days tNW %.2f'%C.stats(np.sort(b)[:-5])['t_nw'], ' worst days %', np.round(100*np.sort(b)[:5],3))
    rs=[C.stats(C.random_book(P,U,rank,eps,d0,d1,K=10,rng=np.random.default_rng(s)))['sharpe_a'] for s in range(300)]
    print('  random SRa median %.2f  beaten %.1f%%'%(np.median(rs),100*np.mean(np.array(rs)<C.stats(b)['sharpe_a'])))
    rises=[]; 
    for (i,e,x,c) in eps:
        H=P['F'][i][e:x+1]; rises.append(np.nanmax(H)/H[0]-1)
    rises=np.array(rises); print('  episodes with perp rise > 50%%: %d, >100%%: %d, >200%%: %d of %d'%((rises>.5).sum(),(rises>1).sum(),(rises>2).sum(),len(rises)))
    worst=sorted(eps,key=lambda e: C.episode_pnl(P,e[0],e[1],e[2]).sum()-e[3])[:5]
    for (i,e,x,c) in worst: print('    worst ep',P['syms'][i],str(np.datetime64(int(P['days'][e]),'ms'))[:10],x-e,'d  %.2f%%'%(100*(C.episode_pnl(P,i,e,x).sum()-c)))
    days=[str(np.datetime64(int(t),'ms'))[:10] for t in P['days'][d0:d1]]
    v=np.array([c3.get(d,0.0) for d in days]); print('  corr C3 daily %.3f'%np.corrcoef(b,v)[0,1])
    from collections import Counter; print('  top coins', Counter(P['syms'][e[0]] for e in eps).most_common(8))
