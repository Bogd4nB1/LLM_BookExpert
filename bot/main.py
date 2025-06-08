import asyncio
from dotenv import dotenv_values # type: ignore
from aiogram import Bot, Dispatcher, F # type: ignore
from aiogram.filters import Command # type: ignore
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton # type: ignore
from aiogram.methods import DeleteMessage # type: ignore
from llm import agent

config = dotenv_values(".env")

TOKEN = config.get("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище для thread_id и истории сообщений каждого пользователя
user_data = {}

async def delete_all_messages(chat_id: int, last_message_id: int):
    """Функция для удаления видимых сообщений в чате"""
    try:
        # Будем удалять сообщения в обратном порядке, начиная с последнего
        # Удаляем только сообщения, начиная с текущего и выше (новые имеют больший message_id)
        for msg_id in range(last_message_id, last_message_id - 100, -1):
            try:
                await bot(DeleteMessage(chat_id=chat_id, message_id=msg_id))
                await asyncio.sleep(0.1)  # Задержка для избежания флуда
            except:
                continue
    except Exception as e:
        print(f"Ошибка при удалении сообщений: {e}")

@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    user_data[message.from_user.id] = {
        "thread_id": f"{message.from_user.id}_{int(message.date.timestamp())}",
        "last_message_id": message.message_id
    }
    await message.answer(
        "📚 Привет! Я бот-помощник по подбору книг.\n\n"
        "Доступные команды:\n"
        "/new - начать новый диалог\n"
        "/clear - очистить историю чата\n"
        "/help - справка по использованию"
    )

@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(
        "ℹ️ Справка по использованию бота:\n\n"
        "/start - перезапустить бота\n"
        "/new - начать новый диалог (сбросить контекст)\n"
        "/clear - очистить историю сообщений в чате\n"
        "/help - показать эту справку\n\n"
        "Просто напишите мне, что вы ищете, и я помогу найти подходящие книги!"
    )

@dp.message(Command("new"))
async def new_dialog_handler(message: Message) -> None:
    thread_id = f"{message.from_user.id}_{int(message.date.timestamp())}"
    user_data[message.from_user.id] = {
        "thread_id": thread_id,
        "last_message_id": message.message_id
    }
    
    await message.answer("✅ Начат новый диалог. Теперь вы можете отправлять свои запросы для поиска книг.")

@dp.message(Command("clear"))
async def clear_chat_handler(message: Message) -> None:
    user_id = message.from_user.id
    if user_id in user_data:
        last_msg_id = user_data[user_id].get("last_message_id", message.message_id)
    else:
        last_msg_id = message.message_id
    
    # Отправляем подтверждение перед очисткой
    confirm_msg = await message.answer(
        "Вы уверены, что хотите очистить весь чат? Это действие нельзя отменить.\n"
        "Отправьте 'да' для подтверждения или 'нет' для отмены.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="да"), KeyboardButton(text="нет")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    
    # Сохраняем ID сообщения с подтверждением
    user_data[user_id] = user_data.get(user_id, {})
    user_data[user_id]["confirmation_msg_id"] = confirm_msg.message_id
    user_data[user_id]["last_message_id"] = last_msg_id

@dp.message(F.text.lower() == "да")
async def confirm_clear_chat(message: Message) -> None:
    user_id = message.from_user.id
    if user_id not in user_data:
        return
    
    # Удаляем сообщение с подтверждением
    try:
        await bot(DeleteMessage(
            chat_id=message.chat.id,
            message_id=user_data[user_id]["confirmation_msg_id"]
        ))
    except:
        pass
    
    # Удаляем все видимые сообщения в чате
    await delete_all_messages(message.chat.id, user_data[user_id]["last_message_id"])
    
    # Создаем новую сессию
    thread_id = f"{user_id}_{int(message.date.timestamp())}"
    user_data[user_id] = {
        "thread_id": thread_id,
        "last_message_id": message.message_id
    }
    
    # Отправляем новое стартовое сообщение
    start_msg = await message.answer(
        "Чат был полностью очищен. Начинаем новый диалог.\n"
        "Чем я могу вам помочь?"
    )
    user_data[user_id]["last_message_id"] = start_msg.message_id

@dp.message(F.text.lower() == "нет")
async def cancel_clear_chat(message: Message) -> None:
    user_id = message.from_user.id
    if user_id not in user_data:
        return
    
    # Удаляем сообщение с подтверждением
    try:
        await bot(DeleteMessage(
            chat_id=message.chat.id,
            message_id=user_data[user_id]["confirmation_msg_id"]
        ))
    except:
        pass
    
    await message.answer("Очистка чата отменена.")

@dp.message(F.text)
async def handle_message(message: Message) -> None:
    # Игнорируем текстовые сообщения, которые являются командами
    if message.text.lower() in ["/start", "/new", "/clear", "/help", "да", "нет"]:
        return
    
    user_id = message.from_user.id
    
    # Если у пользователя нет активной сессии, создаем новую
    if user_id not in user_data:
        thread_id = f"{user_id}_{int(message.date.timestamp())}"
        user_data[user_id] = {
            "thread_id": thread_id,
            "last_message_id": message.message_id
        }
        await message.answer("ℹ️ Автоматически начат новый диалог.")
    
    # Обновляем ID последнего сообщения
    user_data[user_id]["last_message_id"] = message.message_id
    
    thread_id = user_data[user_id]["thread_id"]
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Отправляем "Печатает..." как статус
        await bot.send_chat_action(message.chat.id, "typing")
        
        # Вызываем агента с сообщением пользователя
        resp = await asyncio.to_thread(
            agent.invoke,
            {"messages": [("user", message.text)]},
            config=config
        )
        
        # Получаем последний ответ от агента
        assistant_response = resp["messages"][-1].content
        
        # Отправляем ответ пользователю
        sent_msg = await message.answer(assistant_response)
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