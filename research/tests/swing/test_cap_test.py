"""research/swing/cap_test.py: stack ranks, episodes, the clustered t and the mark-to-market drawdown."""
import numpy as np
import pytest

from research.ticks import DATA_DIR

needs_m1 = pytest.mark.skipif(not (DATA_DIR / "m1" / "BTCUSD.npz").exists(), reason="no M1 cache")
H = 3_600_000


def _trade(sym, t_in, t_out, r=0.0, side=1):
    from research.swing.swing import Trade
    return Trade(sym, side, t_in, t_in, t_out, 1.0, 1.0, 0.1, r, "time", 1.0)


def test_ranks_count_the_bots_open_positions_at_entry():
    from research.swing.cap_test import ranks
    tr = [_trade("A", 0, 10 * H), _trade("A", 1 * H, 10 * H), _trade("A", 2 * H, 3 * H), _trade("A", 3 * H, 4 * H),
          _trade("B", 1 * H, 2 * H)]
    assert ranks(tr) == [1, 2, 3, 3, 1]      # the 2-3 h position closed at 3 h, so it does not count then


def test_episodes_chain_overlapping_positions_per_bot():
    from research.swing.cap_test import episodes
    tr = [_trade("A", 0, 2 * H), _trade("A", 1 * H, 5 * H), _trade("A", 4 * H, 6 * H), _trade("A", 6 * H, 7 * H),
          _trade("B", 1 * H, 2 * H)]
    ep = episodes(tr)
    assert ep[0] == ep[1] == ep[2] != ep[3]
    assert ep[4][0] == "B"


def test_cluster_t_is_the_plain_t_with_one_trade_per_cluster():
    from research.swing.cap_test import cluster_t
    from research.swing.swing import tstat
    rs = [0.5, -1.0, 2.0, 0.3, -0.2, 1.1]
    n, mu, t = cluster_t(rs, range(len(rs)))
    assert (n, mu) == (6, pytest.approx(np.mean(rs)))
    assert t == pytest.approx(tstat(rs)[2])


def test_cluster_t_does_not_count_a_duplicated_trade_twice():
    from research.swing.cap_test import cluster_t
    rs = [0.5, -1.0, 2.0, 0.3, -0.2, 1.1]
    single = cluster_t(rs, range(len(rs)))[2]
    doubled = cluster_t(rs + rs, list(range(len(rs))) * 2)[2]
    assert doubled == pytest.approx(single)


def test_drawdown_nets_changes_at_one_time_and_counts_open_losses():
    from research.swing.cap_test import drawdown
    assert drawdown([(1, 5.0), (1, -5.0)]) == 0.0
    assert drawdown([(1, 10.0), (2, -30.0), (3, 25.0)]) == pytest.approx(30.0)
    assert drawdown([]) == 0.0


def test_peak_risk_frees_the_slot_of_a_position_closing_at_the_entry_minute():
    from research.swing.cap_test import peak_risk
    tr = [_trade("A", 0, 2 * H), _trade("A", 1 * H, 3 * H), _trade("A", 2 * H, 4 * H)]
    assert peak_risk(tr) == pytest.approx(200.0)


@needs_m1
def test_c1_runs_respect_the_cap_and_the_mark_to_market_ends_at_the_net():
    from research.swing import cap_test as C
    for cap in (1, 3):
        tr = C.run_c1(cap)
        assert tr and max(C.ranks(tr)) == cap
    tr = C.run_c1(3)[:40]
    inc = C.mtm_increments(tr)
    assert sum(d for _, d in inc) == pytest.approx(sum(t.usd for t in tr))
