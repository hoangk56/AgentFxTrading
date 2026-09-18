# VPS Install Script Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A single idempotent `scripts/install.sh` that turns a fresh Ubuntu 22.04/24.04 VPS into a running AgentFxTrading host (PostgreSQL 17, Docker, systemd service as user `forge`, three compiled `.algo` files) via `curl | sudo bash`.

**Architecture:** One self-contained bash script; every system step is a function that checks its own post-condition first so re-running is the upgrade path. Pure helpers (URL encoding, key validation, file rendering) are separated from system steps so they can be unit-tested from pytest by sourcing the script on macOS. `scripts/backup_postgres.sh` is rewritten to read `DATABASE_URL` from `.env` so the installer can wire it into cron without hard-coded secrets.

**Tech Stack:** bash (Ubuntu bash 5 on target; helpers must also run under macOS bash 3.2 for local tests), shellcheck, pytest (via `.venv/bin/pytest`), apt (PGDG + docker.com repos), systemd, ufw, `ghcr.io/spotware/ctrader-console`.

**Spec:** `docs/superpowers/specs/2026-09-18-vps-install-script-design.md`

## Global Constraints

- Target OS: Ubuntu **22.04** or **24.04** only; abort otherwise.
- Service user is `forge`, home `/home/forge`; repo at `/home/forge/AgentFxTrading`; cTrader home `/home/forge/ctrader` mounted as `/root` inside containers.
- Dashboard binds `127.0.0.1:8000` only. No nginx.
- The **only** interactive input is the SSH public key (`FORGE_SSH_KEY` env var or `/dev/tty` prompt). Everything else is generated or left as a placeholder.
- sshd: `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `PubkeyAuthentication yes`, `PermitRootLogin prohibit-password`. Drop-in file must be `/etc/ssh/sshd_config.d/00-agentfx.conf` (sshd takes the **first** match for a keyword, and cloud-init ships `50-cloud-init.conf` with `PasswordAuthentication yes`).
- PostgreSQL 17 from PGDG; role `agentfx`, db `agentfx`, password `openssl rand -hex 24`.
- The script never deletes user data: no DB drop, never overwrites an existing `.env`, never removes `authorized_keys` entries.
- `set -euo pipefail`; every step logged with `==> `; failing step name printed on error.
- All helpers unit-tested locally must avoid bash-4-only features (no `declare -A`, no `${var,,}`), because local tests run under macOS bash 3.2.
- Local test command: `.venv/bin/pytest -q` (baseline before this plan: 103 passed). Lint: `shellcheck scripts/install.sh scripts/backup_postgres.sh`.
- Commit messages end with `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

## File Structure

| File | Responsibility |
|---|---|
| `scripts/install.sh` (new) | The installer. Sections in order: prologue (config vars, logging, trap) → pure helpers → render functions → system steps → `main` → source guard. |
| `scripts/backup_postgres.sh` (rewrite) | Daily `pg_dump` using `DATABASE_URL` from `<project>/.env`; `PROJECT_ROOT` derived from its own path (overridable for tests). |
| `.env.example` (modify) | Add `CTRADER_HOME=/root` with explanation. |
| `README.md` (modify) | "One-line VPS install" subsection under Quick Start. |
| `tests/test_backup_script.py` (new) | Runs `backup_postgres.sh` against a fake `pg_dump` on `PATH`. |
| `tests/test_install_script.py` (new) | Sources `install.sh` and exercises helpers/renderers; checks `bash -n`, the source guard, and the non-root preflight. |

---

### Task 1: Rewrite `scripts/backup_postgres.sh` to read `DATABASE_URL` from `.env`

**Files:**
- Modify: `scripts/backup_postgres.sh` (full rewrite)
- Test: `tests/test_backup_script.py`

**Interfaces:**
- Consumes: `<PROJECT_ROOT>/.env` containing `DATABASE_URL=postgresql://...`
- Produces: `<PROJECT_ROOT>/backups/agentfx_YYYYmmdd_HHMMSS.sql.gz` and `<PROJECT_ROOT>/backups/backup.log`. Env override `PROJECT_ROOT` (used by tests and usable by cron).

- [ ] **Step 1: Write the failing tests**

Create `tests/test_backup_script.py`:

```python
import gzip
import os
import stat
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "backup_postgres.sh"
DB_URL = "postgresql://agentfx:kaz%40112358.@127.0.0.1:5432/agentfx"


def _make_fake_pg_dump(bin_dir: Path, args_file: Path) -> None:
    bin_dir.mkdir(parents=True, exist_ok=True)
    fake = bin_dir / "pg_dump"
    fake.write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$@\" > '{args_file}'\n"
        "echo 'FAKE DUMP'\n"
    )
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)


def _run(project_root: Path, bin_dir: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "PROJECT_ROOT": str(project_root)}
    return subprocess.run(["bash", str(SCRIPT)], capture_output=True, text=True, env=env)


def test_backup_uses_database_url_from_env_file(tmp_path):
    project = tmp_path / "proj"
    project.mkdir()
    (project / ".env").write_text(f"LLM_PROVIDER=qwen\nDATABASE_URL={DB_URL}\n")
    args_file = tmp_path / "pg_dump_args.txt"
    _make_fake_pg_dump(tmp_path / "bin", args_file)

    result = _run(project, tmp_path / "bin")

    assert result.returncode == 0, result.stderr
    dumps = sorted((project / "backups").glob("agentfx_*.sql.gz"))
    assert len(dumps) == 1
    with gzip.open(dumps[0], "rt") as fh:
        assert fh.read() == "FAKE DUMP\n"
    args = args_file.read_text().splitlines()
    assert f"--dbname={DB_URL}" in args
    assert "--clean" in args and "--if-exists" in args
    assert "SUCCESS" in (project / "backups" / "backup.log").read_text()


def test_backup_fails_without_database_url(tmp_path):
    project = tmp_path / "proj"
    project.mkdir()
    (project / ".env").write_text("LLM_PROVIDER=qwen\n")
    _make_fake_pg_dump(tmp_path / "bin", tmp_path / "args.txt")

    result = _run(project, tmp_path / "bin")

    assert result.returncode == 1
    assert list((project / "backups").glob("agentfx_*.sql.gz")) == []
    assert "DATABASE_URL" in (project / "backups" / "backup.log").read_text()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_backup_script.py -v`
