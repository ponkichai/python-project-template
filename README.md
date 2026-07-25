# python-project-template

Python プロジェクトのスターターテンプレート。
**AIエージェント（Claude Code）を隔離コンテナの中で動かす**ことを前提にした構成。

## 含まれるもの

| ファイル/ディレクトリ | 役割 |
|----------------------|------|
| `.devcontainer/` | **AIエージェント隔離サンドボックス**の定義（devcontainer + egress firewall） |
| `Dockerfile` | サンドボックス用イメージ（Python + uv + git + Node、非rootユーザー） |
| `.claude/` | Claude Code の方針・hook・権限 |
| `pyproject.toml` | 依存管理 + Ruff・pytest設定 |
| `.pre-commit-config.yaml` | Ruff lint・format の自動実行 |
| `hooks/pre-commit` | 型チェック（Ty）+ pytest の自動実行 |
| `Makefile` | よく使うコマンドのショートカット |
| `config/` | 設定ファイル（Code/Config分離） |
| `src/` | アプリケーションコード |
| `tests/` | テストコード |

## なぜコンテナで動かすのか（このテンプレートの肝）

AIエージェントにコーディングを任せる＝**シェル・ファイル編集・ネットワークの権限を人間以外に渡す**こと。
`.claude/hooks` が「規律（main保護・機密コミット防止等）」を守るのに対し、
**コンテナは「被害範囲」を守る**——エージェントが暴走・誤操作・注入されても、
ホスト（`~/.ssh`・`~/.aws`・他プロジェクト）とネットワークに手が届かないようにする。

- **檻（コンテナ）**: ソースだけをマウント。ホストの機密はマウントしない。非rootで実行
- **見張り（egress firewall）**: 通信先を GitHub / PyPI / npm / Anthropic API の許可リストに限定（`.devcontainer/init-firewall.sh`）

> ⚠️ Docker はカーネル共有のため**堅牢なセキュリティ境界ではない**。狙った攻撃者への「壁」ではなく、
> 事故・暴走の被害範囲を実務的に狭めるもの。本気の隔離が要るなら VM が上位互換。

## セットアップ

### A. サンドボックスで開く（推奨）

VS Code（Dev Containers 拡張）や Claude Code でこのフォルダを開き、
**「Reopen in Container」** を選ぶ。コンテナ内で自動的に：

1. `postCreateCommand: make setup`（依存インストール・hook登録）
2. `postStartCommand: init-firewall.sh`（通信先を許可リストへ制限）

以降、Claude Code はこのコンテナの中で動く。

### B. サンドボックスを使わずローカルで（最小）

```bash
make setup
```

`uv sync` + `pre-commit install` + pytest hook のリンク作成が走る。
（この場合、隔離は効かない点に注意）

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
├── .devcontainer/
│   ├── devcontainer.json  # サンドボックス定義（非root / firewall起動）
│   └── init-firewall.sh   # egress 許可リスト（見張り）
├── .claude/               # Claude Code 方針・hook・権限
├── config/
│   ├── default.yaml       # デフォルト設定（コミットする）
│   └── local.yaml         # ローカル上書き用（.gitignore済み）
├── hooks/
│   └── pre-commit         # Gitネイティブhookスクリプト
├── src/
│   ├── __init__.py
│   ├── config.py          # 設定読み込みモジュール
│   └── main.py            # エントリーポイント
├── tests/
│   └── test_config.py     # サンプルテスト
├── Dockerfile             # サンドボックス用イメージ
├── Makefile
├── pyproject.toml
└── .pre-commit-config.yaml
```

> アプリを**コンテナイメージとして配布**したくなったら、この Dockerfile（サンドボックス用）とは別に
> `Dockerfile.app`（`CMD ["uv","run","python","src/main.py"]` 等）を用意する。役割を混ぜないこと。
