.PHONY: setup lint type-check test audit check

# 初回セットアップ（一度だけ実行）
# pre-commit framework が唯一のgit hook管理者。
# コミット時に Ruff・gitleaks・型チェック・テストが自動実行される（.pre-commit-config.yaml）
setup:
	uv sync
	uv run pre-commit install
	@echo "✅ セットアップ完了"

# lint + format
lint:
	uv run ruff check --fix src/ tests/
	uv run ruff format src/ tests/

# 型チェック
type-check:
	uv run ty check src/

# テスト（カバレッジ付き）
test:
	uv run pytest tests/ --cov=src --cov-report=term-missing

# 依存パッケージの既知脆弱性スキャン（ネットワーク必要のためcheckとは分離）
audit:
	uv run pip-audit

# 全チェック（CI相当）
check: lint type-check test