Expected: both FAIL — the current script ignores `PROJECT_ROOT`, uses hard-coded `/root/AgentFxTrading/backups`, and calls `pg_dump` without `--dbname`.

- [ ] **Step 3: Rewrite the script**

Replace the whole content of `scripts/backup_postgres.sh` with:

```bash
#!/usr/bin/env bash
# =============================================================================
# Automated PostgreSQL Backup Script for AgentFxTrading
# Keeps compressed daily dumps and cleans up backups older than 14 days.
# Connection details come from DATABASE_URL in <project>/.env — nothing is
# hard-coded here. PROJECT_ROOT can be overridden via the environment.
# =============================================================================

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
ENV_FILE="${PROJECT_ROOT}/.env"
BACKUP_DIR="${PROJECT_ROOT}/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/agentfx_${TIMESTAMP}.sql.gz"
LOG_FILE="${BACKUP_DIR}/backup.log"

mkdir -p "${BACKUP_DIR}"

log() { echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] $*" >> "${LOG_FILE}"; }

# Last DATABASE_URL= line wins; surrounding quotes are stripped.
DATABASE_URL="$(grep -E '^DATABASE_URL=' "${ENV_FILE}" 2>/dev/null | tail -n1 | cut -d= -f2- | tr -d "\"'" || true)"
if [[ -z "${DATABASE_URL}" ]]; then
    log "Backup FAILED: DATABASE_URL not found in ${ENV_FILE}"
    exit 1
fi

log "Starting backup..."

# libpq accepts the URL directly (percent-encoded password included).
if pg_dump --dbname="${DATABASE_URL}" --clean --if-exists --no-owner --no-privileges | gzip > "${BACKUP_FILE}"; then
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    log "Backup SUCCESS: ${BACKUP_FILE} (${BACKUP_SIZE})"
else
    log "Backup FAILED!"
    rm -f "${BACKUP_FILE}"
    exit 1
fi

# Retention policy: remove backups older than 14 days
find "${BACKUP_DIR}" -type f -name "agentfx_*.sql.gz" -mtime +14 -delete
log "Cleaned up backups older than 14 days."
```

- [ ] **Step 4: Run tests and lint**

Run: `.venv/bin/pytest tests/test_backup_script.py -v && shellcheck scripts/backup_postgres.sh`
Expected: 2 passed; shellcheck prints nothing.

- [ ] **Step 5: Commit**

```bash
git add scripts/backup_postgres.sh tests/test_backup_script.py
git commit -m "fix(backup): read DATABASE_URL from .env instead of hard-coded credentials

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: `install.sh` skeleton, pure helpers, preflight, source guard

**Files:**
- Create: `scripts/install.sh`
- Test: `tests/test_install_script.py`

**Interfaces:**
- Produces (bash functions, all later tasks rely on these exact names):
  - `log "<msg>"` → prints `==> <msg>`
  - `step "<name>"` → sets `CURRENT_STEP` and logs it
  - `die "<msg>"` → prints `ERROR [<step>]: <msg>` to stderr, exit 1
  - `urlencode "<s>"` → prints percent-encoded string (unreserved chars `A-Za-z0-9.~_-` untouched)
  - `urldecode "<s>"` → inverse
  - `validate_ssh_key "<line>"` → return 0 iff `ssh-keygen -l` accepts it
  - `db_password_from_env "<path/.env>"` → prints the **decoded** password from `DATABASE_URL`, or nothing if file/var absent
  - `generate_password` → prints `openssl rand -hex 24`
  - `preflight` → root + Ubuntu 22.04/24.04 + systemd check
  - Config variables (env-overridable): `FORGE_USER`, `FORGE_GROUP`, `FORGE_HOME`, `REPO_DIR`, `CTRADER_HOME`, `AGENTFX_REPO`, `AGENTFX_BRANCH`, `CTRADER_IMAGE`, `DB_NAME`, `DB_USER`, `SERVICE_NAME`; mutable state `DB_PASSWORD`, `SSH_PUBLIC_KEY`.
  - A `# --- main ---` marker line; later tasks insert functions **above** it and add calls inside `main`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_install_script.py`:

```python
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "install.sh"


def run_fn(snippet: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Source install.sh (main is guarded) and run a bash snippet against it."""
    full_env = {**os.environ, **(env or {})}
    return subprocess.run(
        ["bash", "-c", f"source '{SCRIPT}'; {snippet}"],
        capture_output=True, text=True, env=full_env,
    )


def test_script_parses():
    assert subprocess.run(["bash", "-n", str(SCRIPT)]).returncode == 0


def test_running_directly_as_non_root_hits_preflight():
    if os.geteuid() == 0:
        pytest.skip("must run as non-root")
    result = subprocess.run(["bash", str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "Run as root" in result.stderr


def test_piped_into_bash_also_runs_main():
    if os.geteuid() == 0:
        pytest.skip("must run as non-root")
    result = subprocess.run(["bash", "-c", f"cat '{SCRIPT}' | bash"], capture_output=True, text=True)
    assert result.returncode == 1
    assert "Run as root" in result.stderr


def test_sourcing_does_not_run_main():
    result = run_fn("echo sourced-ok")
    assert result.returncode == 0
    assert result.stdout.strip() == "sourced-ok"


@pytest.mark.parametrize("raw,encoded", [
    ("kaz@112358.", "kaz%40112358."),
    ("abc-_.~09", "abc-_.~09"),
    ("p w:d/#?", "p%20w%3Ad%2F%23%3F"),
])
def test_urlencode(raw, encoded):
    result = run_fn(f"urlencode '{raw}'")
    assert result.stdout == encoded


@pytest.mark.parametrize("encoded,raw", [
    ("kaz%40112358.", "kaz@112358."),
    ("p%20w%3Ad%2F%23%3F", "p w:d/#?"),
])
def test_urldecode(encoded, raw):
    result = run_fn(f"urldecode '{encoded}'")
    assert result.stdout == raw


def test_validate_ssh_key_accepts_real_key(tmp_path):
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(tmp_path / "k")], check=True)
    pub = (tmp_path / "k.pub").read_text().strip()
    assert run_fn(f"validate_ssh_key '{pub}'").returncode == 0


def test_validate_ssh_key_rejects_garbage():
    assert run_fn("validate_ssh_key 'not a key at all'").returncode != 0


def test_db_password_from_env_decodes_password(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text('X=1\nDATABASE_URL="postgresql://agentfx:kaz%40112358.@127.0.0.1:5432/agentfx"\n')
    result = run_fn(f"db_password_from_env '{env_file}'")
    assert result.stdout == "kaz@112358."


def test_db_password_from_env_missing_file_or_var(tmp_path):
    assert run_fn(f"db_password_from_env '{tmp_path / 'nope'}'").stdout == ""
    env_file = tmp_path / ".env"
    env_file.write_text("LLM_PROVIDER=qwen\n")
    assert run_fn(f"db_password_from_env '{env_file}'").stdout == ""


def test_generate_password_is_48_hex_chars():
    out = run_fn("generate_password").stdout.strip()
    assert len(out) == 48
    int(out, 16)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_install_script.py -v`
