"""config.py のテスト。テンプレート付属のサンプルテスト。"""

from src.config import load_config


def test_デフォルト設定が読み込める():
    cfg = load_config("config/default.yaml")
    assert "app" in cfg
    assert "data" in cfg


def test_アプリ名が設定されている():
    cfg = load_config("config/default.yaml")
    assert cfg["app"]["name"] == "my-project"
