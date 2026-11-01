import sys; sys.path.insert(0,'.')
import numpy as np, carry as C
P=C.load_panel(['BTCUSDT','ETHUSDT']); U,rank=C.universe(P,N=30)
cfg=dict(L=14,th_in=0.10,th_out=0.0,K=2,only={'BTCUSDT','ETHUSDT'})
for era in ('IS','VAL'):
    d0,d1=C.era_slice(P,era)
    for name,kw in (('base',{}),('cost1.5',{'cost_mult':1.5}),('late1d',{'lag':1})):
        b,eps=C.simulate(P,U,rank,d0=d0,d1=d1,**cfg,**kw)
        st=C.stats(b); y=C.years(P['days'][d0:d1])
        print(era,name,'ann %.2f%% vol %.2f%% SRa %.2f tNW %.2f dd %.2f%% eps %d inmkt %.0f%%'%(100*st['ann'],100*st['vol'],st['sharpe_a'],st['t_nw'],100*st['maxdd'],len(eps),100*np.mean(b!=0)),
              {int(k):round(100*b[y==k].sum(),2) for k in np.unique(y)})
    # drop top 5 days
    b,eps=C.simulate(P,U,rank,d0=d0,d1=d1,**cfg); bb=np.sort(b)[:-5]; print('  drop top5 days tNW %.2f'%C.stats(bb)['t_nw'])
    rs=[C.stats(C.random_book(P,U,rank,eps,d0,d1,K=2,rng=np.random.default_rng(s)))['sharpe_a'] for s in range(200)]
    print('  random SRa median %.2f  pct beaten %.1f%%'%(np.median(rs),100*np.mean(np.array(rs)<C.stats(b)['sharpe_a'])))
