# VPS Install Script — Design (Phase 1)

**Date:** 2026-09-18
**Status:** Approved (brainstorm), pending implementation plan

## Goal

One command turns a fresh Ubuntu VPS (nothing installed, root SSH access) into a
running AgentFxTrading host:

```bash
curl -fsSL https://raw.githubusercontent.com/kienphan/AgentFxTrading/main/scripts/install.sh | sudo bash
```

After it finishes: PostgreSQL 17 is running, the FastAPI server runs under systemd
as user `forge`, Docker is ready for cBot containers, and the three `.algo`
packages are compiled and sitting in `cBot/`. The dashboard is reachable only on
`127.0.0.1:8000` (SSH tunnel).

## Decisions already made

| Question | Decision |
|---|---|
| Delivery | `curl \| sudo bash` from GitHub raw; script clones the repo itself |
| Dashboard exposure | `127.0.0.1` only; user opens an SSH tunnel. No nginx. |
| Interactive input | **Only** the SSH public key. Everything else is generated or left as a placeholder in `.env`. |
| Implementation style | Single idempotent bash script, one function per step |

## Target layout on the VPS

| Item | Location | Notes |
|---|---|---|
| Service user | `forge` (groups: `sudo`, `docker`) | `/etc/sudoers.d/forge` → `forge ALL=(ALL) NOPASSWD:ALL`, mode 0440 |
| SSH | `/home/forge/.ssh/authorized_keys` (0600, dir 0700) | key from `FORGE_SSH_KEY` env or `/dev/tty` prompt |
| sshd | `/etc/ssh/sshd_config.d/00-agentfx.conf` | `PasswordAuthentication no`, `PubkeyAuthentication yes`, `PermitRootLogin prohibit-password`, `KbdInteractiveAuthentication no`. Named `00-` because sshd uses the **first** value for a keyword and cloud images ship `50-cloud-init.conf` with `PasswordAuthentication yes`. |
| Repo | `/home/forge/AgentFxTrading` | `git clone`; `.venv` inside; owned by `forge` |
| cTrader home | `/home/forge/ctrader` | mounted into every cBot container as `/root`, so in-container paths (`/root/ctrader_data/ctid_pwd`, `/root/cAlgo/...`) stay identical to the README |
| Credentials dir | `/home/forge/ctrader/ctrader_data` (0700) | created empty; Phase 2 writes `ctid_<slug>_pwd` files here |
| PostgreSQL 17 | PGDG apt repo | role `agentfx`, db `agentfx`, password = `openssl rand -hex 24` |
| Docker CE | official docker.com apt repo | `forge` in `docker` group so the Python SDK can use the socket |
| systemd unit | `/etc/systemd/system/agentfx.service` | see below |
| Backup cron | `/etc/cron.d/agentfx-backup` | `0 3 * * * forge /home/forge/AgentFxTrading/scripts/backup_postgres.sh` |
| Firewall | `ufw` | `allow <each port from sshd -T>/tcp`, `enable` (not the `OpenSSH` profile, which assumes port 22) |

Paths are derived from two script variables, `FORGE_USER=forge` and
`FORGE_HOME=/home/forge`, so nothing else is hard-coded.

### systemd unit

