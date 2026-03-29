#!/usr/bin/env python3
"""
PostToolUse hook: WebFetch / WebSearch の結果を受け取った直後にスキャンする。

外部コンテンツに含まれるプロンプトインジェクション試行を検出する。
exit code 2 でブロック、0 で通過。
"""

import json
import re
import sys

# プロンプトインジェクションのパターン
INJECTION_PATTERNS = [
    (r"ignore\s+(previous|above|all)\s+instructions?", "CRITICAL", "指示の上書き試行"),
    (r"you\s+are\s+now\s+", "CRITICAL", "ロール書き換え試行"),
    (r"disregard\s+(your|all)\s+", "CRITICAL", "指示の無視命令"),
    (r"new\s+instructions?:?", "HIGH", "新しい指示の挿入"),
    (r"system\s*prompt", "HIGH", "システムプロンプトへの言及"),
    (r"<\s*/?system\s*>", "HIGH", "systemタグの挿入"),
    (r"as\s+an?\s+(ai|llm|assistant).{0,30}(you\s+must|you\s+should)", "MEDIUM", "AIへの直接命令"),
    (r"forget\s+(everything|what)", "MEDIUM", "記憶の消去命令"),
]


def scan_content(content: str) -> list[tuple[str, str, str]]:
    """コンテンツをスキャンし (レベル, パターン名, マッチ箇所) のリストを返す。"""
    findings = []
    for pattern, level, description in INJECTION_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            findings.append((level, description, str(matches[0])))
    return findings


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("WebFetch", "WebSearch"):
        sys.exit(0)

    # ツール結果のテキストを取得
    tool_result = data.get("tool_result", "")
    if isinstance(tool_result, dict):
        content = tool_result.get("content", "")
    elif isinstance(tool_result, str):
        content = tool_result
    else:
        sys.exit(0)

    findings = scan_content(content)
    if not findings:
        sys.exit(0)

    critical_or_high = [f for f in findings if f[0] in ("CRITICAL", "HIGH")]

    print("🚨 外部コンテンツスキャン: 不審なパターンが検出されました", file=sys.stderr)
    for level, description, match in findings:
        print(f"  [{level}] {description}: '{match}'", file=sys.stderr)

    if critical_or_high:
        print("このコンテンツの適用をブロックします。オーナーに確認を要請してください。", file=sys.stderr)
        sys.exit(2)  # CRITICAL/HIGH → ブロック
    else:
        print("警告: 内容を慎重に確認してから利用してください。", file=sys.stderr)
        sys.exit(0)  # MEDIUM → 警告のみ・通過


if __name__ == "__main__":
    main()