Expected: all FAIL (script does not exist).

- [ ] **Step 3: Create the script skeleton**

Create `scripts/install.sh`:

```bash
#!/usr/bin/env bash
# =============================================================================
# AgentFxTrading — one-shot installer for a fresh Ubuntu 22.04 / 24.04 VPS
#
#   curl -fsSL https://raw.githubusercontent.com/kienphan/AgentFxTrading/main/scripts/install.sh | sudo bash
#
# Optional environment overrides:
#   FORGE_SSH_KEY   public key for the forge user (otherwise prompted on /dev/tty)
#   AGENTFX_REPO    git URL to clone   (default: upstream GitHub repo)
#   AGENTFX_BRANCH  branch to check out (default: main)
#
# Idempotent: every step checks its own post-condition first, so re-running the
# script is the upgrade path.
# Design: docs/superpowers/specs/2026-09-18-vps-install-script-design.md
# =============================================================================
set -euo pipefail

# --- configuration -----------------------------------------------------------
FORGE_USER="${FORGE_USER:-forge}"
FORGE_GROUP="${FORGE_GROUP:-$FORGE_USER}"
FORGE_HOME="${FORGE_HOME:-/home/${FORGE_USER}}"
REPO_DIR="${REPO_DIR:-${FORGE_HOME}/AgentFxTrading}"
CTRADER_HOME="${CTRADER_HOME:-${FORGE_HOME}/ctrader}"
AGENTFX_REPO="${AGENTFX_REPO:-https://github.com/kienphan/AgentFxTrading.git}"
AGENTFX_BRANCH="${AGENTFX_BRANCH:-main}"
CTRADER_IMAGE="${CTRADER_IMAGE:-ghcr.io/spotware/ctrader-console:latest}"
DB_NAME="agentfx"
DB_USER="agentfx"
SERVICE_NAME="agentfx"
DB_PASSWORD=""        # resolved by install_postgresql, consumed by write_env
SSH_PUBLIC_KEY=""     # resolved by read_ssh_key
export DEBIAN_FRONTEND=noninteractive
export NEEDRESTART_MODE=a   # Ubuntu 22.04: never pop the "restart services?" dialog

# --- logging -----------------------------------------------------------------
CURRENT_STEP="startup"
log()  { printf '==> %s\n' "$*"; }
step() { CURRENT_STEP="$1"; log "$1"; }
die()  { printf 'ERROR [%s]: %s\n' "$CURRENT_STEP" "$*" >&2; exit 1; }
on_error() {
  printf '\nInstall failed during step "%s" (line %s). Fix the issue and re-run; completed steps are skipped.\n' \
    "$CURRENT_STEP" "$1" >&2
}
trap 'on_error $LINENO' ERR

# --- pure helpers (unit-tested from tests/test_install_script.py) ------------
urlencode() {
  # usage: urlencode "<string>"  → percent-encodes everything except A-Za-z0-9.~_-
  local s="$1" out="" i c
  for (( i = 0; i < ${#s}; i++ )); do
    c="${s:i:1}"
    case "$c" in
      [a-zA-Z0-9.~_-]) out+="$c" ;;
      *) out+=$(printf '%%%02X' "'$c") ;;
    esac
  done
  printf '%s' "$out"
}

urldecode() {
  # usage: urldecode "<string>"  → reverses urlencode
  local s="${1//+/ }"
  printf '%b' "${s//%/\\x}"
}

validate_ssh_key() {
  # usage: validate_ssh_key "<public key line>"  → 0 iff ssh-keygen can fingerprint it
  local tmp rc=1
  tmp="$(mktemp)"
  printf '%s\n' "$1" > "$tmp"
  if ssh-keygen -l -f "$tmp" >/dev/null 2>&1; then rc=0; fi
  rm -f "$tmp"
  return "$rc"
}

db_password_from_env() {
  # usage: db_password_from_env "<path/.env>"  → prints decoded password from DATABASE_URL (or nothing)
  local env_file="$1" url pw
  [[ -f "$env_file" ]] || return 0
  url="$(grep -E '^DATABASE_URL=' "$env_file" | tail -n1 | cut -d= -f2- | tr -d "\"'" || true)"
  [[ -n "$url" ]] || return 0
  pw="${url#*://}"   # user:pass@host...
  pw="${pw#*:}"      # pass@host...
  pw="${pw%%@*}"     # pass (still percent-encoded, so '@' inside it is safe)
  urldecode "$pw"
}

generate_password() { openssl rand -hex 24; }

# --- system steps --------------------------------------------------------------
preflight() {
  step "Preflight checks"
  [[ "$(id -u)" -eq 0 ]] || die "Run as root:  curl -fsSL <url>/install.sh | sudo bash"
  [[ -r /etc/os-release ]] || die "Cannot read /etc/os-release"
  local os_id os_version
  os_id="$(. /etc/os-release && printf '%s' "${ID:-}")"
  os_version="$(. /etc/os-release && printf '%s' "${VERSION_ID:-}")"
  [[ "$os_id" == "ubuntu" ]] || die "Ubuntu only (detected: ${os_id:-unknown})"
  case "$os_version" in
    22.04|24.04) ;;
    *) die "Ubuntu 22.04 or 24.04 required (detected: ${os_version:-unknown})" ;;
  esac
  command -v systemctl >/dev/null || die "systemd is required"
  log "Ubuntu ${os_version} detected"
}

# --- main ---
main() {
  preflight
}

# Run main when executed (`bash install.sh`) or piped (`curl ... | bash`,
# where BASH_SOURCE is empty). Sourcing the file (tests) does not run main.
if [[ -z "${BASH_SOURCE[0]:-}" || "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
```

- [ ] **Step 4: Run tests and lint**

