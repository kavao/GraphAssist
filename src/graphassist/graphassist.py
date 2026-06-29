#!/usr/bin/env python3
# Version: 0.2.0 (正本: .rulesync/metadata/graphassist.json)
"""GraphAssist 画像処理 CLI。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from graphassist.version import __version__
from graphassist.analyze_cmd import run_analyze
from graphassist.assets_cmd import run_assets_fetch, run_assets_list, run_assets_materialize
from graphassist.batch_runner import run_batch_file
from graphassist.convert_cmd import ConvertOptions, run_convert
from graphassist.font_cmd import run_font_outline
from graphassist.job_runner import run_job_file
from graphassist.lineart_cmd import run_lineart_render, run_lineart_validate
from graphassist.mosaic_cmd import (
    MosaicDecodeOptions,
    MosaicEncodeOptions,
    run_compose_birds,
    run_decode,
    run_encode,
    run_export,
    run_merge,
)
from graphassist.util_cmd import (
    TrimOptions,
    run_contact_sheet,
    run_diff,
    run_inspect,
    run_palette,
    run_sheet_pack,
    run_sheet_split,
    run_trim,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="graphassist",
        description="GraphAssist image CLI (Pillow)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
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
    convert.add_argument("--brightness", type=float, default=None, help="adjust brightness factor (0..3)")
    convert.add_argument("--contrast", type=float, default=None, help="adjust contrast factor (0..3)")
    convert.add_argument("--saturation", type=float, default=None, help="adjust saturation factor (0..3)")
    convert.add_argument("--gamma", type=float, default=None, help="gamma curve (0.1..5)")
    convert.add_argument("--quantize", type=int, default=None, metavar="N", help="reduce to N colors (2..256)")
    convert.add_argument("--blur", type=float, default=None, metavar="R", help="gaussian blur radius (0..50)")
    convert.add_argument("--grayscale", action="store_true", help="Rec.601 luminance grayscale (RGB only, alpha preserved)")
    convert.add_argument("--sepia", type=float, default=None, metavar="S", help="sepia tone strength 0..1")

    job = sub.add_parser("job", help="run ImageJob JSON (Pillow edit pipeline)")
    job.add_argument("json_path", type=Path, help="path to ImageJob JSON file")
    job.add_argument("--dry-run", action="store_true", help="validate and print steps without writing output")

    run = sub.add_parser("run", help="run Batch manifest JSON (multiple commands in one file)")
    run.add_argument("json_path", type=Path, help="path to Batch manifest under samples/jobs/")
    run.add_argument("--dry-run", action="store_true", help="validate and list steps without writing output")

    mosaic = sub.add_parser("mosaic", help="CharGrid mosaic encode / decode / export")
    mosaic_sub = mosaic.add_subparsers(dest="mosaic_command", required=True)

    mosaic_decode = mosaic_sub.add_parser("decode", help="MosaicArt JSON to image")
    mosaic_decode.add_argument("json_path", type=Path, help="MosaicArt JSON under samples/mosaic/ or generated/mosaic/")
    mosaic_decode.add_argument("output", type=Path, help="output image under generated/")
    mosaic_decode.add_argument("--cell-size", type=int, default=1, help="pixels per grid cell (preview scale)")
    mosaic_decode.add_argument(
        "--format",
        dest="fmt",
        default="png",
        choices=["png", "webp"],
        help="output format",
    )
    mosaic_decode.add_argument("--quality", type=int, default=85, help="WebP quality")

    mosaic_encode = mosaic_sub.add_parser("encode", help="image to MosaicArt JSON")
    mosaic_encode.add_argument("input", type=Path, help="input image under samples/source/")
    mosaic_encode.add_argument("output", type=Path, help="output JSON under generated/mosaic/")
    mosaic_encode.add_argument("--grid", required=True, help="output grid size, e.g. 32x32")
    mosaic_encode.add_argument("--max-colors", type=int, default=16, help="max palette size")
    mosaic_encode.add_argument("--transparent", default=".", help="transparent cell character")
    mosaic_encode.add_argument("--alpha-threshold", type=int, default=128, help="alpha <= threshold is transparent")

    mosaic_export = mosaic_sub.add_parser("export", help="export MosaicArt JSON as JS snippet")
    mosaic_export.add_argument("json_path", type=Path, help="MosaicArt JSON path")
    mosaic_export.add_argument("--format", default="js", choices=["js", "json"], help="export format")
    mosaic_export.add_argument("--output", type=Path, default=None, help="write to file under generated/mosaic/")
    mosaic_export.add_argument("--name", default=None, help="JS const base name")

    mosaic_merge = mosaic_sub.add_parser("merge", help="merge MosaicArt JSON layers into one grid")
    mosaic_merge.add_argument("output", type=Path, help="output JSON under generated/mosaic/")
    mosaic_merge.add_argument("--canvas", required=True, help="canvas size WIDTHxHEIGHT")
    mosaic_merge.add_argument(
        "--layer",
        action="append",
        dest="layers",
        required=True,
        metavar="PATH@X,Y",
        help="layer spec (repeatable): samples/mosaic/a.json@10,5",
    )
    mosaic_merge.add_argument("--title", default=None, help="meta.title for merged art")

    mosaic_compose_birds = mosaic_sub.add_parser(
        "compose-birds",
        help="compose birds_on_trunk from parakeet + parrot + trunk preset",
    )
    mosaic_compose_birds.add_argument(
        "output",
        type=Path,
        help="output JSON under generated/mosaic/",
    )

    lineart = sub.add_parser("lineart", help="LineArt vector JSON render / validate")
    lineart_sub = lineart.add_subparsers(dest="lineart_command", required=True)
    lineart_render = lineart_sub.add_parser("render", help="render LineArt JSON to SVG")
    lineart_render.add_argument("json_path", type=Path, help="LineArt JSON under samples/lineart/ or generated/lineart/")
    lineart_render.add_argument("output", type=Path, help="output SVG under generated/vector/")
    lineart_render.add_argument("--dry-run", action="store_true", help="validate without writing output")
    lineart_render.add_argument("--png", type=Path, default=None, help="also rasterize to PNG under generated/images/")
    lineart_render.add_argument("--png-width", type=int, default=None, help="PNG output width; defaults to canvas width")
    lineart_validate = lineart_sub.add_parser("validate", help="validate LineArt metadata and geometry foundation")
    lineart_validate.add_argument("json_path", type=Path, help="LineArt JSON under samples/lineart/ or generated/lineart/")
    lineart_validate.add_argument("--report", required=True, type=Path, help="report JSON under generated/logs/")
    lineart_validate.add_argument("--dry-run", action="store_true", help="validate without writing report")

    font = sub.add_parser("font", help="FontVector outline extraction")
    font_sub = font.add_subparsers(dest="font_command", required=True)
    font_outline = font_sub.add_parser("outline", help="extract text glyph outlines to JSON")
    font_outline.add_argument("--text", required=True, help="text to outline")
    font_outline.add_argument("--font", required=True, type=Path, help="font path under assets/fonts/")
    font_outline.add_argument("--size", type=float, default=48, help="font size in px")
    font_outline.add_argument("--output", required=True, type=Path, help="output JSON under generated/vector/")
    font_outline.add_argument("--dry-run", action="store_true", help="validate without writing output")
    font_outline.add_argument("--strict", action="store_true", help="fail when a glyph is missing or empty")

    trim = sub.add_parser("trim", help="auto-trim margins")
    trim.add_argument("input", type=Path)
    trim.add_argument("output", type=Path)
    trim.add_argument("--background", default="transparent", choices=["transparent", "white", "black"])
    trim.add_argument("--padding", type=int, default=0)
    trim.add_argument("--tolerance", type=int, default=0)

    diff = sub.add_parser("diff", help="visual diff between two images")
    diff.add_argument("before", type=Path)
    diff.add_argument("after", type=Path)
    diff.add_argument("output", type=Path)
    diff.add_argument("--threshold", type=int, default=16)

    inspect = sub.add_parser("inspect", help="inspect image metadata")
    inspect.add_argument("input", type=Path)
    inspect.add_argument("--format", dest="fmt", default="text", choices=["text", "json"])
    inspect.add_argument("--max-long-edge", type=int, default=None)

    contact = sub.add_parser("contact-sheet", help="thumbnail contact sheet")
    contact.add_argument("input", type=Path)
    contact.add_argument("output", type=Path)
    contact.add_argument("--cols", type=int, default=None)
    contact.add_argument("--thumb", type=int, default=128)
    contact.add_argument("--padding", type=int, default=4)

    pack = sub.add_parser("sheet-pack", help="pack images into sprite sheet")
    pack.add_argument("input", type=Path)
    pack.add_argument("output", type=Path)
    pack.add_argument("--cell-width", type=int, required=True)
    pack.add_argument("--cell-height", type=int, required=True)
    pack.add_argument("--cols", type=int, required=True)
    pack.add_argument("--padding", type=int, default=0)

    split = sub.add_parser("sheet-split", help="split sprite sheet into cells")
    split.add_argument("input", type=Path)
    split.add_argument("output", type=Path)
    split.add_argument("--cell-width", type=int, required=True)
    split.add_argument("--cell-height", type=int, required=True)
    split.add_argument("--cols", type=int, required=True)
    split.add_argument("--rows", type=int, required=True)
    split.add_argument("--padding", type=int, default=0)

    palette = sub.add_parser("palette", help="extract dominant colors")
    palette.add_argument("input", type=Path)
    palette.add_argument("--max-colors", type=int, default=16)
    palette.add_argument("--format", dest="fmt", default="json", choices=["json", "text"])

    assets = sub.add_parser("assets", help="fetch curated catalog assets (CC0 / PD)")
    assets_sub = assets.add_subparsers(dest="assets_command", required=True)
    assets_fetch = assets_sub.add_parser("fetch", help="download and mirror catalog assets")
    assets_fetch.add_argument("--force", action="store_true", help="re-download and re-rasterize")
    assets_fetch.add_argument(
        "--id",
        action="append",
        dest="ids",
        metavar="ID",
        help="fetch only these catalog ids (repeatable)",
    )
    assets_list = assets_sub.add_parser("list", help="list catalog asset definitions")
    assets_list.add_argument("--format", dest="fmt", default="text", choices=["text", "json"])
    assets_materialize = assets_sub.add_parser(
        "materialize",
        help="download and mirror catalog assets (alias of fetch)",
    )
    assets_materialize.add_argument("--force", action="store_true", help="re-download and re-rasterize")
    assets_materialize.add_argument(
        "--id",
        action="append",
        dest="ids",
        metavar="ID",
        help="materialize only these catalog ids (repeatable)",
    )

    analyze = sub.add_parser("analyze", help="image metrics profile / compare (Phase A+L)")
    analyze.add_argument("input", type=Path, help="image file or directory")
    analyze.add_argument("--compare", type=Path, default=None, help="compare target image")
    analyze.add_argument("--format", dest="fmt", default="json", choices=["json", "text"])
    analyze.add_argument("--output", type=Path, default=None, help="write JSON/text to file")
    analyze.add_argument("--max-long-edge", type=int, default=512, help="stats downsample (0=full)")
    analyze.add_argument("--max-colors", type=int, default=8)
    analyze.add_argument("--alpha-threshold", type=int, default=128)
    analyze.add_argument("--threshold-brightness", type=float, default=0.15)
    analyze.add_argument("--threshold-palette", type=float, default=0.30)
    analyze.add_argument("--full-profiles", action="store_true")
    analyze.add_argument("--spatial", action="store_true", help="include Phase L local metrics")
    analyze.add_argument("--background", default="transparent", choices=["transparent", "white", "black"])
    analyze.add_argument("--tolerance", type=int, default=0)
    analyze.add_argument("--grid-rows", type=int, default=3)
    analyze.add_argument("--grid-cols", type=int, default=3)
    analyze.add_argument(
        "--roi",
        action="append",
        dest="rois",
        metavar="NAME,X,Y,W,H",
        help="named ROI (repeatable, max 4)",
    )

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
            brightness=args.brightness,
            contrast=args.contrast,
            saturation=args.saturation,
            gamma=args.gamma,
            quantize_colors=args.quantize,
            blur_radius=args.blur,
            grayscale=args.grayscale,
            sepia_strength=args.sepia,
        )
        created = run_convert(args.input, args.output, opts)
        for path in created:
            print(path)
        return 0

    if args.command == "job":
        run_job_file(args.json_path, dry_run=args.dry_run)
        return 0

    if args.command == "run":
        run_batch_file(args.json_path, dry_run=args.dry_run)
        return 0

    if args.command == "mosaic":
        if args.mosaic_command == "decode":
            out = run_decode(
                args.json_path,
                args.output,
                MosaicDecodeOptions(cell_size=args.cell_size, fmt=args.fmt, quality=args.quality),
            )
            print(out)
            return 0
        if args.mosaic_command == "encode":
            out = run_encode(
                args.input,
                args.output,
                MosaicEncodeOptions(
                    grid=args.grid,
                    max_colors=args.max_colors,
                    transparent=args.transparent,
                    alpha_threshold=args.alpha_threshold,
                ),
            )
            print(out)
            return 0
        if args.mosaic_command == "export":
            text = run_export(args.json_path, fmt=args.format, output_path=args.output, name=args.name)
            if args.output is None:
                print(text, end="" if text.endswith("\n") else "\n")
            else:
                print(args.output)
            return 0
        if args.mosaic_command == "merge":
            out = run_merge(args.output, canvas=args.canvas, layers=args.layers, title=args.title)
            print(out)
            return 0
        if args.mosaic_command == "compose-birds":
            out = run_compose_birds(args.output)
            print(out)
            return 0

    if args.command == "lineart":
        if args.lineart_command == "render":
            out = run_lineart_render(
                args.json_path,
                args.output,
                dry_run=args.dry_run,
                png_output=args.png,
                png_width=args.png_width,
            )
            print(out)
            return 0
        if args.lineart_command == "validate":
            out = run_lineart_validate(args.json_path, report=args.report, dry_run=args.dry_run)
            print(out)
            return 0

    if args.command == "font":
        if args.font_command == "outline":
            out = run_font_outline(
                text=args.text,
                font=args.font,
                size=args.size,
                output=args.output,
                dry_run=args.dry_run,
                strict=args.strict,
            )
            print(out)
            return 0

    if args.command == "trim":
        for path in run_trim(
            args.input,
            args.output,
            TrimOptions(background=args.background, padding=args.padding, tolerance=args.tolerance),
        ):
            print(path)
        return 0

    if args.command == "diff":
        out, meta = run_diff(args.before, args.after, args.output, threshold=args.threshold)
        print(out)
        print(f"changed_ratio={meta['changed_ratio']}")
        return 0

    if args.command == "inspect":
        print(run_inspect(args.input, fmt=args.fmt, max_long_edge=args.max_long_edge), end="")
        return 0

    if args.command == "contact-sheet":
        print(run_contact_sheet(args.input, args.output, cols=args.cols, thumb=args.thumb, padding=args.padding))
        return 0

    if args.command == "sheet-pack":
        print(
            run_sheet_pack(
                args.input,
                args.output,
                cell_width=args.cell_width,
                cell_height=args.cell_height,
                cols=args.cols,
                padding=args.padding,
            )
        )
        return 0

    if args.command == "sheet-split":
        for path in run_sheet_split(
            args.input,
            args.output,
            cell_width=args.cell_width,
            cell_height=args.cell_height,
            cols=args.cols,
            rows=args.rows,
            padding=args.padding,
        ):
            print(path)
        return 0

    if args.command == "palette":
        print(run_palette(args.input, max_colors=args.max_colors, fmt=args.fmt), end="")
        return 0

    if args.command == "assets":
        if args.assets_command == "fetch":
            return run_assets_fetch(force=args.force, ids=args.ids)
        if args.assets_command == "materialize":
            return run_assets_materialize(force=args.force, ids=args.ids)
        if args.assets_command == "list":
            return run_assets_list(fmt=args.fmt)

    if args.command == "analyze":
        text = run_analyze(
            args.input,
            compare=args.compare,
            fmt=args.fmt,
            output=args.output,
            max_long_edge=args.max_long_edge,
            max_colors=args.max_colors,
            alpha_threshold=args.alpha_threshold,
            threshold_brightness=args.threshold_brightness,
            threshold_palette=args.threshold_palette,
            full_profiles=args.full_profiles,
            spatial=args.spatial,
            background=args.background,
            tolerance=args.tolerance,
            grid_rows=args.grid_rows,
            grid_cols=args.grid_cols,
            rois=args.rois,
        )
        if args.output is None:
            print(text, end="")
        else:
            print(args.output)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
