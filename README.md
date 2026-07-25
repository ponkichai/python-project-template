# python-project-template

AI時代の開発を前提にした Python プロジェクトのスターターテンプレート。
**特定のAIハーネスに依存しない**——人間だけの開発でも劣化せず、どのエージェント（Claude Code / Codex / Cursor / Gemini CLI 等）で開いても同じ規律が効く構成。

## 設計原則：規律は3層で守る（ハーネス非依存）

規律の実体はハーネスの外にあり、ハーネス層は薄いアダプタに過ぎない（`docs/adr/0001` 参照）。

| 層 | 実体 | 守るもの | 効く相手 |
|----|------|---------|---------|
| **環境層** | devcontainer + egress firewall | 被害範囲 | どのエージェントでも |
| **リポジトリ層** | pre-commit（Ruff・gitleaks・型・テスト）+ CI | 品質・機密 | 人間・どのエージェントでも |
| **ハーネス層** | `.claude/`（任意） | 多層防御のボーナス | Claude Code のみ |

**健全性のテスト**：`.claude/` を丸ごと削除しても品質保証は一切劣化しない。

## 含まれるもの

| ファイル/ディレクトリ | 層 | 役割 |
|----------------------|----|------|
| `.devcontainer/` + `Dockerfile` | 環境 | **AIエージェント隔離サンドボックス**（devcontainer + egress firewall、非root） |
| `.pre-commit-config.yaml` | リポジトリ | コミット時に Ruff・**gitleaks（機密検出）**・型チェック・テストを自動実行 |
| `.github/workflows/ci.yml` | リポジトリ | push/PR時に上記全チェック + **pip-audit（依存脆弱性）** + gitleaks（履歴走査） |
| `AGENTS.md` | リポジトリ | エージェント向け指示の**正本**（業界標準形式） |
| `CLAUDE.md` | ハーネス | `AGENTS.md` へのシンボリックリンク（Claude Code 用アダプタ） |
| `CONTEXT.md` | リポジトリ | ユビキタス言語（用語集）の正本 |
| `docs/` | リポジトリ | `workflow.md`（開発フロー正本）・`architecture.md`・`conventions.md`・`adr/` |
| `specs/` | リポジトリ | 機能仕様書（SDD） |
| `.claude/` | ハーネス | Claude Code 専用の任意アダプタ（hook による危険コマンド遮断・注入検知、スキル、権限） |
| `Makefile` / `pyproject.toml` / `config/` / `src/` / `tests/` | リポジトリ | タスク・依存・Code/Config分離・コード・テスト |

## なぜコンテナで動かすのか

AIエージェントにコーディングを任せる＝**シェル・ファイル編集・ネットワークの権限を人間以外に渡す**こと。
リポジトリ層が「規律」を守るのに対し、**コンテナは「被害範囲」を守る**——エージェントが暴走・誤操作・注入されても、
ホスト（`~/.ssh`・`~/.aws`・他プロジェクト）とネットワークに手が届かないようにする。

- **檻（コンテナ）**: ソースだけをマウント。ホストの機密はマウントしない。非rootで実行
- **見張り（egress firewall）**: 通信先を GitHub / PyPI / npm / Anthropic API の許可リストに限定（`.devcontainer/init-firewall.sh`）

> ⚠️ Docker はカーネル共有のため**堅牢なセキュリティ境界ではない**。狙った攻撃者への「壁」ではなく、
> 事故・暴走の被害範囲を実務的に狭めるもの。本気の隔離が要るなら VM が上位互換。

## セットアップ

### A. サンドボックスで開く（推奨）

VS Code（Dev Containers 拡張）や各種エージェントCLIでこのフォルダを開き、
**「Reopen in Container」** を選ぶ。コンテナ内で自動的に：

1. `postCreateCommand: make setup`（依存インストール・hook登録）
2. `postStartCommand: init-firewall.sh`（通信先を許可リストへ制限）

### B. サンドボックスを使わずローカルで（最小）

```bash
make setup
```

`uv sync` + `pre-commit install` が走り、以降コミットのたびに
Ruff・gitleaks・型チェック・テストが自動実行される。（この場合、隔離は効かない点に注意）

## よく使うコマンド

```bash
make lint        # Ruff lint + format
make type-check  # Ty 型チェック
make test        # pytest（カバレッジ付き）
make check       # 上記すべて（CI相当）
make audit       # 依存パッケージの既知脆弱性スキャン（pip-audit）
```

## 開発フロー（DDD → SDD → TDD → AIDD）

新機能は4段階で作る。**正本は `docs/workflow.md`**（人間・エージェント共通。Claude Code なら `/new-feature` スキルが同ファイルを参照して進行する）。

| 順 | 略語 | 意味 | やること |
|----|------|------|----------|
| 0 | **DDD** | ドメイン駆動設計 | 新しい用語が出たら `CONTEXT.md` の用語集に追記し、以降その言葉で統一する |
| 1 | **SDD** | 仕様駆動開発 | `specs/<機能名>.md`（`specs/_template.md` 参照）に入力・出力・仕様・除外スコープを書く |
| 2 | **TDD** | テスト駆動開発 | Specを元に `tests/test_<機能名>.py` を先に書く（この時点では全て失敗する） |
| 3 | **AIDD** | AI駆動開発 | Spec・テストを踏まえて `src/<機能名>.py` を実装し、`make check` が通ることを確認する |

DDDは軽量版のみ採用しており、`domain/application/infrastructure` のような層状ディレクトリは作らない。
「用語をコード全体で統一する」「ドメインロジックをI/Oから分離する」の2点だけを徹底する（詳細は `docs/conventions.md`）。

## ディレクトリ構造

```
.
├── AGENTS.md              # エージェント指示の正本（ハーネス中立）
├── CLAUDE.md              # → AGENTS.md へのsymlink（Claude Code用アダプタ）
├── CONTEXT.md             # ユビキタス言語（用語集）の正本
├── .devcontainer/
│   ├── devcontainer.json  # サンドボックス定義（非root / firewall起動）
│   └── init-firewall.sh   # egress 許可リスト（見張り）
├── .claude/               # Claude Code 専用の任意アダプタ（hook・スキル・権限）
├── .github/workflows/
│   └── ci.yml             # lint・型・テスト・pip-audit・gitleaks
├── config/
│   ├── default.yaml       # デフォルト設定（コミットする）
│   └── local.yaml         # ローカル上書き用（.gitignore済み）
├── docs/
│   ├── workflow.md        # 開発フロー正本（DDD→SDD→TDD→AIDD）
│   ├── architecture.md    # アーキテクチャ概要
│   ├── conventions.md     # コード規約 + 軽量DDD原則
│   └── adr/               # 設計判断の記録
├── specs/
│   └── _template.md       # Specテンプレート（SDD）
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
