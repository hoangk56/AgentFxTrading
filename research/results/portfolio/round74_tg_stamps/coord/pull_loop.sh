#!/bin/sh
# Chạy lại pageback (resumable) sau lỗi mạng tạm thời; dừng hẳn khi gặp 403/429 (STOP) hoặc đủ hết trang.
cd "$(dirname "$0")"
PY=/Users/hoangbk/00.code_base/105.AgentFxTrading/research/.venv/bin/python
for i in $(seq 1 40); do
  out=$($PY -I pageback.py "$@" 2>&1); echo "$out" | tail -4
  echo "$out" | grep -q "STOP" && { echo "STOP seen, quit"; exit 1; }
  echo "$out" | grep -q "status -1" || { echo "finished"; exit 0; }
  sleep 30
done
