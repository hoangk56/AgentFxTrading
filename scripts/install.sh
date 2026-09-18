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
set -Eeuo pipefail

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
  # shellcheck disable=SC1091
  os_id="$(. /etc/os-release && printf '%s' "${ID:-}")"
  # shellcheck disable=SC1091
  os_version="$(. /etc/os-release && printf '%s' "${VERSION_ID:-}")"
  [[ "$os_id" == "ubuntu" ]] || die "Ubuntu only (detected: ${os_id:-unknown})"
  case "$os_version" in
    22.04|24.04) ;;
    *) die "Ubuntu 22.04 or 24.04 required (detected: ${os_version:-unknown})" ;;
  esac
  command -v systemctl >/dev/null || die "systemd is required"
  log "Ubuntu ${os_version} detected"
}

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

# --- main ---
main() {
  preflight
  read_ssh_key
  install_base_packages
  create_forge_user
  harden_sshd
}

# Run main when executed (`bash install.sh`) or piped (`curl ... | bash`,
# where BASH_SOURCE is empty). Sourcing the file (tests) does not run main.
if [[ -z "${BASH_SOURCE[0]:-}" || "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
