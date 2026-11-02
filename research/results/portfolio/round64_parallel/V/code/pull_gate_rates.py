"""Gate public hourly loan-rate history for B's current-universe and VAL-event coins that Gate lends."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coins  # noqa: E402
import fetch  # noqa: E402

D = fetch.ROOT + '/gate'
uc = {c['name']: c for c in json.load(open(D + '/unified_currencies.json'))}
want = sorted(set(coins.current_universe()) | set(coins.val_event_coins()))
os.makedirs(D + '/hlr', exist_ok=True)
n = 0
for c in want:
    if c not in uc or uc[c].get('loan_status') != 'enable':
        continue
    p = f'{D}/hlr/{c}.json'
    if os.path.exists(p):
        continue
    st, _ = fetch.get(f'https://api.gateio.ws/api/v4/unified/history_loan_rate?currency={c}', p)
    n += 1
    if st in (403, 'blocked'):
        print('stopped: 403')
        break
print('requested', n)