```ini
[Unit]
Description=AgentFxTrading FastAPI server
After=network-online.target postgresql.service docker.service
Wants=network-online.target

[Service]
User=forge
Group=forge
WorkingDirectory=/home/forge/AgentFxTrading
ExecStart=/home/forge/AgentFxTrading/.venv/bin/uvicorn app.server:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

The app loads `.env` itself via `python-dotenv`, so no `EnvironmentFile=` is needed.

## Script flow — `scripts/install.sh`

Each numbered item is a bash function. `main` calls them in order. Every function
is idempotent: it checks its own post-condition first and returns early if already
satisfied, so re-running the script is the upgrade path.

1. **`preflight`** — must be root; must be Ubuntu 22.04 or 24.04 (`/etc/os-release`);
   `systemctl` must exist. Abort with a clear message otherwise.
2. **`read_ssh_key`** — use `$FORGE_SSH_KEY` if set; else prompt on `/dev/tty`
   (stdin is the curl pipe). Validate with `ssh-keygen -l -f <(echo "$key")`.
   Abort if invalid. Never continue with an empty key — this is the only way into
   the box once password auth is off.
3. **`install_base_packages`** — `apt-get update`; install `git curl ca-certificates
   gnupg lsb-release python3 python3-venv python3-dev build-essential libpq-dev
   ufw openssl`. `DEBIAN_FRONTEND=noninteractive` throughout.
4. **`create_forge_user`** — `adduser --disabled-password --gecos ""` if missing;
   add to `sudo`; write sudoers drop-in; write `authorized_keys` (append if the key
   is not already present); fix ownership/modes.
5. **`harden_sshd`** — refuse to proceed unless `authorized_keys` contains the key;
   ensure `sshd_config` has the `Include /etc/ssh/sshd_config.d/*.conf` line; write
   the drop-in above; run `sshd -t`; only if it passes, `systemctl reload ssh`.
   Runs **after** the key is in place.
6. **`install_postgresql`** — add PGDG repo + key; install `postgresql-17`;
   `systemctl enable --now postgresql`; create role/db if absent
   (`psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='agentfx'"`). The password
   is resolved here and kept in a shell variable for step 10: if
   `/home/forge/AgentFxTrading/.env` already exists (re-run) and contains
   `DATABASE_URL`, parse the password out of it; otherwise generate a new one and
   `ALTER ROLE agentfx PASSWORD ...` so DB and `.env` always agree.
7. **`install_docker`** — add docker.com repo + key; install `docker-ce docker-ce-cli
   containerd.io`; `usermod -aG docker forge`; `systemctl enable --now docker`.
8. **`clone_repo`** — as `forge`: `git clone` if `/home/forge/AgentFxTrading/.git`
   is missing, else `git pull --ff-only`. Repo URL and branch come from
   `AGENTFX_REPO` / `AGENTFX_BRANCH` env vars (defaults: the upstream repo, `main`).
9. **`setup_venv`** — as `forge`: `python3 -m venv .venv` if missing;
   `.venv/bin/pip install --upgrade pip`; `pip install -r requirements.txt`.
10. **`write_env`** — if `.env` is missing: copy `.env.example`, then set
    `DATABASE_URL=postgresql://agentfx:<urlencoded pw>@127.0.0.1:5432/agentfx` and
    `CTRADER_HOME=/home/forge/ctrader`. If `.env` exists: leave it alone (only
    append `CTRADER_HOME` if absent). LLM keys stay as placeholders. Mode 0600.
11. **`prepare_ctrader_home`** — `mkdir -p /home/forge/ctrader/ctrader_data`
    (0700), owned by `forge`.
12. **`build_algos`** — `docker pull ghcr.io/spotware/ctrader-console:latest`;
    for each of `AiAgentBot`, `AsianRangeJudasSweepBot`, `FlowRsiBot`:
    - skip if `cBot/<Name>.algo` is newer than `cBot/<Name>.cs`;
    - `docker run --rm -v <repo>:/workspace -v /home/forge/ctrader:/root <image> create cbot <Name>` (skip if the csproj already exists);
    - `cp cBot/<Name>.cs /home/forge/ctrader/cAlgo/Sources/Robots/<Name>/<Name>/<Name>.cs`;
    - `docker run --rm ... build /root/cAlgo/Sources/Robots/<Name>/<Name>/<Name>.csproj`;
    - `cp /home/forge/ctrader/cAlgo/Sources/Robots/<Name>.algo cBot/`.
    The container runs as root, so finish with `chown -R forge:forge /home/forge/ctrader <repo>/cBot`.
    A build failure aborts the script (the bots are the point of the box).
13. **`install_systemd_unit`** — write the unit; `daemon-reload`; `enable --now`;
    poll `curl -fs http://127.0.0.1:8000/api/watchdog/status` for up to 30 s;
    abort with `journalctl -u agentfx -n 50` output if it never answers.
14. **`install_backup_cron`** — write `/etc/cron.d/agentfx-backup`.
15. **`configure_firewall`** — allow every port reported by `sshd -T` (refuse to enable ufw if none); `ufw --force enable`.
16. **`print_summary`** — what was installed, the SSH tunnel command
    (`ssh -L 8000:127.0.0.1:8000 forge@<ip>`), where `.env` is and which keys
    still need filling, and that Phase 2's "Setup Instances" screen is where
    cTrader accounts go.

Global settings: `set -euo pipefail`; a `log()` helper prefixes each step with
`==> `; a `trap` on `ERR` prints the failing step name and line. All apt work uses
`DEBIAN_FRONTEND=noninteractive` and `-y`.

## Changes to existing files

| File | Change |
|---|---|
| `scripts/install.sh` | **new** |
| `scripts/backup_postgres.sh` | Stop hard-coding the password and `/root`. Derive `PROJECT_ROOT` from the script's own location, source `DATABASE_URL` from `$PROJECT_ROOT/.env`, parse it into `PGHOST/PGPORT/PGUSER/PGPASSWORD/PGDATABASE` (URL-decode the password), keep `BACKUP_DIR=$PROJECT_ROOT/backups` and the 14-day retention. |
| `.env.example` | Add `CTRADER_HOME=/root` with a comment explaining it is the host directory mounted as `/root` inside cBot containers. |
| `README.md` | Add a short "One-line VPS install" subsection under Quick Start pointing at the command above and the SSH-tunnel step. |

Not touched: `app/db.py` (`DEFAULT_PG_URL` stays as the fallback for the existing
production box; new installs always have `DATABASE_URL` in `.env`),
`scripts/recalibrate_live_risk.py`, `scripts/deploy_feature.sh`, `AGENTS.md`.

## Error handling

- Any step failure stops the script (`set -e`) and prints which step failed.
- `read_ssh_key` and `build_algos` are the two steps that must never be skipped
  silently; both abort explicitly with actionable messages.
- `harden_sshd` never reloads sshd on a failing `sshd -t`.
- The script never deletes user data: it does not drop the DB, does not overwrite
  an existing `.env`, does not remove `authorized_keys` entries.

## Testing

1. `bash -n scripts/install.sh` and `shellcheck scripts/install.sh` must pass
   (shellcheck installed locally via Homebrew if missing).
2. `scripts/backup_postgres.sh` gets a pytest that runs it with a fake `.env` and a
   stubbed `pg_dump` on `PATH`, asserting the parsed `PG*` variables and the output
   file name.
3. End-to-end: if Multipass or OrbStack is available on the dev machine, launch a
   clean Ubuntu 24.04 VM, run the script with `FORGE_SSH_KEY` set and
   `AGENTFX_REPO` pointing at the local checkout, then verify:
   `systemctl is-active agentfx`, `curl 127.0.0.1:8000/api/watchdog/status`,
   `ls cBot/*.algo` (3 files), `sudo -u forge docker ps` works, `ssh forge@vm`
   with the key works and password login is refused. If no VM tool is available,
   the user runs it on a throwaway VPS and we iterate on the log.