Run: `chmod +x scripts/install.sh && .venv/bin/pytest tests/test_install_script.py -v && shellcheck scripts/install.sh`
Expected: 14 passed; shellcheck prints nothing. (If shellcheck flags `SC1091` for `. /etc/os-release`, add `# shellcheck disable=SC1091` on the line above each `. /etc/os-release` — that is the only acceptable suppression.)

- [ ] **Step 5: Commit**

```bash
git add scripts/install.sh tests/test_install_script.py
git commit -m "feat(install): add installer skeleton with tested helpers and preflight

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: Render functions, `write_env`, and `.env.example` `CTRADER_HOME`

**Files:**
- Modify: `scripts/install.sh` (insert above `# --- main ---`)
- Modify: `.env.example` (append at end)
- Test: `tests/test_install_script.py` (append)

**Interfaces:**
- Consumes: `urlencode`, `step`, `log`, config vars from Task 2.
- Produces:
  - `render_env "<.env.example>" "<database_url>" "<ctrader_home>"` → prints new `.env` content
  - `write_env` → creates/updates `${REPO_DIR}/.env` using `DB_PASSWORD`, owned by `${FORGE_USER}:${FORGE_GROUP}`, mode 0600
  - `render_systemd_unit` → prints unit file
  - `render_sshd_dropin` → prints sshd drop-in
  - `render_backup_cron` → prints one cron.d line

- [ ] **Step 1: Append `CTRADER_HOME` to `.env.example`**

Append to the end of `.env.example`:

```bash

# =============================================================================
# cTrader container home
# =============================================================================
# Host directory mounted as /root inside every cBot container. It holds
# ctrader_data/ (cTID password files) and cAlgo/ (ctrader-console build output).
# The VPS installer (scripts/install.sh) sets this to /home/forge/ctrader.
CTRADER_HOME=/root
```

- [ ] **Step 2: Write the failing tests**

Append to `tests/test_install_script.py`:

```python
DB_URL = "postgresql://agentfx:kaz%40112358.@127.0.0.1:5432/agentfx"


def _env_for_write(tmp_path: Path) -> dict:
    """Point the script at a throwaway repo dir and at the current user so chown works."""
    repo = tmp_path / "AgentFxTrading"
    repo.mkdir(exist_ok=True)
    return {
        "FORGE_USER": subprocess.check_output(["id", "-un"], text=True).strip(),
        "FORGE_GROUP": subprocess.check_output(["id", "-gn"], text=True).strip(),
        "FORGE_HOME": str(tmp_path),
        "REPO_DIR": str(repo),
        "CTRADER_HOME": str(tmp_path / "ctrader"),
    }


def test_render_env_replaces_placeholders_and_keeps_rest(tmp_path):
    example = tmp_path / ".env.example"
    example.write_text(
        "LLM_PROVIDER=qwen\n"
        "# DATABASE_URL=postgresql://agentfx:old@127.0.0.1:5432/agentfx\n"
        "CTRADER_HOME=/root\n"
    )
    out = run_fn(f"render_env '{example}' '{DB_URL}' /home/forge/ctrader").stdout
    lines = out.splitlines()
    assert "LLM_PROVIDER=qwen" in lines
    assert f"DATABASE_URL={DB_URL}" in lines
    assert "CTRADER_HOME=/home/forge/ctrader" in lines
    assert not any(l.startswith("# DATABASE_URL") for l in lines)
    assert lines.count("CTRADER_HOME=/home/forge/ctrader") == 1
    assert "CTRADER_HOME=/root" not in lines


def test_write_env_creates_file_from_example(tmp_path):
    env = _env_for_write(tmp_path)
    (Path(env["REPO_DIR"]) / ".env.example").write_text("LLM_PROVIDER=qwen\n# DATABASE_URL=x\nCTRADER_HOME=/root\n")
    result = run_fn("DB_PASSWORD='kaz@112358.'; write_env", env)
    assert result.returncode == 0, result.stderr
    env_file = Path(env["REPO_DIR"]) / ".env"
    content = env_file.read_text().splitlines()
    assert f"DATABASE_URL={DB_URL}" in content
    assert f"CTRADER_HOME={env['CTRADER_HOME']}" in content
    assert "LLM_PROVIDER=qwen" in content
    assert oct(env_file.stat().st_mode & 0o777) == "0o600"


def test_write_env_leaves_existing_file_alone_but_fills_missing_keys(tmp_path):
    env = _env_for_write(tmp_path)
    env_file = Path(env["REPO_DIR"]) / ".env"
    env_file.write_text("LLM_PROVIDER=openai\nOPENAI_API_KEY=sk-real\n")
    result = run_fn("DB_PASSWORD='kaz@112358.'; write_env", env)
    assert result.returncode == 0, result.stderr
    content = env_file.read_text().splitlines()
    assert content[0] == "LLM_PROVIDER=openai"
    assert "OPENAI_API_KEY=sk-real" in content
    assert f"DATABASE_URL={DB_URL}" in content
    assert f"CTRADER_HOME={env['CTRADER_HOME']}" in content


def test_write_env_is_idempotent_when_complete(tmp_path):
    env = _env_for_write(tmp_path)
    env_file = Path(env["REPO_DIR"]) / ".env"
    original = f"LLM_PROVIDER=qwen\nDATABASE_URL={DB_URL}\nCTRADER_HOME={env['CTRADER_HOME']}\n"
    env_file.write_text(original)
    run_fn("DB_PASSWORD='different'; write_env", env)
    assert env_file.read_text() == original


def test_render_systemd_unit():
    out = run_fn("render_systemd_unit", {"FORGE_USER": "forge", "FORGE_HOME": "/home/forge"}).stdout
    assert "User=forge" in out
    assert "Group=forge" in out
    assert "WorkingDirectory=/home/forge/AgentFxTrading" in out
    assert "ExecStart=/home/forge/AgentFxTrading/.venv/bin/uvicorn app.server:app --host 127.0.0.1 --port 8000" in out
    assert "After=network-online.target postgresql.service docker.service" in out
    assert "Restart=always" in out
    assert "WantedBy=multi-user.target" in out


def test_render_sshd_dropin():
    out = run_fn("render_sshd_dropin").stdout.splitlines()
    assert "PasswordAuthentication no" in out
    assert "KbdInteractiveAuthentication no" in out
    assert "PubkeyAuthentication yes" in out
    assert "PermitRootLogin prohibit-password" in out


def test_render_backup_cron():
    out = run_fn("render_backup_cron", {"FORGE_USER": "forge", "FORGE_HOME": "/home/forge"}).stdout
    assert out == "0 3 * * * forge /home/forge/AgentFxTrading/scripts/backup_postgres.sh\n"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_install_script.py -v -k "render or write_env"`
