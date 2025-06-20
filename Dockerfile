FROM python:3.12-slim-bookworm

# Установка uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN chmod +x /bin/uv

# Установка зависимостей
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

# Копирование приложения и очистка кэша
COPY . /app
WORKDIR /app
RUN find . -type f -name "*.pyc" -delete && \
    find . -type d -name "__pycache__" -delete

# Создание пользователя для безопасности
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["sh", "-c", "uv run start_memory.py && uv run main.py"]