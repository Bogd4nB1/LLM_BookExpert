# Книжный эксперт на базе LLM GigaChat

## 📚 Описание проекта

Рекомендательная система на базе LLM GigaChat, которая подбирает книги по вкусу пользователя и находит ссылки для их приобретения в интернете.

## 📅 Планы развития

- **Веб-интерфейс** с чатом (в разработке)
- **Интеграция с внешними книжными сервисами** (в разработке)

## 🛠️ Технологический стек

- **Backend**: Python + aiogram
- **LLM**: GigaChat-2 (Sberbank AI)
- **Веб-поиск**: Парсинг API книжных магазинов

## 🚀 Запуск проекта

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Bogd4nB1/LLM_BookExpert.git
```

2. Перейдите в него:
```bash
cd LLM_BookExpert
```

3. Создайте файл `.env` с вашими учетными данными:
```env
GIGACHAT_API_KEY=ваш_api_ключ
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_MODEL=модель_llm
BOT_TOKEN=token
DB=postgresql://<username>:<password>@postgres:5432/bookexpert?sslmode=disable
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_USER=
CORPORATE_CHAT_ID="id канала или группы"
```

4. Соберите образ:
```bash
docker compose build
```

5. Запуск:
```bash
docker compose up
```


