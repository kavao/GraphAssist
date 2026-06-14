# CLI reference (operations)

English · [日本語](../ja/image/operations.md)

GraphAssist subcommands. See each guide for path rules.

## Subcommands

| Command | Purpose |
|---------|---------|
| `convert` | Batch resize / format conversion |
| `job` | Run ImageJob JSON |
| `run` | Batch manifest (multi-command) |
| `mosaic` | CharGrid encode / decode / export |
| `trim` | Auto-trim margins |
| `diff` | Visual diff between two images |
| `inspect` | Resolution, mode, corruption check |
| `contact-sheet` | Thumbnail grid sheet |
| `sheet-pack` | Multiple PNGs → sprite sheet |
| `sheet-split` | Sprite sheet → PNG cells |
| `palette` | Dominant color extraction |

## ImageJob operations

| type | Summary |
|------|---------|
| `resize` | Scale |
| `crop` | Rectangular crop (`anchor`: `top_left` / `center`) |
| `extend` | Canvas padding |
| `rotate` | Rotation |
| `border` | Border |
| `composite` | Overlay |
| `text` | Font rendering (`assets/fonts/`, `direction`: `horizontal` / `vertical`) |
| `trim` | Trim margins |
| `flatten` | Flatten alpha to background |

Colors: names (`white`, etc.) or `#RRGGBB`

## Examples

```bash
uv run graphassist trim samples/source/icon.png generated/images/icon_trim.png
uv run graphassist diff before.png after.png generated/images/diff.png
uv run graphassist inspect samples/source/icon.png --format json
uv run graphassist contact-sheet samples/source generated/images/sheet.png --cols 4
uv run graphassist palette samples/source/icon.png --max-colors 8
```

## See also

- [convert.md](convert.md)
- [edit-job.md](edit-job.md)
- [mosaic.md](mosaic.md)
- [batch.md](batch.md)
