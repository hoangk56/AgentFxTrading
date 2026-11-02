import sys
sys.path.insert(0, "/Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round66_fast_execution/B2/code")
import net
for h in sys.argv[1:]:
    try:
        s, b = net.get(f"https://{h}/robots.txt", save=f"robots_{h}.txt", note="GET robots")
    except SystemExit as e:
        print(h, "403"); continue
    print("=====", h, s, len(b)); print(b[:1500].decode("utf-8", "replace"))
