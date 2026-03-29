# python-project-template

Python プロジェクトのスターターテンプレート。

## 含まれるもの

| ファイル/ディレクトリ | 役割 |
|----------------------|------|
| `Dockerfile` | Docker環境の定義（uv使用） |
| `pyproject.toml` | 依存管理 + Ruff・pytest設定 |
| `.pre-commit-config.yaml` | Ruff lint・format の自動実行 |
| `hooks/pre-commit` | 型チェック（Ty）+ pytest の自動実行 |
| `Makefile` | よく使うコマンドのショートカット |
| `config/` | 設定ファイル（Code/Config分離） |
| `src/` | アプリケーションコード |
| `tests/` | テストコード |

## セットアップ

```bash
make setup
```

これ一発で以下が完了します：
- `uv sync`（依存インストール）
- `pre-commit install`（Ruff hookの登録）
- pytest hookのシンボリックリンク作成

## よく使うコマンド

```bash
make lint        # Ruff lint + format
make type-check  # Ty 型チェック
make test        # pytest（カバレッジ付き）
make check       # 上記すべて（CI相当）
```

## ディレクトリ構造

```
.
├── config/
│   ├── default.yaml   # デフォルト設定（コミットする）
│   ├── docker.yaml    # Docker環境用設定（コミットする）
│   └── local.yaml     # ローカル上書き用（.gitignore済み）
├── hooks/
│   └── pre-commit     # Gitネイティブhookスクリプト
├── src/
│   ├── __init__.py
│   ├── config.py      # 設定読み込みモジュール
│   └── main.py        # エントリーポイント
├── tests/
│   └── test_config.py # サンプルテスト
├── Dockerfile
├── Makefile
├── pyproject.toml
└── .pre-commit-config.yaml
```
