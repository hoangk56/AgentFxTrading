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


def test_err_trap_fires_for_failures_inside_functions():
    result = run_fn("CURRENT_STEP='demo step'; f() { false; }; f; echo unreachable")
    assert result.returncode != 0
    assert "unreachable" not in result.stdout
    assert 'Install failed during step "demo step"' in result.stderr
