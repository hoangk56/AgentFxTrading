"""Code hashes for a pre-registration: sha256 (first 16 hex) of each file, as Markdown list lines.

Run it right before a holdout, paste the output into the prereg file, and do not edit those files until the
holdout has run. `--at <commit>` hashes the files as committed instead of the working tree, so a registered hash
can be checked against git later.

    research/.venv/bin/python -m research.tools.prereg_hashes research/swing/swing.py research/swing/swing_rules.py
    research/.venv/bin/python -m research.tools.prereg_hashes --at af3ab38 research/scan/rates.py
"""
import argparse
import hashlib
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def short_sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def file_bytes(path: str, commit: str = None) -> bytes:
    if commit:
        return subprocess.run(["git", "show", f"{commit}:{path}"], capture_output=True, check=True,
                              cwd=REPO_ROOT).stdout
    return Path(path).read_bytes()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--at", metavar="COMMIT", help="hash the files as committed at COMMIT")
    args = ap.parse_args(argv)
    for f in args.files:
        print(f"- `{f}` {short_sha(file_bytes(f, args.at))}")


if __name__ == "__main__":
    main()
