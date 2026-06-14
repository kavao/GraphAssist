"""assets CLI tests."""

from __future__ import annotations

import unittest

from graphassist.assets_cmd import run_assets_fetch


class AssetsCmdTest(unittest.TestCase):
    def test_fetch_unknown_id_exits_nonzero(self) -> None:
        code = run_assets_fetch(ids=["not-a-real-catalog-id"])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
