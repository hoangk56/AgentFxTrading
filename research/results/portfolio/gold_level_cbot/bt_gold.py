"""Backtest the compile-checked GoldLevelBot.algo (temp build, not production) on IC ticks, to compare its trades with
the research engine's. Runs on the VPS like pull_ticks_r30.py: credentials, account and paths come from the demo
EcbWindowBot container and are never printed; bridge network, URLs disabled, CommandPollMs=0, low CPU priority.
usage: python3 bt_gold.py NAME START END [extra --Param=value ...]   (dates dd/mm/yyyy)
Writes out/<NAME>/trades.csv (the bot's trade log), out/<NAME>/log.txt (docker logs), out/<NAME>/report.json."""
import json
import os
import re
import subprocess
import sys
import time

SRC = "cbot-demo-demo-eurusd-ecb-e1"
HERE = "/home/forge/backtest_tmp/r30"
ALGO = f"{HERE}/build_home/cAlgo/Sources/Robots/GoldLevelBot.algo"
CAL = f"{HERE}/seed_bt.csv"
OFF = "http://127.0.0.1:9/disabled"
name, start, end = sys.argv[1:4]
extra = sys.argv[4:]
out = f"{HERE}/out/{name}"
os.makedirs(out, exist_ok=True)


def sh(*a, **kw):
    return subprocess.run(list(a), capture_output=True, text=True, **kw)


def scrub(s):
    return re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "<email>", s)


args = json.loads(sh("docker", "inspect", SRC, "--format", "{{json .Args}}").stdout)
opt = {a[2:].split("=", 1)[0]: a.split("=", 1)[1] for a in args if a.startswith("--") and "=" in a}
mounts = json.loads(sh("docker", "inspect", SRC, "--format", "{{json .Mounts}}").stdout)
root_src = next(m["Source"] for m in mounts if m["Destination"] == "/root")
PWD = root_src + opt["pwd-file"][len("/root"):]
IMAGE = sh("docker", "inspect", SRC, "--format", "{{.Config.Image}}").stdout.strip()
cname = f"bt-r30-gold-{name}"
sh("docker", "rm", "-f", cname)
cmd = ["docker", "run", "-d", "--name", cname, "--network", "bridge", "--memory", "3g", "--cpus", "1.5",
       "--cpu-shares", "256", "-v", f"{ALGO}:/algo/GoldLevelBot.algo:ro", "-v", f"{PWD}:/secrets/pwd:ro",
       "-v", f"{CAL}:/cal/usd_high_calendar.csv:ro", "-v", f"{out}:/out", "-v", "agentfx-bt-cache:/bt-cache",
       IMAGE, "backtest", "/algo/GoldLevelBot.algo", f"--ctid={opt['ctid']}", "--pwd-file=/secrets/pwd",
       f"--account={opt['account']}", "--symbol=XAUUSD", "--period=m15", f"--start={start}", f"--end={end}",
       "--data-mode=ticks", "--data-dir=/bt-cache", "--balance=100000", "--commission-auto",
       "--report-json=/out/report.json", "--full-access", "--exit-on-stop",
       "--CalendarFile=/cal/usd_high_calendar.csv", "--TradeLogFile=/out/trades.csv", "--Lots=0.01",
       f"--ApiUrl={OFF}", f"--TelemetryUrl={OFF}", f"--ReportUrl={OFF}", "--CommandPollMs=0", f"--BotId=bt-gold-{name}",
       "--AccountLabel=backtest", *extra]
t0 = time.time()
r = sh(*cmd)
if r.returncode:
    print("START FAILED", scrub(r.stderr)[-500:])
    sys.exit(1)
code = sh("docker", "wait", cname).stdout.strip()
logs = sh("docker", "logs", cname)
open(f"{out}/log.txt", "w").write(scrub(logs.stdout + logs.stderr))
sh("docker", "rm", cname)
n = sum(1 for l in open(f"{out}/log.txt") if "[GoldLevel] TRADE" in l)
print(f"{name}: exit {code} in {time.time() - t0:.0f}s, {n} TRADE lines; out {out}")
