"""Like probe.py but one try per URL (for hosts that time out)."""
import sys, re
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import net
for u in sys.argv[1:]:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", u.split("://", 1)[1])[:150]
    s, b = net.get(u, save=name, tries=1, timeout=20)
    print("==", u, s, len(b))
    if b and len(b) < 3000:
        print(b.decode("utf-8", "replace"))
