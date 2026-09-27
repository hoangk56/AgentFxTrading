"""Throttle / log_throttled (app/logging_setup.py): a line repeated by 45 bots every second is logged once a
minute with the number of repeats it held back, not 45 times a second."""
import logging

from app.logging_setup import Throttle, log_throttled


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_a_key_passes_once_per_interval_and_reports_what_it_held_back():
    clock = FakeClock()
    throttle = Throttle(60, clock=clock)
    assert throttle.hit("a") == 0          # first time: passes, nothing held back
    assert throttle.hit("a") is None       # held back
    clock.now += 30
    assert throttle.hit("a") is None       # held back
    assert throttle.hit("b") == 0          # keys are independent
    clock.now += 31
    assert throttle.hit("a") == 2          # passes again, with the two repeats it held back
    assert throttle.hit("a") is None
    clock.now += 61
    assert throttle.hit("a") == 1


def test_old_keys_are_dropped_once_the_table_is_full():
    clock = FakeClock()
    throttle = Throttle(60, clock=clock, max_keys=3)
    for key in ("a", "b", "c"):
        throttle.hit(key)
    clock.now += 61
    throttle.hit("d")                      # a, b, c are past their interval: dropped
    assert len(throttle) == 1


def test_log_throttled_logs_the_first_line_then_the_held_back_count(caplog):
    clock = FakeClock()
    throttle = Throttle(60, clock=clock)
    log = logging.getLogger("tests.throttle")
    with caplog.at_level(logging.INFO, logger="tests.throttle"):
        for _ in range(3):
            log_throttled(log, logging.WARNING, "k", "bad pnl from bot-1", throttle=throttle)
        clock.now += 61
        log_throttled(log, logging.WARNING, "k", "bad pnl from bot-1", throttle=throttle)
    assert [(r.levelno, r.getMessage()) for r in caplog.records] == [
        (logging.WARNING, "bad pnl from bot-1"),
        (logging.WARNING, "bad pnl from bot-1 (+2 similar since the last one)"),
    ]


def test_log_throttled_keeps_the_traceback(caplog):
    log = logging.getLogger("tests.throttle")
    with caplog.at_level(logging.INFO, logger="tests.throttle"):
        try:
            raise ValueError("boom")
        except ValueError:
            log_throttled(log, logging.ERROR, "tb", "failed", exc_info=True, throttle=Throttle(60))
    assert caplog.records[0].exc_info[0] is ValueError
