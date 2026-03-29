"""設定読み込みモジュール。config/*.yaml を読み込む。"""

import os
from pathlib import Path

import yaml


def load_config(path: str | None = None) -> dict:
    """YAML設定ファイルを読み込む。

    環境変数 CONFIG_PATH が設定されている場合はそちらを優先。
    未指定の場合は config/default.yaml を使用。
    """
    config_path = path or os.environ.get("CONFIG_PATH", "config/default.yaml")
    with Path(config_path).open() as f:
        return yaml.safe_load(f)
