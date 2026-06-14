#!/usr/bin/env python3
"""GraphAssist 画像処理 CLI。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.graphassist.convert_cmd import ConvertOptions, run_convert  # noqa: E402
from tools.graphassist.job_runner import run_job_file  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="graphassist", description="GraphAssist image CLI (Pillow)")
    sub = parser.add_subparsers(dest="command", required=True)

    convert = sub.add_parser("convert", help="batch resize / format conversion")
    convert.add_argument("input", type=Path, help="input file or directory")
    convert.add_argument("output", type=Path, help="output file or directory")
    convert.add_argument(
        "--format",
        dest="fmt",
        default="png",
        choices=["png", "jpeg", "webp"],
        help="output format",
    )
    convert.add_argument("--long-edge", type=int, default=None, metavar="N", help="resize so max(w,h)=N")
    convert.add_argument("--width", type=int, default=None, help="output width")
    convert.add_argument("--height", type=int, default=None, help="output height")
    convert.add_argument("--square", action="store_true", help="pad to square canvas")
    convert.add_argument(
        "--square-fill",
        default="transparent",
        choices=["transparent", "white", "black"],
        help="fill when --square",
    )
    convert.add_argument("--quality", type=int, default=85, help="JPEG/WebP quality")
    convert.add_argument("--dpi", type=float, default=None, help="output DPI metadata")
    convert.add_argument("--strip-exif", action="store_true", help="strip EXIF on JPEG output")
    convert.add_argument("--numbered", action="store_true", help="use 0001, 0002, ... for batch output names")

    job = sub.add_parser("job", help="run ImageJob JSON (Pillow edit pipeline)")
    job.add_argument("json_path", type=Path, help="path to ImageJob JSON file")
    job.add_argument("--dry-run", action="store_true", help="validate and print steps without writing output")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "convert":
        opts = ConvertOptions(
            fmt=args.fmt,
            long_edge=args.long_edge,
            width=args.width,
            height=args.height,
            square=args.square,
            square_fill=args.square_fill,
            quality=args.quality,
            dpi=args.dpi,
            strip_exif=args.strip_exif,
            numbered=args.numbered,
        )
        created = run_convert(args.input, args.output, opts)
        for path in created:
            print(path)
        return 0

    if args.command == "job":
        run_job_file(args.json_path, dry_run=args.dry_run)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
