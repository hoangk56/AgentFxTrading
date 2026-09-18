"""
cTrader account service behind /api/ctrader-accounts (the dashboard's
"Setup Instances" screen): input validation, slug derivation, the cTID
password file under $CTRADER_HOME/ctrader_data, and the ctrader_accounts row.

The password only ever passes through create_ctrader_account on its way to
disk; it is never logged, stored, or returned.
"""
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

from app.accounts import AccountRegistry

logger = logging.getLogger(__name__)

SLUG_MAX_LEN = 24
LABEL_MAX_LEN = 40
CONTAINER_CREDENTIALS_DIR = "/root/ctrader_data"   # every container mounts CTRADER_HOME as /root


class AccountValidationError(ValueError):
    """Bad client input -> HTTP 422."""


class DuplicateSlugError(ValueError):
    """An account with the same slug already exists -> HTTP 409."""


def ctrader_home() -> str:
    """Host directory mounted as /root in every cBot container (Phase 1 writes it to .env)."""
    return os.environ.get("CTRADER_HOME", "").strip() or "/root"


def slugify(account_type: str, label: str) -> str:
    """`<type>-<label>` in [a-z0-9-], max 24 chars: ('live', 'IC Markets #2') -> 'live-ic-markets-2'."""
    body = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return f"{account_type}-{body}"[:SLUG_MAX_LEN].rstrip("-")


def validate_account_input(label: str, ctid_email: str, password: str, account_number: str, account_type: str) -> None:
    if account_type not in ("live", "demo"):
        raise AccountValidationError("account_type must be 'live' or 'demo'")
    if not 1 <= len(label) <= LABEL_MAX_LEN:
        raise AccountValidationError(f"label must be 1-{LABEL_MAX_LEN} characters")
    if '"' in label or "\n" in label or "\r" in label:
        raise AccountValidationError("label must not contain quotes or newlines")
    if not re.search(r"[a-z0-9]", label.lower()):
        raise AccountValidationError("label must contain at least one letter or digit")
    if account_type == "demo" and "live" in slugify(account_type, label):
        raise AccountValidationError("a demo account label must not contain 'live' (the dashboard uses it to detect live bots)")
    if "@" not in ctid_email or re.search(r'[\s"]', ctid_email):
        raise AccountValidationError("ctid_email must be an email address")
    if not account_number.isdigit():
        raise AccountValidationError("account_number must contain digits only")
    if not password:
        raise AccountValidationError("password must not be empty")


def password_file_paths(slug: str) -> Tuple[Path, str]:
    """(host path, in-container path) of the cTID password file for `slug`."""
    filename = f"ctid_{slug}_pwd"
    return Path(ctrader_home()) / "ctrader_data" / filename, f"{CONTAINER_CREDENTIALS_DIR}/{filename}"


def write_password_file(path: Path, password: str) -> None:
    """Write `password` to `path` with mode 0600; the parent is created 0700 when missing."""
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(password)
    os.chmod(path, 0o600)   # O_CREAT's mode is umask-masked and ignored for a pre-existing file


def public_view(row: Dict) -> Dict:
    return {k: row[k] for k in ("id", "slug", "ctid_email", "account_number", "account_type", "label", "created_at")}


def list_ctrader_accounts(registry: AccountRegistry) -> List[Dict]:
    return [public_view(row) for row in registry.list_ctrader_accounts()]


def create_ctrader_account(registry: AccountRegistry, *, label: str, ctid_email: str, password: str,
                           account_number: str, account_type: str) -> Dict:
    """Validate, write the password file, insert the row, mark the dashboard account configured.

    Raises AccountValidationError (422), DuplicateSlugError (409) or OSError (500, no row written).
    """
    label = label.strip()
    ctid_email = ctid_email.strip()
    account_number = account_number.strip()
    account_type = account_type.strip().lower()
    validate_account_input(label, ctid_email, password, account_number, account_type)

    slug = slugify(account_type, label)
    if registry.get_ctrader_account_by_slug(slug):
        raise DuplicateSlugError(f"an account with slug '{slug}' already exists")

    host_path, container_path = password_file_paths(slug)
    write_password_file(host_path, password)
    try:
        row = registry.insert_ctrader_account(slug, ctid_email, account_number, account_type, label, container_path)
    except Exception:
        host_path.unlink(missing_ok=True)
        raise
    registry.upsert_configured_account(f"{account_type}-{account_number}", account_number, account_type, label)
    logger.info(f"cTrader account created: {slug} ({account_type} {account_number})")
    return public_view(row)


def delete_ctrader_account(registry: AccountRegistry, account_id: int) -> bool:
    """Delete the row and its password file. cbot_configs are left alone (their commands are self-contained)."""
    row = registry.get_ctrader_account(account_id)
    if not row:
        return False
    registry.delete_ctrader_account(account_id)
    host_path, _ = password_file_paths(row["slug"])
    try:
        host_path.unlink(missing_ok=True)
    except OSError as e:
        logger.warning(f"Could not remove password file {host_path}: {e}")
    logger.info(f"cTrader account deleted: {row['slug']}")
    return True
