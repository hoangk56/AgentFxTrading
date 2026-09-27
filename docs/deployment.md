# Deployment

Installing, running and maintaining AgentFxTrading. Settings are described in [configuration.md](configuration.md);
the preset `docker run` commands in [docker-instances.md](docker-instances.md).

## One-line VPS install

For a fresh Ubuntu 22.04 / 24.04 / 26.04 VPS, as root:

```bash
curl -fsSL https://raw.githubusercontent.com/kienphan/AgentFxTrading/main/scripts/install.sh | sudo bash
```

The script ([`scripts/install.sh`](../scripts/install.sh)) asks for one thing, the SSH public key of the `forge`
user, then:

1. installs base packages (git, Python 3 venv, build tools, cron, ufw);
2. creates a swap file if none is active (2 × RAM under 2 GiB, = RAM up to 8 GiB, RAM / 2 above);
3. creates the `forge` user (passwordless sudo, key-only login) and disables SSH password login, root included;
4. installs PostgreSQL 17 with an `agentfx` role and database (random password, reused on re-runs);
5. installs Docker CE and adds `forge` to the `docker` group;
6. clones the repo into `/home/forge/AgentFxTrading`, creates `.venv` and installs `requirements.txt`;
7. writes `.env` from `.env.example` with `DATABASE_URL` and `CTRADER_HOME=/home/forge/ctrader` (an existing
   `.env` is kept, missing keys appended) and checks that the database accepts the URL;
