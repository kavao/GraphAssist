"""GraphAssist バージョン整合のテスト。"""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.graphassist import __version__  # noqa: E402
from tools.graphassist.version import __version__ as version_module  # noqa: E402

CANONICAL_PATH = ROOT / "tools/graphassist/graphassist.py"
METADATA_PATH = ROOT / ".rulesync/metadata/graphassist.json"
PYPROJECT_PATH = ROOT / "pyproject.toml"


class VersionTest(unittest.TestCase):
    def test_version_matches_rulesync_metadata(self) -> None:
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(__version__, metadata["version"])
        self.assertEqual(version_module, metadata["version"])

    def test_graphassist_header_contains_version(self) -> None:
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        header = CANONICAL_PATH.read_text(encoding="utf-8").splitlines()[1]
        self.assertIn("Version:", header)
        self.assertIn(metadata["version"], header)

    def test_pyproject_version_matches(self) -> None:
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        text = PYPROJECT_PATH.read_text(encoding="utf-8")
        match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
        self.assertIsNotNone(match)
        assert match is not None
        self.assertEqual(match.group(1), metadata["version"])


if __name__ == "__main__":
    unittest.main()
