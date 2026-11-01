import sys, csv; sys.path.insert(0,'.')
import numpy as np, carry as C
P=C.load_panel(['BTCUSDT','ETHUSDT']); U,rank=C.universe(P,N=30)
cfg=dict(L=14,th_in=0.10,th_out=0.0,K=2,only={'BTCUSDT','ETHUSDT'})
# C3 daily pnl (R) by UTC exit date
c3={}
for r in csv.DictReader(open('../../trades_C3_gotobi_jpy_basket.csv')):
    k=r['t_out_utc'][:10]; c3[k]=c3.get(k,0)+float(r['r'])
for era in ('IS','VAL'):
    d0,d1=C.era_slice(P,era)
    b,eps=C.simulate(P,U,rank,d0=d0,d1=d1,**cfg)
    for (i,e,x,c) in eps:
        F=P['F'][i]; H=F[e:x+1]
        print(era,P['syms'][i],str(np.datetime64(int(P['days'][e]),'ms'))[:10],str(np.datetime64(int(P['days'][x]),'ms'))[:10],
              'days %4d  max perp rise from entry %+.0f%%  pnl %.2f%%'%(x-e,100*(np.max(H)/H[0]-1),100*(C.episode_pnl(P,i,e,x).sum()-c)))
    days=[str(np.datetime64(int(t),'ms'))[:10] for t in P['days'][d0:d1]]
    v=np.array([c3.get(d,0.0) for d in days]); m=v!=0
    print(era,'corr with C3 daily (C3 trade days) %.3f  all days %.3f'%(np.corrcoef(b[m],v[m])[0,1],np.corrcoef(b,v)[0,1]))
    # worst daily book returns
    print('  worst days', np.round(100*np.sort(b)[:5],3))