Expected: 8 FAIL with `command not found`.

- [ ] **Step 4: Add the functions to `install.sh`**

Insert immediately above the `# --- main ---` line:

```bash
# --- render helpers ------------------------------------------------------------
render_env() {
  # usage: render_env "<.env.example>" "<database_url>" "<ctrader_home>"  → prints a fresh .env
  local example="$1" db_url="$2" ctrader_home="$3"
  # Drop the template's DATABASE_URL / CTRADER_HOME lines (commented or not), then append real values.
  grep -vE '^#? ?(DATABASE_URL|CTRADER_HOME)=' "$example" || true
  printf '\nDATABASE_URL=%s\n' "$db_url"
  printf 'CTRADER_HOME=%s\n' "$ctrader_home"
}

render_systemd_unit() {
  cat <<EOF
[Unit]
Description=AgentFxTrading FastAPI server
After=network-online.target postgresql.service docker.service
Wants=network-online.target

[Service]
User=${FORGE_USER}
Group=${FORGE_GROUP}
WorkingDirectory=${REPO_DIR}
ExecStart=${REPO_DIR}/.venv/bin/uvicorn app.server:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
}

render_sshd_dropin() {
  cat <<'EOF'
# Managed by AgentFxTrading scripts/install.sh — key-only SSH.
# Named 00-* on purpose: sshd uses the FIRST value it sees for a keyword and
# cloud images ship 50-cloud-init.conf with PasswordAuthentication yes.
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
PermitRootLogin prohibit-password
EOF
}

render_backup_cron() {
  printf '0 3 * * * %s %s/scripts/backup_postgres.sh\n' "$FORGE_USER" "$REPO_DIR"
}

write_env() {
  step "Writing ${REPO_DIR}/.env"
  local env_file="${REPO_DIR}/.env" db_url
  db_url="postgresql://${DB_USER}:$(urlencode "$DB_PASSWORD")@127.0.0.1:5432/${DB_NAME}"
  if [[ -f "$env_file" ]]; then
    log ".env already exists — keeping it"
    if ! grep -qE '^DATABASE_URL=' "$env_file"; then
      printf 'DATABASE_URL=%s\n' "$db_url" >> "$env_file"
      log "Appended DATABASE_URL"
    fi
    if ! grep -qE '^CTRADER_HOME=' "$env_file"; then
      printf 'CTRADER_HOME=%s\n' "$CTRADER_HOME" >> "$env_file"
      log "Appended CTRADER_HOME=${CTRADER_HOME}"
    fi
  else
    render_env "${REPO_DIR}/.env.example" "$db_url" "$CTRADER_HOME" > "$env_file"
    log "Created .env with DATABASE_URL and CTRADER_HOME (LLM keys left as placeholders)"
  fi
  chown "${FORGE_USER}:${FORGE_GROUP}" "$env_file"
  chmod 0600 "$env_file"
}

```

- [ ] **Step 5: Run the full test file and lint**

Run: `.venv/bin/pytest tests/test_install_script.py -v && shellcheck scripts/install.sh`
Expected: 22 passed; shellcheck clean.

- [ ] **Step 6: Commit**

```bash
git add scripts/install.sh tests/test_install_script.py .env.example
git commit -m "feat(install): add .env/systemd/sshd/cron renderers and CTRADER_HOME setting

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: SSH key input, base packages, forge user, sshd hardening

**Files:**
- Modify: `scripts/install.sh` (insert above `# --- main ---`; extend `main`)

**Interfaces:**
- Consumes: `validate_ssh_key`, `render_sshd_dropin`, `die`, `step`, `log`, `SSH_PUBLIC_KEY`, `FORGE_*`.
- Produces: `read_ssh_key`, `install_base_packages`, `apt_install <pkgs...>`, `create_forge_user`, `harden_sshd`.

These steps need root and Ubuntu; they are verified by shellcheck here and by the VPS run in Task 8.

- [ ] **Step 1: Add the functions**

Insert immediately above `# --- main ---`:

```bash
read_ssh_key() {
  step "SSH public key for user ${FORGE_USER}"
  local key="${FORGE_SSH_KEY:-}"
  if [[ -z "$key" ]]; then
    [[ -r /dev/tty ]] || die "FORGE_SSH_KEY is not set and there is no terminal to prompt on. Re-run with FORGE_SSH_KEY='ssh-ed25519 AAAA... you@laptop'"
    printf 'Paste the SSH public key that will log in as %s (one line, e.g. "ssh-ed25519 AAAA... you@laptop"):\n> ' "$FORGE_USER" > /dev/tty
    IFS= read -r key < /dev/tty
  fi
  key="$(printf '%s' "$key" | tr -d '\r' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
  [[ -n "$key" ]] || die "SSH public key is empty — refusing to continue because password login will be disabled"
  validate_ssh_key "$key" || die "Not a valid SSH public key: ${key:0:40}..."
  SSH_PUBLIC_KEY="$key"
  log "Key accepted (${key%% *})"
}

apt_install() { apt-get install -y -q "$@"; }

install_base_packages() {
  step "Installing base packages"
  apt-get update -q
  apt_install git curl ca-certificates gnupg lsb-release openssl cron ufw \
    python3 python3-venv python3-dev build-essential libpq-dev
}

create_forge_user() {
  step "Creating user ${FORGE_USER}"
  if id "$FORGE_USER" >/dev/null 2>&1; then
    log "User ${FORGE_USER} already exists"
  else
    adduser --disabled-password --gecos "" "$FORGE_USER"
  fi
  usermod -aG sudo "$FORGE_USER"
  printf '%s ALL=(ALL) NOPASSWD:ALL\n' "$FORGE_USER" > "/etc/sudoers.d/${FORGE_USER}"
  chmod 0440 "/etc/sudoers.d/${FORGE_USER}"
  visudo -cf "/etc/sudoers.d/${FORGE_USER}" >/dev/null || die "Generated sudoers file is invalid"

  install -d -m 0700 -o "$FORGE_USER" -g "$FORGE_GROUP" "${FORGE_HOME}/.ssh"
  local auth="${FORGE_HOME}/.ssh/authorized_keys"
  touch "$auth"
  if grep -qxF "$SSH_PUBLIC_KEY" "$auth"; then
    log "Key already present in authorized_keys"
  else
    printf '%s\n' "$SSH_PUBLIC_KEY" >> "$auth"
    log "Key added to authorized_keys"
  fi
  chown "${FORGE_USER}:${FORGE_GROUP}" "$auth"
  chmod 0600 "$auth"
}

harden_sshd() {
  step "Hardening sshd (key-only login)"
  grep -qxF "$SSH_PUBLIC_KEY" "${FORGE_HOME}/.ssh/authorized_keys" \
    || die "authorized_keys does not contain the key — refusing to disable password login"
  install -d -m 0755 /etc/ssh/sshd_config.d
  if ! grep -qE '^Include /etc/ssh/sshd_config\.d/\*\.conf' /etc/ssh/sshd_config; then
    sed -i '1i Include /etc/ssh/sshd_config.d/*.conf' /etc/ssh/sshd_config
  fi
  render_sshd_dropin > /etc/ssh/sshd_config.d/00-agentfx.conf
  sshd -t || die "sshd -t failed; NOT reloading. Inspect /etc/ssh/sshd_config.d/00-agentfx.conf"
  systemctl reload ssh 2>/dev/null || systemctl restart ssh
  log "Password authentication disabled; root login is key-only"
}

```

