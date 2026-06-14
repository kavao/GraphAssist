# convert guide

English · [日本語](../ja/image/convert.md)

Batch conversion for files or directories.

```bash
uv run graphassist convert samples/source/ generated/images/batch \
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
| `--brightness` | Brightness factor (0..3) |
| `--contrast` | Contrast factor (0..3) |
| `--saturation` | Saturation factor (0..3) |
| `--gamma` | Gamma correction (0.1..5) |
| `--quantize N` | Reduce to N colors (2..256) |
| `--blur R` | Gaussian blur radius (0..50) |
| `--grayscale` | Rec.601 luminance grayscale |
| `--sepia S` | Sepia tone strength (0..1) |

Tone flags apply **after** resize options. Order: adjust → curve → grayscale → sepia → quantize → blur.

```bash
uv run graphassist convert samples/source/ generated/images/out \
  --long-edge 1024 --format webp --brightness 1.1 --gamma 1.05
```

## See also

- [operations.md](operations.md)
- [quickstart.md](../quickstart.md)
