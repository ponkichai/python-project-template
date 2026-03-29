#!/usr/bin/env python3
"""PostToolUse hook: WebFetch/WebSearch/GitHub MCP 結果のプロンプトインジェクション検出。"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

PATTERNS = [
    (r"ignore\s+(previous|above|all)\s+instructions?", "CRITICAL", "指示の上書き試行"),
    (r"you\s+are\s+now\s+",                            "CRITICAL", "ロール書き換え試行"),
    (r"disregard\s+(your|all)\s+",                     "CRITICAL", "指示の無視命令"),
    (r"new\s+instructions?:?",                          "HIGH",     "指示の挿入"),
    (r"<\s*/?system\s*>",                              "HIGH",     "systemタグ挿入"),
    (r"system\s*prompt",                               "HIGH",     "システムプロンプト言及"),
    (r"forget\s+(everything|what)",                     "MEDIUM",   "記憶の消去命令"),
    (r"as\s+an?\s+(ai|llm|assistant).{0,30}you\s+(must|should)", "MEDIUM", "AIへの直接命令"),
]


def extract_text(obj: object) -> str:
    """JSON オブジェクトから再帰的にテキストを抽出する。"""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return " ".join(extract_text(v) for v in obj.values())
    if isinstance(obj, list):
        return " ".join(extract_text(v) for v in obj)
    return ""


def main() -> None:
    data = json.load(sys.stdin)
    tool_name = data.get("tool_name", "")
    is_target = (
        tool_name in ("WebFetch", "WebSearch")
        or tool_name.startswith("mcp__github__")
    )
    if not is_target:
        sys.exit(0)

    content = extract_text(data.get("tool_result", ""))
    findings = [(lvl, desc) for pat, lvl, desc in PATTERNS if re.search(pat, content, re.IGNORECASE)]
    if not findings:
        sys.exit(0)

    log = Path(".claude/audit.log")
    log.parent.mkdir(exist_ok=True)
    with log.open("a") as f:
        f.write(f"[{datetime.now().isoformat()}] POST_WEB ({tool_name}):\n")
        for lvl, desc in findings:
            f.write(f"  [{lvl}] {desc}\n")

    critical_or_high = [f for f in findings if f[0] in ("CRITICAL", "HIGH")]
    print("🚨 外部コンテンツに不審なパターンが検出されました", file=sys.stderr)
    for lvl, desc in findings:
        print(f"  [{lvl}] {desc}", file=sys.stderr)

    if critical_or_high:
        print("ブロックします。オーナーに確認を要請してください。", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
