#!/bin/bash
# usage: fetch.sh <url> <outfile> [via_agentfx]
# Logs UTC time, URL, status, bytes to requests.log; sleeps >= 1.2 s after each request.
D=/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/hk_lev_etf
url="$1"; out="$2"; via="$3"
t=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if [ "$via" = "agentfx" ]; then
  tmp=/tmp/hkle_$$.bin
  st=$(ssh agentFx "curl -s -m 40 -A research-script -o $tmp -w '%{http_code}' '$url'; " 2>/dev/null)
  ssh agentFx "cat $tmp 2>/dev/null; rm -f $tmp" > "$out"
else
  st=$(curl -s -m 40 -A research-script -o "$out" -w '%{http_code}' "$url")
fi
b=$(wc -c < "$out" | tr -d ' ')
echo "$t $st $b $url${via:+ (via agentFx)}" >> $D/requests.log
echo "$st $b"
sleep 1.2
