"""B's coin lists (names only; no trade results). Run with python -I (adds its own dir)."""
import csv
import time

R63 = '/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round63_parallel'
EXCL = {'BTCUSDT', 'ETHUSDT'}  # B's basis.py EXCL
VAL0 = int(time.mktime((2022, 1, 1, 0, 0, 0, 0, 0, 0)) - time.timezone) * 1000
CUT = int(time.mktime((2025, 1, 1, 0, 0, 0, 0, 0, 0)) - time.timezone) * 1000


def _rows(name):
    return [r for r in csv.reader(open(f'{R63}/B/{name}')) if r and r[0] not in EXCL]


def base_of(spot):
    return spot[:-4] if spot.endswith('USDT') else spot


def current_universe():
    """Coins in universe60_hold.csv whose membership reaches the last 30 days of the file."""
    rows = _rows('universe60_hold.csv')
    mx = max(int(r[4]) for r in rows)
    return sorted({base_of(r[1]) for r in rows if int(r[4]) >= mx - 30 * 86400000})


def all_names():
    return sorted({base_of(r[1]) for r in _rows('universe60.csv') + _rows('universe60_hold.csv')})


def val_events():
    """B's frozen-cell VAL entries (lag 0) from BX/out/events.csv: (perp, h_ms, e_ms, x_ms), 2022-24 only."""
    perp2spot = {r[0]: (r[1], float(r[2])) for r in _rows('universe60.csv')}
    out = []
    for r in csv.DictReader(open(f'{R63}/BX/out/events.csv')):
        if r['lag'] != '0':
            continue
        e = int(r['e_ms'])
        if not (VAL0 <= e < CUT) or int(r['x_ms']) >= CUT:
            continue
        sp = perp2spot.get(r['perp'], (r['perp'], 1.0))[0]
        out.append((r['perp'], sp, int(r['h_ms']), e, int(r['x_ms'])))
    return out


def val_event_coins():
    return sorted({base_of(sp) for _, sp, _, _, _ in val_events()})


if __name__ == '__main__':
    print('current', len(current_universe()), current_universe())
    print('all', len(all_names()))
    ev = val_events()
    print('val events', len(ev), 'coins', len(val_event_coins()))
