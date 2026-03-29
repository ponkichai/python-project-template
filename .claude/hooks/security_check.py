#!/usr/bin/env python3
"""
PreToolUse hook: Bash コマンド実行前に危険なパターンを検出する。

Claude Code から標準入力でツール情報（JSON）が渡される。
exit code 2 でブロック、0 で通過。
"""

import json
import re
import sys

# 危険なコマンドパターン
DANGEROUS_PATTERNS = [
    (r"curl\s+.+\|\s*(bash|sh)", "curl pipe to shell"),
    (r"wget\s+.+\|\s*(bash|sh)", "wget pipe to shell"),
    (r"eval\s*\$\(", "eval with command substitution"),
    (r"base64\s+-d.+\|\s*(bash|sh)", "base64 decode pipe to shell"),
    (r"rm\s+-rf\s+/(?!\S)", "rm -rf /"),
    (r">\s*/etc/", "write to /etc/"),
    (r"chmod\s+777", "chmod 777"),
]

# 機密パスパターン
SENSITIVE_PATHS = [
    r"/etc/passwd",
    r"/etc/shadow",
    r"~/\.ssh/",
    r"~/.aws/credentials",
    r"\.env$",
]


def check_command(command: str) -> list[tuple[str, str]]:
    """コマンド文字列を検査し、検出された(レベル, 説明)のリストを返す。"""
    findings = []

    for pattern, description in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            findings.append(("CRITICAL", description))

    for pattern in SENSITIVE_PATHS:
        if re.search(pattern, command, re.IGNORECASE):
            findings.append(("HIGH", f"sensitive path access: {pattern}"))

    return findings


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # JSON解析失敗は通過させる

    tool_name = data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    findings = check_command(command)
    if not findings:
        sys.exit(0)

    # 検出された場合はブロック
    print("🚨 セキュリティチェック: 危険なコマンドが検出されました", file=sys.stderr)
    for level, description in findings:
        print(f"  [{level}] {description}", file=sys.stderr)
    print(f"  コマンド: {command[:200]}", file=sys.stderr)
    print("実行を中断します。意図した操作であれば直接ターミナルで実行してください。", file=sys.stderr)

    sys.exit(2)  # exit code 2 = ブロック


if __name__ == "__main__":
    main()
