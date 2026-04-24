# syntax=docker/dockerfile:1.9
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

RUN uv run playwright install-deps chromium && \
    uv run playwright install chromium

COPY src/ ./src/
RUN uv sync --frozen --no-dev

RUN useradd --create-home --uid 1000 botrunner && \
    chown -R botrunner:botrunner /app /opt/playwright-browsers
USER botrunner

ENTRYPOINT ["uv", "run", "python", "-m", "waf_bots"]
CMD ["--help"]
