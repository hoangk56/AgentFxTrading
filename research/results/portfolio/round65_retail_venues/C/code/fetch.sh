#!/bin/bash
# Lấy một URL qua agentFx (DNS của Mac trỏ hkex.com.hk về 127.0.0.1), chép thân về máy, ghi requests.log.
# Dùng: fetch.sh <url> <file đích, tương đối trong research/data/hk_cbbc/raw/>
# Không để lại file trên agentFx: file tạm ở /tmp bị xoá ngay trong cùng lệnh.
set -u
URL="$1"; OUT="$2"
D=/Users/hoangbk/00.code_base/105.AgentFxTrading/research/data/hk_cbbc
mkdir -p "$D/raw/$(dirname "$OUT")"
sleep 1.2
META=$(ssh agentFx "f=\$(mktemp /tmp/c.XXXXXX); m=\$(curl -s -A research-script --max-time 60 -o \$f -w '%{http_code} %{size_download} %{content_type} %{redirect_url}' '$URL'); echo \"\$m\" >&2; cat \$f; rm -f \$f" 2>"$D/.meta.tmp" >"$D/raw/$OUT")
M=$(tail -1 "$D/.meta.tmp"); rm -f "$D/.meta.tmp"
CODE=$(echo "$M" | awk '{print $1}'); BYTES=$(echo "$M" | awk '{print $2}')
printf '%s\tGET\t%s\t%s\t%s\tvia agentFx\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$URL" "$CODE" "$BYTES" "$M" >> "$D/requests.log"
echo "$M"
