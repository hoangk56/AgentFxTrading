"""The code registered for the swing lab v2 holdout stays verifiable: the reconstructed sources kept next to the
prereg file hash to the values it names, and the files that were committed unchanged still hash the same in git."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from research.tools.prereg_hashes import file_bytes, short_sha

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "research" / "results" / "portfolio" / "prereg_swing_v2.md"
CODE = PREREG.parent / "prereg_swing_v2_code"


def test_kept_sources_match_the_hash_in_their_name_and_in_the_prereg():
    text = PREREG.read_text(encoding="utf-8")
    kept = sorted(CODE.glob("*@*.py.txt"))
    assert len(kept) == 3
    for f in kept:
        registered = re.search(r"@([0-9a-f]{16})\.py\.txt$", f.name).group(1)
        assert short_sha(f.read_bytes()) == registered, f.name
        assert registered in text, f.name


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")
def test_files_committed_unchanged_still_hash_as_registered():
    registered = {"research/scan/rates.py": "5a84860812283a21", "research/scan/specs_ext.py": "e63964ed74d204b2",
                  "research/scan/data.py": "763e848464232614", "research/specs.py": "9ef05930b3f0baf1"}
    try:
        got = {f: short_sha(file_bytes(f, "af3ab38")) for f in registered}
    except subprocess.CalledProcessError:
        pytest.skip("commit af3ab38 is not in this clone")
    assert got == registered
