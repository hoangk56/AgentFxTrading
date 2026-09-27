# AgentFxTrading — AI Agent Project Conventions

This file is the single source of agent rules for this repo. Tool-specific files (`CLAUDE.md`, `.omp/`)
only point here; if they ever disagree with this file, this file wins.

## Architecture Overview
- **Backend**: FastAPI server running under systemd as `agentfx.service`
  (`/home/forge/AgentFxTrading/.venv/bin/uvicorn app.server:app --host 127.0.0.1 --port 8000`).
- **Bots**: Spotware cTrader CLI containers running in Docker with `--network host`, one container per
  strategy × symbol × account. Two strategies, both rule-based: Gotobi Fix (`cBot/GotobiBot.cs`) and Crypto
  Donchian (`cBot/CryptoDonchianBot.cs`). The server makes no trading decision: the bots report positions and
  telemetry (`/portfolio/report`, `/api/tick`) and poll dashboard commands (`/api/cbot/commands`).
  - Containers are named `cbot-<account slug>-<symbol>-<session>-<strategy>`; the name doubles as `--BotId`.
    List what actually runs with `docker ps`.
  - Source of truth for presets and strategy flags: `app/cbot_presets.py`. The long form (every `docker run`
    command) is `docs/docker-instances.md`; `tests/app/test_cbot_presets.py` keeps the two in sync. Do not copy
    preset tables anywhere else (README included).
- **Watchdog**: background auto-healing loop in `app/cbot_watchdog.py` that monitors cBot login state and
  restarts stuck containers.
- **Database**: PostgreSQL 17 in production via `DATABASE_URL`, with a daily backup cron job
  (`scripts/backup_postgres.sh`); SQLite WAL (`portfolio.db`) is the fallback for local runs and tests.
- **Research**: `research/` is offline strategy research (the swing lab behind both bots) with its own venv
  (`research/.venv`, `research/requirements.txt`) and tests. Conclusions go in `research/JOURNAL.md` (one dated
  entry per result).

## Where new code goes
- New HTTP endpoints: an `APIRouter` module (see `app/dashboard.py`, `app/backtest_api.py`) included from
  `app/server.py`, not new `@app.*` handlers in `server.py`.
- New dashboard JavaScript: a file under `static/js/`, not inline `<script>` in `templates/*.html`.
- New tests: `tests/app/...` for the Python app, `tests/cbot/<bot>/` for tests that read `cBot/*.cs` source.
- Docs: `README.md` stays a short overview (install, run, links). Reference material lives in English under
  `docs/`. The translations (`README.vi/ja/zh/ru/pt.md`) translate only the short README; when you change
  `README.md`, update them too or say which ones are now behind.
- Don't quote performance figures (win rate, Sharpe, …) without a result file under `research/results/` to
  cite.

## Mandatory Post-Feature Delivery Workflow
Whenever you add a feature, fix a bug, or adjust configurations:

1. **Test & Verify**:
   - App: `pytest` from the repo root (the root `pytest.ini` limits it to `tests/`). On the VPS:
     `/home/forge/AgentFxTrading/.venv/bin/pytest`.
   - Research (only if `research/` changed): `research/.venv/bin/python -m pytest research/tests`.
   - Ensure all tests pass, or report the failures with their output.

2. **Commit & Push — only when the user asks**:
   - **Never commit or push on your own.** Finish with the changes left in the working tree, report what
     changed and the test result, and wait for the user to say "commit" / "push". An approval covers that
     one commit or push, not later ones.
   - Several agent sessions may be editing this checkout at once: stage only the files (or hunks) you
     changed yourself — never `git add -A`, `git add .`, or a whole file that also carries another
     session's edits.
   - When asked:
     - Stage: `git add <files>`
     - Commit: `git commit -m "feat/fix/style: <concise message>"`
     - Push the current branch: `git push -u <remote> <current-branch>`. Don't push to `main` or merge
       into it unless the user says so.
   - `.gitignore` ignores bulky research output (`research/results/**` data files, `research/data/`) but
     tracks Markdown reports. If a file you were asked to commit is ignored, run
     `git check-ignore -v <file>` and tell the user instead of forcing it in silently.

3. **Restart Service** (on the VPS, once the change is deployed there):
   - If `app/`, `templates/`, or `static/` files changed: `systemctl restart agentfx.service`
   - Verify: `systemctl status agentfx.service` and `curl -s http://127.0.0.1:8000/api/watchdog/status`

4. **Restart cBot Containers (If Relevant)**:
   - If `cBot/*.cs`, bot parameters, or database bot configs changed: restart the affected container(s)
     with `docker restart <container_name>`, then check for a clean login with
     `docker logs --tail 20 <container_name>`.
