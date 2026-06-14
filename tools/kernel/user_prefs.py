#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ユーザーロケール設定（ホーム config / プロジェクト local）の読取と副本ルール生成。

正本: ~/.config/dna-kernel/config.toml（秘密は .env ではない）

使い方:
  python user_prefs.py init-config
  python user_prefs.py show conversation.language
  python user_prefs.py sync
  python user_prefs.py sync --dry-run
"""

from __future__ import annotations

import argparse
import json
import locale
import os
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SUPPORTED_LANGUAGES = frozenset({"ja", "en"})
DEFAULT_CONVERSATION_LANGUAGE = "ja"
DEFAULT_DOC_EDITORIAL = "ja"

CONFIG_TEMPLATE = """\
# dna_kernel user preferences (home config)
# 会話言語と docs 編集正本は別軸。詳細: docs/ja/dna-kernel/onboarding.md

[conversation]
language = "ja"  # "ja" | "en"

[authoring]
default_doc_editorial = "ja"  # docs 編集正本（既定 ja）
require_en_sync = true        # docs 更新時に en 同期を必須
"""

LOCAL_CONFIG_FILENAME = ".dna-kernel.local.toml"


@dataclass(frozen=True)
class ResolvedLanguage:
    language: str
    source: str


def repo_root() -> Path:
    start = Path(__file__).resolve().parent
    for candidate in (start, *start.parents):
        if (
            (candidate / "rulesync.jsonc").is_file()
            and (candidate / ".rulesync").is_dir()
        ) or (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def home_config_dir() -> Path:
    return Path.home() / ".config" / "dna-kernel"


def home_config_path() -> Path:
    return home_config_dir() / "config.toml"


def local_config_path(root: Path | None = None) -> Path:
    return (root or repo_root()) / LOCAL_CONFIG_FILENAME


def _read_toml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"config のルートはテーブルである必要があります: {path}")
    return data


def _get_nested(data: dict[str, Any], key: str) -> Any:
    cur: Any = data
    for part in key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _validate_language(value: Any, *, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} は文字列である必要があります")
    lang = value.strip().lower()
    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"{field} は {sorted(SUPPORTED_LANGUAGES)} のいずれかです（got: {value!r}）"
        )
    return lang


def os_locale_fallback() -> str:
    for key in ("LC_ALL", "LANG", "LC_MESSAGES"):
        val = os.environ.get(key, "")
        if val.lower().startswith("ja"):
            return "ja"
    try:
        loc = locale.getlocale()[0]
    except (ValueError, AttributeError):
        loc = None
    if loc and loc.lower().startswith("ja"):
        return "ja"
    return "en"


def load_merged_config(root: Path | None = None) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    home = _read_toml(home_config_path())
    local = _read_toml(local_config_path(root))
    for src in (home, local):
        for section, table in src.items():
            if not isinstance(table, dict):
                continue
            merged.setdefault(section, {})
            if isinstance(merged[section], dict):
                merged[section].update(table)
    return merged


def resolve_conversation_language(
    *,
    root: Path | None = None,
    explicit: str | None = None,
) -> ResolvedLanguage:
    if explicit is not None:
        return ResolvedLanguage(
            language=_validate_language(explicit, field="explicit"),
            source="explicit",
        )

    local_path = local_config_path(root)
    local = _read_toml(local_path)
    local_lang = _get_nested(local, "conversation.language")
    if local_lang is not None:
        return ResolvedLanguage(
            language=_validate_language(local_lang, field="conversation.language (local)"),
            source=f"local:{local_path.name}",
        )

    home_path = home_config_path()
    home = _read_toml(home_path)
    home_lang = _get_nested(home, "conversation.language")
    if home_lang is not None:
        return ResolvedLanguage(
            language=_validate_language(home_lang, field="conversation.language (home)"),
            source=f"home:{home_path}",
        )

    return ResolvedLanguage(language=os_locale_fallback(), source="os-locale")


def resolve_authoring_prefs(root: Path | None = None) -> dict[str, Any]:
    cfg = load_merged_config(root)
    authoring = cfg.get("authoring", {})
    if not isinstance(authoring, dict):
        authoring = {}

    editorial = authoring.get("default_doc_editorial", DEFAULT_DOC_EDITORIAL)
    if not isinstance(editorial, str):
        editorial = DEFAULT_DOC_EDITORIAL
    editorial = editorial.strip().lower()
    if editorial not in SUPPORTED_LANGUAGES:
        editorial = DEFAULT_DOC_EDITORIAL

    require_en_sync = authoring.get("require_en_sync", True)
    if not isinstance(require_en_sync, bool):
        require_en_sync = True

    return {
        "default_doc_editorial": editorial,
        "require_en_sync": require_en_sync,
    }


def locale_rule_body(language: str) -> str:
    if language == "ja":
        return """# User locale (generated)

