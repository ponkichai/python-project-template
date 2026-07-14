# === AIエージェント隔離サンドボックス用イメージ ===
# 目的: Claude Code(AIエージェント)を「このコンテナの中」で動かし、
#       ホスト環境（~/.ssh, ~/.aws, 他プロジェクト等）から隔離して被害範囲を閉じ込める。
# これは「アプリを実行して出荷する本番イメージ」ではない。
# アプリのコンテナ配布が必要になったら Dockerfile.app 等を別途用意すること。
FROM python:3.12-slim

# --- 開発サンドボックスに必要な基盤パッケージ ---
# git            : バージョン管理
# curl,ca-certs  : パッケージ/メタ情報の取得
# iptables,ipset : egress ファイアウォール(init-firewall.sh)用
# dnsutils       : dig（許可リストのドメイン→IP解決）
# sudo           : 起動時にファイアウォールを設定するため dev ユーザーへ限定付与
# nodejs,npm     : Claude Code CLI の実行基盤
RUN apt-get update && apt-get install -y --no-install-recommends \
      git curl ca-certificates sudo iptables ipset dnsutils \
      nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# uv（高速な Python パッケージ管理）を公式イメージからコピー
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# --- 非root ユーザー（コンテナ脱出時の被害を限定）---
ARG USERNAME=dev
RUN useradd -m -s /bin/bash ${USERNAME} \
    # firewall 設定だけを NOPASSWD で許可（sudo 全開放はしない）
    && echo "${USERNAME} ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" \
       > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

# egress ファイアウォール初期化スクリプトを配置（起動時に devcontainer が実行）
COPY .devcontainer/init-firewall.sh /usr/local/bin/init-firewall.sh
RUN chmod +x /usr/local/bin/init-firewall.sh

WORKDIR /workspace

# 依存を先に入れてレイヤキャッシュを効かせる。
# 本番イメージと違い dev 依存（ruff/pytest 等）も含める＝サンドボックス内で lint/test するため。
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-install-project || true

USER ${USERNAME}

# サンドボックスは「常駐する作業環境」。アプリを実行して終了はしない。
# devcontainer 経由なら不要だが、`docker run` 単体でも生かしておくためのフォールバック。
CMD ["sleep", "infinity"]
