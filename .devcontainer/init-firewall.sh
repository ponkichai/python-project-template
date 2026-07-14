#!/usr/bin/env bash
# === egress ファイアウォール（許可リスト方式）===
# 目的: サンドボックス内の AI エージェントが、意図しない外部へ
#       データを送る / 不審な場所から取りに行く のを防ぐ「見張り」。
# 方針: OUTPUT はデフォルト DROP。DNS・localhost・確立済み接続と、
#       開発に必要な許可ドメイン(GitHub/PyPI/npm/Anthropic)のみ通す。
#
# 注意（過信しないための明記）:
# - 許可リストは「解決した IP」ベース。CDN の IP ローテーションで
#   稀に許可先へ繋がらなくなることがある（その場合は再実行）。
# - Docker はカーネル共有のため堅牢な境界ではない。事故・暴走の
#   被害範囲を実務的に狭めるもの。本気の隔離が要るなら VM を検討。
set -euo pipefail

# 既存ルール初期化
iptables -F
iptables -X 2>/dev/null || true
ipset destroy allowed 2>/dev/null || true
ipset create allowed hash:net

# ドメイン→IP を解決して許可セットへ追加
add_domain() {
  for ip in $(dig +short A "$1" | grep -E '^[0-9.]+$'); do
    ipset add allowed "$ip" 2>/dev/null || true
  done
}

# GitHub の公開 IP レンジは meta API から取得（多数のホストに分散するため）
if command -v curl >/dev/null 2>&1; then
  curl -s https://api.github.com/meta 2>/dev/null \
    | grep -oE '"[0-9.]+/[0-9]+"' | tr -d '"' \
    | while read -r cidr; do ipset add allowed "$cidr" 2>/dev/null || true; done || true
fi

# 開発に必要な許可ドメイン
for d in \
  github.com api.github.com codeload.github.com objects.githubusercontent.com \
  pypi.org files.pythonhosted.org \
  registry.npmjs.org \
  api.anthropic.com \
  ; do add_domain "$d"; done

# デフォルトポリシー: 受信・転送・送信すべて DROP
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

# loopback は許可
iptables -A INPUT  -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# 確立済み・関連パケットは許可（応答を受け取れるように）
iptables -A INPUT  -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# DNS（名前解決を許可しないと何も引けない）
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT

# 許可リスト宛の送信のみ通す
iptables -A OUTPUT -p tcp -m set --match-set allowed dst -j ACCEPT

echo "✅ egress firewall applied (allowlist only)"
