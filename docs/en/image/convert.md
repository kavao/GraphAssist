# convert guide

English · [日本語](../ja/image/convert.md)

Batch conversion for files or directories.

```bash
uv run python tools/graphassist/graphassist.py convert samples/source/ generated/images/batch \
  --long-edge 1024 --format webp
```

## Options

| Option | Description |
|--------|-------------|
| `--format` | `png` / `jpeg` / `webp` |
| `--long-edge N` | Resize so max(w,h)=N |
| `--width` / `--height` | Fixed size |
| `--square` | Pad to square |
| `--square-fill` | `transparent` / `white` / `black` |
| `--quality` | JPEG/WebP quality |
| `--dpi` | Output DPI |
| `--strip-exif` | Strip JPEG EXIF |
| `--numbered` | Numbered output names |

## See also

- [operations.md](operations.md)
- [quickstart.md](../quickstart.md)
