# Nanobot gateway Dockerfile
# Build context: ./nanobot with additional_contexts workspace: .

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY --from=workspace . ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# ---
# Stage 2: Runtime image
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends gosu && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder --chown=nonroot:nonroot /app /app

# Fix workspace permissions - make writable
RUN chmod -R 777 /app/nanobot/workspace

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

USER nonroot

ENTRYPOINT ["python", "/app/nanobot/entrypoint.py"]