8. builds the five cBot `.algo` packages (see [Building the cBots](#building-the-cbots));
9. installs the `agentfx` systemd service and a daily 03:00 backup cron job (`/etc/cron.d/agentfx-backup`);
10. enables ufw with only the SSH port open.

**Before closing the root session**, check the key from another terminal:

```bash
ssh forge@YOUR_VPS_IP 'sudo -n true && echo LOGIN_OK'
```

Then open the dashboard through an SSH tunnel and browse `http://127.0.0.1:8000`:

```bash
ssh -N -L 8000:127.0.0.1:8000 forge@YOUR_VPS_IP
```

Put your LLM key in `/home/forge/AgentFxTrading/.env` (`LLM_PROVIDER`, `DASHSCOPE_API_KEY`, ...) and run
`sudo systemctl restart agentfx`. Add your cTrader account and start bots from **Docker Bot Management → Setup
Instances**.

**Overrides.** `FORGE_SSH_KEY` skips the prompt; `AGENTFX_REPO` and `AGENTFX_BRANCH` pick another repository or
branch. Plain `sudo` strips the environment, so export them and use `sudo -E`:

```bash
export FORGE_SSH_KEY="ssh-ed25519 AAAA... you@laptop"
curl -fsSL https://raw.githubusercontent.com/kienphan/AgentFxTrading/main/scripts/install.sh | sudo -E bash
```

**Upgrades.** Re-running the same command is the upgrade path: every step checks its own result first, the
checkout is fast-forwarded and bots whose `.cs` is newer than their `.algo` are rebuilt.

On an installed VPS the cTrader home is `/home/forge/ctrader`, mounted as `/root` in containers: when you copy a
`docker run` command, replace `-v /root:/root` with `-v /home/forge/ctrader:/root`.

## Manual / local setup

```bash
git clone https://github.com/kienphan/AgentFxTrading.git
cd AgentFxTrading
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # set LLM_PROVIDER and its API key; optionally DATABASE_URL
```

Start the server either way:

```bash
python app/server.py                                         # uses SERVER_HOST / SERVER_PORT / SERVER_RELOAD
uvicorn app.server:app --host 127.0.0.1 --port 8000          # what the systemd service runs
```

Run a **single worker** only (no `--workers`): the dashboard → cBot command queue lives in process memory.

For PostgreSQL, create a database and role and set `DATABASE_URL`. Without a reachable PostgreSQL the server logs a
warning and uses SQLite `portfolio.db` (fine for local work and tests).

The server binds to `127.0.0.1` and has no authentication of its own; reach it through an SSH tunnel rather than
exposing the port.

## Building the cBots

Headless bots run the compiled `cBot/<Name>.algo`, which git does not track. The installer builds all five; to do
it by hand, run once per bot with `<Name>` = `AiAgentBot`, `AsianRangeJudasSweepBot`, `FlowRsiBot`, `GotobiBot`,
`CryptoDonchianBot` (from the repo root, with `CTRADER_HOME` = the host directory mounted as `/root`, e.g. `/root`
or `/home/forge/ctrader`):

```bash
IMAGE=ghcr.io/spotware/ctrader-console:latest
NAME=AiAgentBot
CTRADER_HOME=/root
ROBOTS=$CTRADER_HOME/cAlgo/Sources/Robots

# first time only: create the project skeleton
docker run --rm -v "$(pwd)":/workspace -v "$CTRADER_HOME":/root $IMAGE create cbot $NAME

cp cBot/$NAME.cs $ROBOTS/$NAME/$NAME/$NAME.cs
docker run --rm -v "$(pwd)":/workspace -v "$CTRADER_HOME":/root $IMAGE \
  build /root/cAlgo/Sources/Robots/$NAME/$NAME/$NAME.csproj
cp $ROBOTS/$NAME.algo cBot/$NAME.algo
```

Alternatively, in **cTrader Desktop**: Automate → New cBot, paste the `.cs` file, Build, and attach it to a chart
with the `ApiUrl` pointing at your server.

## Running bots

1. **cTID password file** (the dashboard writes one per account when you add it on Setup Instances):

   ```bash
   mkdir -p /root/ctrader_data
   echo "your_ctid_password" > /root/ctrader_data/ctid_pwd
   chmod 600 /root/ctrader_data/ctid_pwd
   ```

2. **Start containers** from the dashboard (**Docker Bot Management → Setup Instances**) or with the commands in
   [docker-instances.md](docker-instances.md), which also covers container naming, the placeholders to replace and
   running demo and live accounts side by side.

3. **Check** a bot with `docker logs --tail 20 <container>`; the dashboard's Bots view shows watchdog health.

## Operations

| Task | Command |
| :--- | :--- |
| Service status / logs | `systemctl status agentfx` · `journalctl -u agentfx -f` |
| Restart after changing `app/`, `templates/`, `static/` or `.env` | `sudo systemctl restart agentfx` |
| Health check | `curl -s http://127.0.0.1:8000/api/watchdog/status` |
| Restart a bot after rebuilding its `.algo` or changing its flags | `docker restart <container>` |
| Server log | `logs/agent_YYYY-MM-DD.log` (14 days kept) |

## Backups

[`scripts/backup_postgres.sh`](../scripts/backup_postgres.sh) dumps the database named by `DATABASE_URL` in `.env`
to `backups/agentfx_<timestamp>.sql.gz` (log in `backups/backup.log`) and deletes dumps older than 14 days. The
installer schedules it daily at 03:00 as the `forge` user. Restore with:

```bash
gunzip -c backups/agentfx_<timestamp>.sql.gz | psql "$DATABASE_URL"
```

## Other scripts

- `scripts/migrate_sqlite_to_pg.py`: one-off copy of a SQLite `portfolio.db` into PostgreSQL. Its target DSN is
  hard-coded at the top of the file; edit it before running.
- `scripts/deploy_feature.sh`, `scripts/recalibrate_live_risk.py`: older maintenance helpers with hard-coded
  container names. `deploy_feature.sh` stages everything and pushes to `main`, which conflicts with the repo's
  current rules in [AGENTS.md](../AGENTS.md); read them before use.

## Tests

```bash
pytest tests                                                   # app and cBot source tests
research/.venv/bin/python -m pytest research/tests             # research, own venv (research/requirements.txt)
```