- ユーザーとの会話は **日本語** で行う。
- **会話言語と書き込み正本は別軸**。docs の編集正本は `docs/ja/`、表示用に `docs/en/` を同期する（`docs-writing` / `content-placement` 参照）。
- このファイルは `user_prefs.py sync` で再生成される。`corepack pnpm dlx rulesync generate` の**後**にも `user_prefs.py sync` を実行する。
"""
    return """# User locale (generated)

- Respond to the user in **English**.
- **Conversation language is separate from editorial sources.** Write docs to `docs/ja/` first and sync `docs/en/` for display (see `docs-writing` / `content-placement`).
- This file is regenerated by `user_prefs.py sync`. Run sync **after** `corepack pnpm dlx rulesync generate`.
"""


def cursor_locale_rule(language: str) -> str:
    return (
        "---\n"
        "description: User conversation language (generated by user_prefs.py sync)\n"
        "alwaysApply: true\n"
        "---\n"
        + locale_rule_body(language)
    )


def claude_locale_rule(language: str) -> str:
    return (
        "---\n"
        "paths:\n"
        '  - "**/*"\n'
        "---\n"
        + locale_rule_body(language)
    )


def sync_targets(root: Path) -> list[tuple[Path, str]]:
    resolved = resolve_conversation_language(root=root)
    body_cursor = cursor_locale_rule(resolved.language)
    body_claude = claude_locale_rule(resolved.language)
    return [
        (root / ".cursor" / "rules" / "user-locale.mdc", body_cursor),
        (root / ".claude" / "rules" / "user-locale.md", body_claude),
    ]


def init_config(*, dry_run: bool = False) -> dict[str, Any]:
    path = home_config_path()
    created = False
    if path.is_file():
        action = "exists"
    else:
        action = "create"
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(CONFIG_TEMPLATE, encoding="utf-8")
        created = True
    return {
        "path": str(path.resolve()),
        "action": action,
        "created": created,
        "dry_run": dry_run,
    }


def run_sync(*, root: Path | None = None, dry_run: bool = False) -> dict[str, Any]:
    r = root or repo_root()
    resolved = resolve_conversation_language(root=r)
    written: list[str] = []
    for path, content in sync_targets(r):
        if dry_run:
            written.append(str(path.resolve()))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(str(path.resolve()))
    return {
        "language": resolved.language,
        "source": resolved.source,
        "paths": written,
        "dry_run": dry_run,
    }


def show_value(key: str, *, root: Path | None = None) -> Any:
    if key == "conversation.language":
        resolved = resolve_conversation_language(root=root)
        return {"value": resolved.language, "source": resolved.source}
    if key.startswith("authoring."):
        prefs = resolve_authoring_prefs(root)
        sub = key.removeprefix("authoring.")
        if sub not in prefs:
            raise KeyError(key)
        return prefs[sub]
    merged = load_merged_config(root)
    value = _get_nested(merged, key)
    if value is None:
        raise KeyError(key)
    return value


def cmd_init_config(args: argparse.Namespace) -> int:
    result = init_config(dry_run=args.dry_run)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.dry_run:
        print(f"[dry-run] ホーム config: {result['path']} ({result['action']})")
    elif result["action"] == "exists":
        print(f"確認: ホーム config は既に存在します: {result['path']}")
    else:
        print(f"作成しました: {result['path']}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve() if args.repo_root else repo_root()
    try:
        value = show_value(args.key, root=root)
    except (KeyError, ValueError) as e:
        print(str(e), file=sys.stderr)
        return 1
    if args.json:
        if isinstance(value, dict):
            print(json.dumps(value, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"key": args.key, "value": value}, ensure_ascii=False, indent=2))
    elif isinstance(value, dict):
        print(value.get("value", value))
        if "source" in value:
            print(f"# source: {value['source']}", file=sys.stderr)
    else:
        print(value)
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve() if args.repo_root else repo_root()
    try:
        result = run_sync(root=root, dry_run=args.dry_run)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.dry_run:
        print(f"[dry-run] conversation.language={result['language']} ({result['source']})")
        for p in result["paths"]:
            print(f"  → {p}")
    else:
        print(f"sync 完了: language={result['language']} ({result['source']})")
        for p in result["paths"]:
            print(f"  書き込み: {p}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="dna_kernel ユーザーロケール設定（ホーム config / 副本ルール sync）"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="リポジトリルート（既定: 自動検出）",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init-config", help="ホーム config テンプレを作成（存在すればスキップ）")
    p_init.add_argument("--dry-run", action="store_true")
    p_init.add_argument("--json", action="store_true")
    p_init.set_defaults(func=cmd_init_config)

    p_show = sub.add_parser("show", help="設定値を表示（例: conversation.language）")
    p_show.add_argument("key", help="ドット区切りキー（conversation.language 等）")
    p_show.add_argument("--json", action="store_true")
    p_show.set_defaults(func=cmd_show)

    p_sync = sub.add_parser(
        "sync",
        help="会話言語を .cursor/.claude の user-locale 副本へ書き出す（rulesync generate の後）",
    )
    p_sync.add_argument("--dry-run", action="store_true")
    p_sync.add_argument("--json", action="store_true")
    p_sync.set_defaults(func=cmd_sync)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
