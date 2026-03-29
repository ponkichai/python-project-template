.PHONY: setup lint type-check test check

# 初回セットアップ（一度だけ実行）
setup:
	uv sync
	pre-commit install
	ln -sf ../../hooks/pre-commit .git/hooks/pre-commit
	chmod +x hooks/pre-commit
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

# 全チェック（CI相当）
check: lint type-check test