- [ ] **Step 2: Extend `main`**

Replace the `main` body with:

```bash
main() {
  preflight
  read_ssh_key
  install_base_packages
  create_forge_user
  harden_sshd
}
```

- [ ] **Step 3: Lint and re-run the local tests**

Run: `shellcheck scripts/install.sh && .venv/bin/pytest tests/test_install_script.py -q`
Expected: shellcheck clean; 22 passed (sourcing still does not run main; preflight test still exits 1 before touching anything).

- [ ] **Step 4: Commit**

```bash
git add scripts/install.sh
git commit -m "feat(install): ssh key input, base packages, forge user with key-only sshd

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: PostgreSQL 17 and Docker CE

**Files:**
- Modify: `scripts/install.sh` (insert above `# --- main ---`; extend `main`)

**Interfaces:**
- Consumes: `db_password_from_env`, `generate_password`, `apt_install`, `DB_*`, `REPO_DIR`, `FORGE_USER`.
- Produces: `install_postgresql` (sets `DB_PASSWORD`), `install_docker`.

- [ ] **Step 1: Add the functions**

Insert immediately above `# --- main ---`:

```bash
install_postgresql() {
  step "Installing PostgreSQL 17"
  if dpkg -s postgresql-17 >/dev/null 2>&1; then
    log "postgresql-17 already installed"
  else
    install -d /usr/share/postgresql-common/pgdg
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \
      -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc
    printf 'deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt %s-pgdg main\n' \
      "$(lsb_release -cs)" > /etc/apt/sources.list.d/pgdg.list
    apt-get update -q
    apt_install postgresql-17
  fi
  systemctl enable --now postgresql

  # Password: reuse the one in an existing .env (re-run), otherwise generate.
  # The role password is always set to match, so DB and .env never disagree.
  DB_PASSWORD="$(db_password_from_env "${REPO_DIR}/.env")"
  if [[ -n "$DB_PASSWORD" ]]; then
    log "Reusing database password from existing .env"
  else
    DB_PASSWORD="$(generate_password)"
    log "Generated a new database password"
  fi
  local pw_sql
  pw_sql="$(printf '%s' "$DB_PASSWORD" | sed "s/'/''/g")"

  if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'" | grep -q 1; then
    sudo -u postgres psql -qc "ALTER ROLE ${DB_USER} WITH LOGIN PASSWORD '${pw_sql}'"
    log "Role ${DB_USER} exists — password synced"
  else
    sudo -u postgres psql -qc "CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD '${pw_sql}'"
    log "Role ${DB_USER} created"
  fi
  if sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -q 1; then
    log "Database ${DB_NAME} exists"
  else
    sudo -u postgres createdb -O "$DB_USER" "$DB_NAME"
    log "Database ${DB_NAME} created"
  fi
}

install_docker() {
  step "Installing Docker CE"
  if dpkg -s docker-ce >/dev/null 2>&1; then
    log "docker-ce already installed"
  else
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
    printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu %s stable\n' \
      "$(dpkg --print-architecture)" "$(lsb_release -cs)" > /etc/apt/sources.list.d/docker.list
    apt-get update -q
    apt_install docker-ce docker-ce-cli containerd.io
  fi
  systemctl enable --now docker
  usermod -aG docker "$FORGE_USER"
  log "User ${FORGE_USER} is in the docker group"
}

```

- [ ] **Step 2: Extend `main`**

Add after `harden_sshd`:

```bash
  install_postgresql
  install_docker
```

- [ ] **Step 3: Lint and re-run the local tests**

Run: `shellcheck scripts/install.sh && .venv/bin/pytest tests/test_install_script.py -q`
Expected: shellcheck clean; 22 passed.

- [ ] **Step 4: Commit**

```bash
git add scripts/install.sh
git commit -m "feat(install): install PostgreSQL 17 (PGDG) and Docker CE, provision agentfx role/db

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 6: Repo checkout, venv, cTrader home, `.algo` builds

**Files:**
- Modify: `scripts/install.sh` (insert above `# --- main ---`; extend `main`)

**Interfaces:**
- Consumes: `write_env` (Task 3), `REPO_DIR`, `CTRADER_HOME`, `CTRADER_IMAGE`, `AGENTFX_REPO`, `AGENTFX_BRANCH`, `FORGE_*`.
- Produces: `run_as_forge <cmd...>`, `clone_repo`, `setup_venv`, `prepare_ctrader_home`, `ctrader_console <args...>`, `build_algo <BotName>`, `build_algos`.

- [ ] **Step 1: Add the functions**

Insert immediately above `# --- main ---`:

