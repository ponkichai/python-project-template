#!/usr/bin/env python3
"""PreToolUse hook: Write/Edit で保護対象ファイルへの書き込みをブロック。"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

PROTECTED = [
    (r"\.claude/hooks/",                          "CRITICAL", "hook script tampering"),
    (r"\.git/hooks/",                             "CRITICAL", "git hook tampering"),
    (r"\.(bashrc|zshrc|profile|bash_profile)$",   "HIGH",     "shell profile tampering"),
    # 機密ファイルの上書き防止（Defense in Depth）
    (r"(^|/)\.env$",                              "HIGH",     ".env file write"),
    (r"\.(pem|key|p12|pfx)$",                     "HIGH",     "private key file write"),
    (r"(credentials|secrets)(\.ya?ml|\.json|$)",  "HIGH",     "credentials file write"),
]


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") not in ("Write", "Edit", "NotebookEdit"):
        sys.exit(0)

    path = data.get("tool_input", {}).get("file_path", "")
    findings = [(lvl, desc) for pat, lvl, desc in PROTECTED if re.search(pat, path)]
    if not findings:
        sys.exit(0)

    log = Path(".claude/audit.log")
    log.parent.mkdir(exist_ok=True)
    with log.open("a") as f:
        f.write(f"[{datetime.now().isoformat()}] PRE_WRITE BLOCKED: {path}\n")
        for lvl, desc in findings:
            f.write(f"  [{lvl}] {desc}\n")

    print(f"🚨 保護対象ファイルへの書き込みがブロックされました: {path}", file=sys.stderr)
    for lvl, desc in findings:
        print(f"  [{lvl}] {desc}", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
