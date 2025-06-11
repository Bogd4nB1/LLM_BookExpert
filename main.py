import asyncio
from dotenv import dotenv_values # type: ignore
from aiogram import Bot, Dispatcher, F # type: ignore
from aiogram.filters import Command # type: ignore
from aiogram.types import Message # type: ignore
from llm.agent_llm import agent_llm
from llm.agent_sberbank import agent_sberbank
from middleware.check_is_group import AccessMiddleware 

config_dotenv = dotenv_values(".env")

TOKEN = config_dotenv.get("BOT_TOKEN")
CORPORATE_CHAT_ID = config_dotenv.get("CORPORATE_CHAT_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.update.middleware(AccessMiddleware(CORPORATE_CHAT_ID))

# Хранилище для thread_id и истории сообщений каждого пользователя
user_data = {}

@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    user_data[message.from_user.id] = {
        "thread_id": f"{message.from_user.id}_{int(message.date.timestamp())}",
        "last_message_id": message.message_id,
        "agent_type": "default"
    }
    await message.answer(
        "📚 Привет! Я бот-помощник по подбору книг.\n\n"
        "Доступные команды:\n"
        "/start - перезапустить бота\n"
        "/new - начать новый диалог (обычный агент)\n"
        "/sber_new - начать новый диалог (Sberbank агент)\n"
        "/help - справка по использованию"
    )

@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(
        "ℹ️ Справка по использованию бота:\n\n"
        "/start - перезапустить бота\n"
        "/new - начать новый диалог с обычным агентом\n"
        "/sber_new - начать новый диалог с Sberbank агентом\n"
        "/help - показать эту справку\n\n"
        "Просто напишите мне, что вы ищете, и я помогу найти подходящие книги!"
    )

@dp.message(Command("new"))
async def new_dialog_handler(message: Message) -> None:
    thread_id = f"{message.from_user.id}_{int(message.date.timestamp())}"
    user_data[message.from_user.id] = {
        "thread_id": thread_id,
        "last_message_id": message.message_id,
        "agent_type": "default"
    }
    
    await message.answer("✅ Начат новый диалог с обычным агентом. Теперь вы можете отправлять свои запросы для поиска книг.")

@dp.message(Command("sber_new"))
async def new_sber_dialog_handler(message: Message) -> None:
    thread_id = f"{message.from_user.id}_{int(message.date.timestamp())}"
    user_data[message.from_user.id] = {
        "thread_id": thread_id,
        "last_message_id": message.message_id,
        "agent_type": "sberbank"
    }
    
    await message.answer("✅ Начат новый диалог с Sberbank агентом. Теперь вы можете отправлять свои запросы для поиска книг в библиотеке Sberbank.")

@dp.message(F.text)
async def handle_message(message: Message) -> None:
    # Игнорируем текстовые сообщения, которые являются командами
    if message.text.lower() in ["/start", "/new", "/sber_new", "/help"]:
        return
    
    user_id = message.from_user.id
    
    # Если у пользователя нет активной сессии, создаем новую с обычным агентом
    if user_id not in user_data:
        thread_id = f"{user_id}_{int(message.date.timestamp())}"
        user_data[user_id] = {
            "thread_id": thread_id,
            "last_message_id": message.message_id,
            "agent_type": "default"
        }
        await message.answer("ℹ️ Автоматически начат новый диалог с обычным агентом.")
    
    # Обновляем ID последнего сообщения
    user_data[user_id]["last_message_id"] = message.message_id
    
    thread_id = user_data[user_id]["thread_id"]
    config = {"configurable": {"thread_id": thread_id}}
    agent_type = user_data[user_id].get("agent_type", "default")
    
    try:
        # Отправляем "Печатает..." как статус
        await bot.send_chat_action(message.chat.id, "typing")
        
        # Вызываем соответствующий агент в зависимости от типа
        if agent_type == "sberbank":
            resp = agent_sberbank(message.text, config)
        else:
            resp = agent_llm(message.text, config)
        
        # Отправляем ответ пользователю
        try:
            sent_msg = await message.answer(resp, parse_mode="Markdown")
        except:
            # Если Markdown разметка некорректна, отправляем как обычный текст
            sent_msg = await message.answer(resp)
        user_data[user_id]["last_message_id"] = sent_msg.message_id
        
    except Exception as e:
        error_msg = await message.answer(f"Произошла ошибка: {str(e)}")
        user_data[user_id]["last_message_id"] = error_msg.message_id
        # В случае ошибки создаем новую сессию
        user_data[user_id]["thread_id"] = f"{user_id}_{int(message.date.timestamp())}"

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        print("Bot is running...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")