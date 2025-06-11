# Книжный эксперт на базе LLM GigaChat

## 📚 Описание проекта

Рекомендательная система на базе LLM GigaChat, которая подбирает книги по вкусу пользователя и находит ссылки для их приобретения в интернете.

## 🛠️ Технологический стек

- **Backend**: Python + aiogram
- **LLM**: GigaChat-2 (Sberbank AI)
- **Веб-поиск**: Парсинг книжных магазинов

## 🚀 Запуск проекта

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Bogd4nB1/LLM_BookExpert.git
```

2. Перейдите в него:
```bash
cd LLM_BookExpert
```

3. Установите зависимости (для uv):
```bash
uv sync
```

4. Создайте файл `.env` с вашими учетными данными:
```env
GIGACHAT_API_KEY=ваш_api_ключ
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_MODEL=GigaChat-2-Pro
```

5. Запустите фалй:
```bash
uv run main.py
```