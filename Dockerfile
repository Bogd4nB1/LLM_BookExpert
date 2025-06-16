FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN chmod +x /bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev

COPY . /app
WORKDIR /app

CMD ["sh", "-c", "uv run start_memory.py && uv run main.py"]