# A2-D5L capture test and B borrow check: cheapest steps of the user's decisions 1 and 2, 2026-11-02

The user approved (2026-11-02) decision 1 (A2-D5L notice bot) and decision 2 (B borrow), each from its cheapest step,
and K2 as paper only. No order was sent and no account was opened.

## Answer first
- **A2: keyless polling cannot meet the registered gate** (detection <= 3 s after N on >= 80 % of live KRW-listing
  notices). The notice list returns 429 long before a 1.5 s poll can be sustained:

  | host | period | result |
  |---|---|---|
  | agentFx (Hetzner, Helsinki) | 1.5 s | 429 after 3 requests |
  | agentFx | 3 s, after 4 min quiet | 429 after 1 request, then every ~35 s after a 30 s backoff |
  | agentFx | 5 s | 429 after 1-2 requests |
  | Mac (residential, Viettel) | 1.5 s | 429 after 15 requests (~22 s) |
  | crawl's Surfshark exit vpn-sg (Datacamp, Singapore), asked by the user | 1.5 s, stop at first 429 | 429 after 10 requests (16 s) |

  The allowance is a burst of ~10-15 requests per IP whatever the network; the earlier pitfall note (~10 requests / min)
  fits. At ~10 / min a single IP polls every ~6 s, so detection lag is ~uniform 0-6 s and well under 80 % of notices
  fall within 3 s. Meeting the gate keyless would need several IPs in rotation, which was declined (it evades the
  block Upbit put on agentFx).

  The response itself is fresh (Cloudflare `cache-control: public, max-age=1`, `cf-cache-status: REVALIDATED`), so the
  limit is the request rate, not caching. Spreading requests across IPs would be working around the limit, so it was
  not done.
  - The remaining route is Upbit's private WebSocket notice feed. It needs an Upbit account with an API key; Upbit
    normally requires Korean identity verification. This is a **user decision**; without it, A2 cannot be promoted.
  - Round 65 (stream W) saw 1.5 s "run clean" only in short paging runs of fewer than 15 requests.
- **B: the paper demo already runs** (`app/basis_b_runner.py`, hourly cron on agentFx since 2026-11-01,
  `docs/basis-b-demo.md`). Its first signal, LSKUSDT at 2026-11-02 01:00 UTC (d -124 bp), was recorded as not
  fillable: `available-inventory` LSK = 0, and `maxBorrowable` LSK returned -3045 "The system does not have enough
  asset now". This is a real shortage of lendable coin, the risk B's research could not measure, not an account block.
  - Today's universe (60 coins): 5 have zero inventory (HYPE, OGN, IOST, WAL, LSK) and 5 are not in the inventory list.
    The PREREG stop rule (> 30 % of signals not fillable) will decide on signals, not on this snapshot.
  - Account level: `maxBorrowable` SOL = 0 with `borrowLimit` 0, i.e. the cross-margin account holds no collateral.
    This matters only for real trades: the user must open Cross Margin and move collateral in. The paper demo decides
    fillability from system inventory.
- **K2: paper only.** The public-data forward log is re-run by hand (`K/coord/forward/fwd_k2.py`): 1 event so far,
  NIL +2,238 bp. The A2 public forward log (`fwd_a2.py`) has 0 events in 2026-10-30..10-31.

## Slow logger: started, then stopped
- `capture_a2.py` (this folder) ran on agentFx from forge's crontab (01:25-01:53 UTC), polling every 20 s with a
  backoff that doubled to 8 min. Its only purpose was to check that notices appear at their stamp N.
- It got 429 again after 4-8 requests, and the first request after an 8-minute pause was 429 too. The Hetzner IP is in
  a lasting penalty state, so the logger was stopped per the 429 rule.
  - Cron line and folder removed; logs kept in `research/data/upbit_capture_a2/` (no notice was captured).
- Keyless capture from a server is therefore not available at any useful rate.
