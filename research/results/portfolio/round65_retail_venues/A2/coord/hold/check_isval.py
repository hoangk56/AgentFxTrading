"""Must reproduce PREREG_DRAFT_A2_D5L: IS n 12 +1,296 bp t 3.07; VAL n 32 +520 t 1.75 (aggressor +516, worst-of-1s +373)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core
from events import load_events
E = load_events()
core.use_npz("/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/upbit_latency/npz")
for era in ("IS", "VAL"):
    core.grade([e for e in E if e["era"] == era], era)
