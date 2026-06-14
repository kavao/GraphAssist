from pathlib import Path
import subprocess
import sys

WORKSPACE_DIRS = [
    "_workingspace/log",
    "_workingspace/diary",
    "_workingspace/plans",
]


def init() -> None:
    print("dna_kernel — 初期セットアップ")
    print()

    print("_workingspace/ ディレクトリを確認します...")
    for d in WORKSPACE_DIRS:
        path = Path(d)
        if not path.exists():
            path.mkdir(parents=True)
            (path / ".gitkeep").touch()
            print(f"  作成: {d}/")
        else:
            print(f"  確認: {d}/ (存在)")

    print()
    print("ホーム config（会話言語）を確認します...")
    script = Path(__file__).resolve().parent / "tools" / "kernel" / "user_prefs.py"
    subprocess.run([sys.executable, str(script), "init-config"], check=False)

    print()
    print("セットアップ完了。以下のツールが使えます:")
    print("  uv run python tools/kernel/workspace_audit_log.py append '本文'")
    print("  uv run python tools/kernel/json_weighted_pick.py <file.json> -p <path>")
    print("  uv run python tools/kernel/user_prefs.py show conversation.language")
    print()
    print("ルール再生成の標準手順（generate の後に sync 必須）:")
    print("  corepack pnpm dlx rulesync generate --dry-run")
    print("  corepack pnpm dlx rulesync generate")
    print("  uv run python tools/kernel/user_prefs.py sync")


if __name__ == "__main__":
    init()
