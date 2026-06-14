from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "tools" / "kernel"
sys.path.insert(0, str(KERNEL))

import user_prefs as up  # noqa: E402


class UserPrefsTests(unittest.TestCase):
    def test_explicit_language(self) -> None:
        r = up.resolve_conversation_language(explicit="en")
        self.assertEqual(r.language, "en")
        self.assertEqual(r.source, "explicit")

    def test_local_overrides_home(self) -> None:
        with tempfile_dirs() as (repo, home):
            home_cfg = home / "config.toml"
            home_cfg.parent.mkdir(parents=True, exist_ok=True)
            home_cfg.write_text('[conversation]\nlanguage = "ja"\n', encoding="utf-8")
            local = repo / up.LOCAL_CONFIG_FILENAME
            local.write_text('[conversation]\nlanguage = "en"\n', encoding="utf-8")
            with patch.object(up, "home_config_path", return_value=home_cfg):
                r = up.resolve_conversation_language(root=repo)
        self.assertEqual(r.language, "en")
        self.assertTrue(r.source.startswith("local:"))

    def test_home_config_used(self) -> None:
        with tempfile_dirs() as (repo, home):
            home_cfg = home / "config.toml"
            home_cfg.parent.mkdir(parents=True, exist_ok=True)
            home_cfg.write_text('[conversation]\nlanguage = "ja"\n', encoding="utf-8")
            with patch.object(up, "home_config_path", return_value=home_cfg):
                r = up.resolve_conversation_language(root=repo)
        self.assertEqual(r.language, "ja")
        self.assertTrue(r.source.startswith("home:"))

    def test_os_fallback(self) -> None:
        with tempfile_dirs() as (repo, _home):
            with patch.object(up, "home_config_path", return_value=_home / "missing.toml"):
                with patch.object(up, "os_locale_fallback", return_value="en"):
                    r = up.resolve_conversation_language(root=repo)
        self.assertEqual(r.language, "en")
        self.assertEqual(r.source, "os-locale")

    def test_invalid_language_raises(self) -> None:
        with self.assertRaises(ValueError):
            up.resolve_conversation_language(explicit="fr")

    def test_init_config_creates_template(self) -> None:
        with tempfile_dirs() as (_repo, home):
            home_cfg = home / "config.toml"
            with patch.object(up, "home_config_path", return_value=home_cfg):
                result = up.init_config()
            self.assertEqual(result["action"], "create")
            self.assertTrue(home_cfg.is_file())
            self.assertIn("[conversation]", home_cfg.read_text(encoding="utf-8"))

    def test_sync_writes_locale_rules(self) -> None:
        with tempfile_dirs() as (repo, home):
            home_cfg = home / "config.toml"
            home_cfg.parent.mkdir(parents=True, exist_ok=True)
            home_cfg.write_text('[conversation]\nlanguage = "ja"\n', encoding="utf-8")
            (repo / "rulesync.jsonc").write_text("{}", encoding="utf-8")
            (repo / ".rulesync").mkdir()
            with patch.object(up, "home_config_path", return_value=home_cfg):
                result = up.run_sync(root=repo)
            self.assertEqual(result["language"], "ja")
            cursor_rule = repo / ".cursor" / "rules" / "user-locale.mdc"
            claude_rule = repo / ".claude" / "rules" / "user-locale.md"
            self.assertTrue(cursor_rule.is_file())
            self.assertTrue(claude_rule.is_file())
            self.assertIn("日本語", cursor_rule.read_text(encoding="utf-8"))

    def test_authoring_prefs_defaults(self) -> None:
        with tempfile_dirs() as (repo, home):
            with patch.object(up, "home_config_path", return_value=home / "missing.toml"):
                prefs = up.resolve_authoring_prefs(root=repo)
        self.assertEqual(prefs["default_doc_editorial"], "ja")
        self.assertTrue(prefs["require_en_sync"])


class tempfile_dirs:
    def __enter__(self) -> tuple[Path, Path]:
        import tempfile

        self._repo = tempfile.TemporaryDirectory()
        self._home = tempfile.TemporaryDirectory()
        return Path(self._repo.name), Path(self._home.name)

    def __exit__(self, *args: object) -> None:
        self._repo.cleanup()
        self._home.cleanup()


if __name__ == "__main__":
    unittest.main()
