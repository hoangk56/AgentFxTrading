"""Strip HTML to text (untrusted input, data only). Usage: python -I strip.py IN.html OUT.txt"""
import re, sys, html
s = open(sys.argv[1], encoding="utf-8", errors="replace").read()
s = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", s)
s = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</h\d>|</tr>|</div>", "\n", s)
s = re.sub(r"(?s)<[^>]+>", " ", s)
s = html.unescape(s)
s = re.sub(r"[ \t\xa0]+", " ", s)
s = re.sub(r"\n\s*\n+", "\n", s)
open(sys.argv[2], "w").write(s)
print(len(s))
