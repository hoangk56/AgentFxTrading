# AgentFxTrading

- Server: FastAPI under systemd `agentfx.service` (uvicorn `app.server:app`, 127.0.0.1:8000). It makes no trading
  decision: bots report to `/portfolio/report` and `/api/tick` and poll `/api/cbot/commands`.
- Bots: cTrader CLI containers (`--network host`), one per account × symbol × strategy. One strategy: Gotobi Fix
  (`cBot/GotobiBot.cs`). Name `cbot-<account>-<symbol>-<session>-<strategy>` = `--BotId`; `docker ps` lists them.
- Presets: source of truth `app/cbot_presets.py`; every `docker run` is in `docs/docker-instances.md`, kept in sync by
  `tests/app/test_cbot_presets.py`. Don't copy preset tables anywhere else.
- Changing a running bot's `RiskPerTradeMoney` is ops only: `PUT /api/bots/{name}` on the VPS (a `docker restart`
  keeps the old args). Don't touch the preset, docs or tests for it.
- Watchdog `app/cbot_watchdog.py` restarts stuck containers.
- DB: Postgres 17 in prod (`DATABASE_URL`, daily `scripts/backup_postgres.sh`); SQLite `portfolio.db` locally/tests.
- `research/`: offline, own venv (`research/.venv`). Conclusions: one dated entry per result in `research/JOURNAL.md`.

## Where code goes
- Endpoints: an `APIRouter` module included from `app/server.py`, never `@app.*` in `server.py`.
- Dashboard JS: `static/js/`, never inline in `templates/*.html`.
- Tests: `tests/app/`; tests reading `cBot/*.cs` in `tests/cbot/<bot>/`.
- Docs: English, under `docs/`. No README files.
- No performance figures (win rate, Sharpe…) without a result file under `research/results/` to cite.

## After every change
1. Test: `pytest` from the repo root (VPS: `/home/forge/AgentFxTrading/.venv/bin/pytest`). If `research/` changed:
   `research/.venv/bin/python -m pytest research/tests`. Report failures with their output.
2. Never commit or push unless asked; one approval = one commit/push. Other sessions share this checkout: stage only
   your own files/hunks, never `git add -A`/`.`. Message `feat/fix/style: <msg>`. Push the current branch; never
   push to or merge into `main` unless told. If a file to commit is ignored, run `git check-ignore -v` and tell the user.
3. VPS, once deployed: `app/`, `templates/` or `static/` changed → `systemctl restart agentfx.service`, then check
   `systemctl status agentfx.service` and `curl -s http://127.0.0.1:8000/api/watchdog/status`.
4. `cBot/*.cs`, bot params or DB bot configs changed → `docker restart <container>`, then
   `docker logs --tail 20 <container>` for a clean login.

## Prod
- nginx `000-catchall` returns 444 to everything on purpose (real money). Sole exception: `location = /error.log` for
  hub IP 213.163.206.169 only, so the hub can scan the nginx log (added 2026-10-03; old copy backed up next to the
  file and in `/root`). Don't widen it.
