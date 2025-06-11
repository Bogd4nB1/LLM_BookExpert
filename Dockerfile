# Используем официальный образ Python с поддержкой uv
FROM python:3.12-slim-bookworm

# Устанавливаем uv (менеджер зависимостей от Astral)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN chmod +x /bin/uv

# Копируем только файлы зависимостей для кэширования слоев
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости (без кода проекта)
RUN uv sync --locked --no-dev

# Копируем остальные файлы проекта
COPY . /app
WORKDIR /app

# Загружаем переменные из .env (для разработки)
# В продакшене используйте `docker-compose.yml` или секреты Docker/Kubernetes
ENV GIGACHAT_KEY=${GIGACHAT_KEY} \
    GIGACHAT_SCOPE=${GIGACHAT_SCOPE} \
    GIGACHAT_MODEL=${GIGACHAT_MODEL} \
    BOT_TOKEN=${BOT_TOKEN} \
    DB=${DB} \
    CORPORATE_CHAT_ID=${CORPORATE_CHAT_ID}

# Запуск приложения через uv
CMD ["sh", "-c", "uv run start_memory.py && uv run main.py"]