#!/bin/bash
# Copy only the given years of the cTrader tick/m15 cache from the VPS: pull_years.sh "2023 2024" BTCUSD XAUUSD ...
# The glob runs inside `sudo sh` (root), since the cache is root-owned and a forge-side glob would fail.
set -euo pipefail
VPS=forge@204.168.144.232
CACHE=/var/lib/docker/volumes/agentfx-bt-cache/_data/V1/demo_e5322e87
DEST="$(cd "$(dirname "$0")" && pwd)/data"
YEARS=$1; shift
for s in "$@"; do
  pats=""
  for y in $YEARS; do pats="$pats t1/${y}*.zticks m15/${y}*.zbars"; done
  mkdir -p "$DEST/$s"
  ssh "$VPS" "sudo -n sh -c 'cd $CACHE/$s && tar cf - $pats 2>/dev/null; true'" | tar xf - -C "$DEST/$s"
  echo "$s: $(ls "$DEST/$s/t1" | wc -l | tr -d ' ') tick days ($(ls "$DEST/$s/t1" | head -1) .. $(ls "$DEST/$s/t1" | tail -1))"
done
