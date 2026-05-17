#!/usr/bin/env python3
"""PostToolUse hook: Python ファイル編集後に ruff lint を自動実行しフィードバックする。"""
import json
import subprocess
import sys


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") not in ("Write", "Edit", "NotebookEdit"):
        sys.exit(0)

    path = data.get("tool_input", {}).get("file_path", "")
    if not path or not path.endswith(".py"):
        sys.exit(0)

    result = subprocess.run(
        ["uv", "run", "ruff", "check", path, "--output-format", "concise"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        sys.exit(0)

    # stdout はClaudeのコンテキストにフィードバックされる
    print(f"[auto-lint] {path} に lint エラーがあります。修正してください:")
    print(result.stdout or result.stderr)


if __name__ == "__main__":
    main()
