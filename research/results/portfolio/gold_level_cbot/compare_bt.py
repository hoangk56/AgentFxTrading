"""Compare the GoldLevelBot backtest trade logs with the registered HOLD run's trades, trade by trade.
usage: python compare_bt.py ENGINE_TRADES.csv BOT_TRADES.csv [...]"""
import csv, sys
import numpy as np
eng = {r['trigger_utc']: r for r in csv.DictReader(open(sys.argv[1]))}
bot = {}
for fn in sys.argv[2:]:
    for r in csv.DictReader(open(fn)):
        bot[r['trigger_utc']] = r
both = sorted(set(eng) & set(bot)); only_e = sorted(set(eng) - set(bot)); only_b = sorted(set(bot) - set(eng))
print(f'engine {len(eng)}, bot {len(bot)}, matched on trigger time {len(both)}, engine only {len(only_e)}, bot only {len(only_b)}')
for k in only_e: print('  engine only', k, eng[k]['level'], eng[k]['side'], eng[k]['net_250'])
for k in only_b: print('  bot only   ', k, bot[k]['level'], bot[k]['side'], bot[k]['model_net_bp'])
fields = [('arm_utc', 'arm_utc'), ('level', 'level'), ('side', 'side')]
bad = [k for k in both if any(eng[k][a] != bot[k][b] and not (a == 'level' and float(eng[k][a]) == float(bot[k][b])) for a, b in fields)]
print('matched trades with a different arm time / level / side:', len(bad))
d_stop = np.array([float(bot[k]['stop']) - float(eng[k]['stop_price']) for k in both])
d_s60 = np.array([float(bot[k]['s60']) - float(eng[k]['s60_arm']) for k in both])
m_net = np.array([float(bot[k]['model_net_bp']) for k in both]); e_net = np.array([float(eng[k]['net_250']) for k in both])
filled = [k for k in both if bot[k]['fill_net_bp']]
missed = [k for k in both if not bot[k]['fill_net_bp']]
print(f'filled {len(filled)}, missed {len(missed)}' + (': ' + ', '.join(f"{k} ({bot[k]['note']})" for k in missed) if missed else ''))
f_net = np.array([float(bot[k]['fill_net_bp']) for k in filled]); e_l0 = np.array([float(eng[k]['net_L0']) for k in filled])
print(f'max |stop diff| {np.abs(d_stop).max():.2e}, max |s60 diff| {np.abs(d_s60).max():.2e}')
print(f'bot model net (250 ms) vs engine net_250: max |diff| {np.abs(m_net - e_net).max():.4f} bp; means {m_net.mean():+.3f} / {e_net.mean():+.3f}')
print(f'backtest fill net vs engine net_L0: max |diff| {np.abs(f_net - e_l0).max():.4f} bp; means {f_net.mean():+.3f} / {e_l0.mean():+.3f}')
big = [(k, f_net[i] - e_l0[i]) for i, k in enumerate(filled) if abs(f_net[i] - e_l0[i]) > 0.05]
for k, d in big[:10]: print('  fill vs L0 differs', k, f'{d:+.3f}')
