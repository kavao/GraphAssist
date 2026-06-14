#!/usr/bin/env python3
"""parakeet + parrot + trunk preset から birds_on_trunk 相当 JSON を生成する。"""

from __future__ import annotations

from graphassist.mosaic_cmd import run_compose_birds
from graphassist.schema.paths import project_root


def main() -> None:
    root = project_root()
    out = run_compose_birds(root / "generated/mosaic/birds_on_trunk_merged.json", root=root)
    print(out)


if __name__ == "__main__":
    main()
