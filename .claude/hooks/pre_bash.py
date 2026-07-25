#!/usr/bin/env python3
"""PreToolUse hook: Bash コマンドの安全性をスキャン。exit 2 でブロック。"""
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PATTERNS = [
    # コマンドインジェクション
    (r"curl\s+.+\|\s*(ba)?sh",                          "CRITICAL", "curl pipe to shell"),
    (r"wget\s+.+\|\s*(ba)?sh",                          "CRITICAL", "wget pipe to shell"),
    (r"eval\s*\$\(",                                     "CRITICAL", "eval injection"),
    (r"base64\s+-d.+\|\s*(ba)?sh",                      "CRITICAL", "base64 decode to shell"),
    (r"bash\s+-i\s+>&\s*/dev/tcp",                      "CRITICAL", "reverse shell"),
    (r"python3?\s+-c\s+['\"].*os\.(system|exec|popen)", "CRITICAL", "python -c os exec"),
    # データ窃取
    (r"curl\s+.+\s+-d\s+@",                             "HIGH",     "curl file upload"),
    (r"\|\s*nc\s+\S+\s+\d+",                            "HIGH",     "netcat exfiltration"),
    (r"(cat|curl)\s+.*\.(ssh|aws|env).*\|",             "HIGH",     "credentials exfiltration"),
    # hook・設定の改ざん
    (r"\.claude/hooks/",                                 "CRITICAL", "hook script tampering"),
    (r"git\s+config.+core\.hookspath",                   "HIGH",     "git hook path override"),
    # 破壊的操作
    (r"rm\s+-rf\s+(~/|/home/|/Users/)",                 "HIGH",     "rm home directory"),
    (r">\s*/etc/",                                       "HIGH",     "write to /etc/"),
    (r"chmod\s+777",                                     "MEDIUM",   "chmod 777"),
]


def check_main_branch_commit(cmd: str) -> list[tuple[str, str]]:
    """mainブランチへの直接コミット/プッシュを検出する。"""
    if not re.search(r"git\s+(commit|push)\b", cmd):
        return []
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.SubprocessError:
        return []
    if branch in ("main", "master"):
        return [("HIGH", f"mainブランチ ({branch}) への直接コミット/プッシュ — feature branchを使うこと")]
    return []


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        sys.exit(0)

    cmd = data.get("tool_input", {}).get("command", "")
    findings = [(lvl, desc) for pat, lvl, desc in PATTERNS if re.search(pat, cmd, re.IGNORECASE)]
    findings += check_main_branch_commit(cmd)

    if not findings:
        sys.exit(0)

    log = Path(".claude/audit.log")
    log.parent.mkdir(exist_ok=True)
    with log.open("a") as f:
        f.write(f"[{datetime.now().isoformat()}] PRE_BASH BLOCKED: {cmd[:200]}\n")
        for lvl, desc in findings:
            f.write(f"  [{lvl}] {desc}\n")

    print("🚨 危険なコマンドが検出されました", file=sys.stderr)
    for lvl, desc in findings:
        print(f"  [{lvl}] {desc}", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
