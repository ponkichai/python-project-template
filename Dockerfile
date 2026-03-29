FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# lockファイルを使って厳密に再現インストール（本番用: --no-dev）
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY . .

ENV CONFIG_PATH=config/docker.yaml

CMD ["uv", "run", "python", "src/main.py"]
