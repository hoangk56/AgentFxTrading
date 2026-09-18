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

# --- main ---
main() {
  preflight
}

# Run main when executed (`bash install.sh`) or piped (`curl ... | bash`,
# where BASH_SOURCE is empty). Sourcing the file (tests) does not run main.
if [[ -z "${BASH_SOURCE[0]:-}" || "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