```bash
run_as_forge() { sudo -u "$FORGE_USER" -H "$@"; }

clone_repo() {
  step "Fetching repository into ${REPO_DIR}"
  if [[ -d "${REPO_DIR}/.git" ]]; then
    run_as_forge git -C "$REPO_DIR" fetch --quiet origin "$AGENTFX_BRANCH"
    run_as_forge git -C "$REPO_DIR" checkout --quiet "$AGENTFX_BRANCH"
    run_as_forge git -C "$REPO_DIR" pull --ff-only --quiet origin "$AGENTFX_BRANCH"
    log "Updated existing checkout (${AGENTFX_BRANCH})"
  else
    run_as_forge git clone --quiet --branch "$AGENTFX_BRANCH" "$AGENTFX_REPO" "$REPO_DIR"
    log "Cloned ${AGENTFX_REPO} (${AGENTFX_BRANCH})"
  fi
}

setup_venv() {
  step "Python virtualenv and dependencies"
  [[ -x "${REPO_DIR}/.venv/bin/python" ]] || run_as_forge python3 -m venv "${REPO_DIR}/.venv"
  run_as_forge "${REPO_DIR}/.venv/bin/pip" install -q --upgrade pip
  run_as_forge "${REPO_DIR}/.venv/bin/pip" install -q -r "${REPO_DIR}/requirements.txt"
  log "Dependencies installed"
}

prepare_ctrader_home() {
  step "Preparing ${CTRADER_HOME}"
  install -d -m 0755 -o "$FORGE_USER" -g "$FORGE_GROUP" "$CTRADER_HOME"
  install -d -m 0700 -o "$FORGE_USER" -g "$FORGE_GROUP" "${CTRADER_HOME}/ctrader_data"
  log "ctrader_data/ ready for cTID password files"
}

ctrader_console() {
  # Runs the Spotware CLI with the same mounts every cBot container uses.
  docker run --rm -v "${REPO_DIR}:/workspace" -v "${CTRADER_HOME}:/root" "$CTRADER_IMAGE" "$@"
}

build_algo() {
  # usage: build_algo <BotName>   compiles cBot/<BotName>.cs → cBot/<BotName>.algo
  local name="$1"
  local src="${REPO_DIR}/cBot/${name}.cs"
  local out="${REPO_DIR}/cBot/${name}.algo"
  local robots="${CTRADER_HOME}/cAlgo/Sources/Robots"
  local csproj="${robots}/${name}/${name}/${name}.csproj"
  [[ -f "$src" ]] || die "Missing cBot source: ${src}"
  if [[ -f "$out" && "$out" -nt "$src" ]]; then
    log "${name}.algo is newer than ${name}.cs — skipping"
    return 0
  fi
  [[ -f "$csproj" ]] || ctrader_console create cbot "$name"
  cp "$src" "${robots}/${name}/${name}/${name}.cs"
  ctrader_console build "/root/cAlgo/Sources/Robots/${name}/${name}/${name}.csproj"
  cp "${robots}/${name}.algo" "$out"
  log "Built ${name}.algo"
}

build_algos() {
  step "Building cBot .algo packages (this pulls ${CTRADER_IMAGE})"
  docker pull -q "$CTRADER_IMAGE"
  local name
  for name in AiAgentBot AsianRangeJudasSweepBot FlowRsiBot; do
    build_algo "$name"
  done
  # The console container runs as root, so hand everything back to forge.
  chown -R "${FORGE_USER}:${FORGE_GROUP}" "$CTRADER_HOME" "${REPO_DIR}/cBot"
}

```

- [ ] **Step 2: Extend `main`**

Add after `install_docker`:

```bash
  clone_repo
  setup_venv
  write_env
  prepare_ctrader_home
  build_algos
```

- [ ] **Step 3: Lint and re-run the local tests**

Run: `shellcheck scripts/install.sh && .venv/bin/pytest tests/test_install_script.py -q`
Expected: shellcheck clean; 22 passed.

- [ ] **Step 4: Commit**

```bash
git add scripts/install.sh
git commit -m "feat(install): clone repo, create venv, write .env, build the three .algo packages

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 7: systemd service, backup cron, ufw, summary, README section

**Files:**
- Modify: `scripts/install.sh` (insert above `# --- main ---`; finish `main`)
- Modify: `README.md` (insert before `### 1. Install Python Dependencies`, currently line 190)

**Interfaces:**
- Consumes: `render_systemd_unit`, `render_backup_cron` (Task 3), `SERVICE_NAME`, `REPO_DIR`, `FORGE_USER`, `DB_*`, `CTRADER_HOME`.
- Produces: `install_systemd_unit`, `install_backup_cron`, `configure_firewall`, `print_summary`; final `main`.

- [ ] **Step 1: Add the functions**

Insert immediately above `# --- main ---`:

```bash
install_systemd_unit() {
  step "Installing systemd service ${SERVICE_NAME}"
  render_systemd_unit > "/etc/systemd/system/${SERVICE_NAME}.service"
  systemctl daemon-reload
  systemctl enable "$SERVICE_NAME" >/dev/null
  systemctl restart "$SERVICE_NAME"
  local i
  for i in $(seq 1 30); do
    if curl -fs http://127.0.0.1:8000/api/watchdog/status >/dev/null 2>&1; then
      log "Service is answering on 127.0.0.1:8000 (after ${i}s)"
      return 0
    fi
    sleep 1
  done
  journalctl -u "$SERVICE_NAME" -n 50 --no-pager >&2 || true
  die "Service did not answer within 30s — see journal output above"
}

install_backup_cron() {
  step "Installing daily database backup"
  chmod +x "${REPO_DIR}/scripts/backup_postgres.sh"
  render_backup_cron > /etc/cron.d/agentfx-backup
  chmod 0644 /etc/cron.d/agentfx-backup
  log "Backups run daily at 03:00 into ${REPO_DIR}/backups"
}

configure_firewall() {
  step "Configuring ufw"
  ufw allow OpenSSH >/dev/null
  ufw --force enable >/dev/null
  log "ufw enabled: only OpenSSH is allowed inbound"
}

print_summary() {
  local ip
  ip="$(curl -fs4 --max-time 5 https://api.ipify.org 2>/dev/null || hostname -I | awk '{print $1}')"
  cat <<EOF

=============================================================================
 AgentFxTrading installed
=============================================================================
 User         : ${FORGE_USER}  (passwordless sudo, SSH key only)
 Project      : ${REPO_DIR}
 Service      : systemctl status ${SERVICE_NAME}
 Database     : postgresql://${DB_USER}:***@127.0.0.1:5432/${DB_NAME}  (full URL in .env)
 cBots built  : ${REPO_DIR}/cBot/{AiAgentBot,AsianRangeJudasSweepBot,FlowRsiBot}.algo
 cTrader home : ${CTRADER_HOME}  (mounted as /root inside cBot containers)

 Next steps
 1. Open the dashboard through an SSH tunnel from your machine:
      ssh -L 8000:127.0.0.1:8000 ${FORGE_USER}@${ip}
    then browse http://127.0.0.1:8000
 2. Put your LLM API key in ${REPO_DIR}/.env
    (LLM_PROVIDER, DASHSCOPE_API_KEY, ...), then:  sudo systemctl restart ${SERVICE_NAME}
 3. Add your cTrader account and start bots from
    Dashboard → Docker Bot Management → Setup Instances.
 Re-running this installer is safe; it updates the checkout and rebuilds bots.
=============================================================================
EOF
}

```

