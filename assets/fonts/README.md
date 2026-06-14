# Fonts

Place `.ttf` / `.otf` files here for ImageJob `text` operations.

GraphAssist ships `DejaVuSans.ttf` (or place your own).  
ImageJob JSON must reference paths under `assets/fonts/` only, for example:

```json
{"type": "text", "content": "Hello", "font": "assets/fonts/DejaVuSans.ttf", "size": 48, "color": "white", "x": 10, "y": 10}
```

For Noto Sans or other OFL fonts, add the license file alongside the font.
