import sys
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/B2/code")
import net
url, save = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
try:
    s, b = net.get(url, save=save)
except SystemExit as e:
    print("STOP", e); sys.exit()
print(s, len(b)); print(b[:n].decode("utf-8", "replace"))