- [ ] **Step 2: Finish `main`**

Replace the `main` function with its final form:

```bash
main() {
  preflight
  read_ssh_key
  install_base_packages
  create_forge_user
  harden_sshd
  install_postgresql
  install_docker
  clone_repo
  setup_venv
  write_env
  prepare_ctrader_home
  build_algos
  install_systemd_unit
  install_backup_cron
  configure_firewall
  print_summary
}
```

- [ ] **Step 3: Add the README section**

In `README.md`, insert the following block immediately before the line `### 1. Install Python Dependencies` (the block ends with a blank line so the existing heading keeps its spacing). The outer fence below uses four backticks only so the plan renders; the inserted text uses the normal three-backtick fences shown:

````markdown
### 🚀 One-line VPS install (Ubuntu 22.04 / 24.04)

On a fresh VPS, as root, run:

```bash
curl -fsSL https://raw.githubusercontent.com/kienphan/AgentFxTrading/main/scripts/install.sh | sudo bash
```

It asks for one thing — the SSH public key that will log in as the `forge` user — and then installs PostgreSQL 17, Docker, the FastAPI server as a systemd service (`agentfx.service`, user `forge`, bound to `127.0.0.1:8000`), compiles the three cBot `.algo` packages, and enables a daily database backup. Password SSH login is disabled.

Afterwards open the dashboard through a tunnel:

```bash
ssh -L 8000:127.0.0.1:8000 forge@YOUR_VPS_IP
```

then browse `http://127.0.0.1:8000`, put your LLM key in `/home/forge/AgentFxTrading/.env`, and `sudo systemctl restart agentfx`.

Re-running the same command later is safe — it pulls the latest code and rebuilds the bots. To skip the prompt, set `FORGE_SSH_KEY="ssh-ed25519 AAAA..."` before the command.

> The installer keeps the cTrader home at `/home/forge/ctrader` (mounted as `/root` inside containers). If you copy a `docker run` command from the sections below onto an installed VPS, replace `-v /root:/root` with `-v /home/forge/ctrader:/root`.

````

- [ ] **Step 4: Lint, run the whole suite**

Run: `shellcheck scripts/install.sh scripts/backup_postgres.sh && .venv/bin/pytest -q`
Expected: shellcheck clean; `127 passed` (103 baseline + 2 backup + 22 install).

- [ ] **Step 5: Commit**

```bash
git add scripts/install.sh README.md
git commit -m "feat(install): systemd service, backup cron, ufw, summary; document one-line VPS install

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 8: End-to-end verification on a throwaway Ubuntu VPS

No VM tooling (Multipass/OrbStack/Docker) exists on the dev machine, so this task is a manual run on a disposable VPS. It is the only place the system steps execute for real; do not mark Phase 1 complete without it.

**Files:** none (findings feed fixes back into `scripts/install.sh`, each fix committed with its own message).

- [ ] **Step 1: Push the branch so the raw URL serves the new script**

```bash
git push origin main
```

(If working on a feature branch, use its name in the `curl` URL below instead of `main`, and set `AGENTFX_BRANCH=<branch>`.)

- [ ] **Step 2: Create a fresh Ubuntu 24.04 VPS** (any provider; 2 vCPU / 4 GB is enough for the .NET build). Note its IP and log in as root.

- [ ] **Step 3: Run the installer**

```bash
FORGE_SSH_KEY="$(cat ~/.ssh/id_ed25519.pub)" bash -c 'curl -fsSL https://raw.githubusercontent.com/kienphan/AgentFxTrading/main/scripts/install.sh | sudo -E bash'
```

Expected: every step prints `==> ...`, the three `Built <Name>.algo` lines appear, `Service is answering on 127.0.0.1:8000`, and the summary block. Total time roughly 5–10 minutes (mostly the .NET builds).

- [ ] **Step 4: Verify from a second terminal on your machine**

```bash
ssh forge@VPS_IP 'sudo -n true && echo SUDO_OK; systemctl is-active agentfx postgresql docker; ls -la ~/AgentFxTrading/cBot/*.algo; docker ps >/dev/null && echo DOCKER_OK; curl -s 127.0.0.1:8000/api/watchdog/status | head -c 200; sudo ufw status | head -3; cat /etc/cron.d/agentfx-backup; grep -c "^DATABASE_URL=" ~/AgentFxTrading/.env'
```

Expected: `SUDO_OK`, three `active`, three `.algo` files owned by `forge`, `DOCKER_OK`, JSON from the watchdog endpoint, `Status: active`, the cron line, `1`.

- [ ] **Step 5: Verify password login is refused**

```bash
ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password forge@VPS_IP
```

Expected: `Permission denied (publickey)` without a password prompt. Also confirm `ssh root@VPS_IP` still works with your key.

- [ ] **Step 6: Verify the backup script works against the real database**

```bash
ssh forge@VPS_IP '~/AgentFxTrading/scripts/backup_postgres.sh && tail -2 ~/AgentFxTrading/backups/backup.log && ls ~/AgentFxTrading/backups/'
```

Expected: a `Backup SUCCESS` line and one `agentfx_*.sql.gz` file.

- [ ] **Step 7: Verify idempotency — run the installer a second time**

Repeat Step 3. Expected: no errors; lines such as `User forge already exists`, `.env already exists — keeping it`, `Reusing database password from existing .env`, `<Name>.algo is newer than <Name>.cs — skipping`; the service restarts and answers again. `.env` content must be byte-identical to before (`md5sum` it before and after).

- [ ] **Step 8: Fix anything that failed**

For each failure: reproduce on the VPS, patch `scripts/install.sh` locally, run `shellcheck scripts/install.sh && .venv/bin/pytest tests/test_install_script.py -q`, commit with `fix(install): <what>`, push, and re-run from Step 3. Destroy the VPS when done.
