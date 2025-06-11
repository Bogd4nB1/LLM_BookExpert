from aiogram import BaseMiddleware # type: ignore
from aiogram.types import Message, Update # type: ignore
from typing import Callable, Dict, Any, Awaitable

class AccessMiddleware(BaseMiddleware):
    def __init__(self, corporate_chat_id: str):
        self.corporate_chat_id = corporate_chat_id

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем сообщение из апдейта
        message = self.get_message(event)
        if not message or not message.text:
            return await handler(event, data)
            
        # Пропускаем команду /help без проверки
        if message.text.startswith('/help'):
            return await handler(event, data)
            
        # Для всех остальных команд проверяем доступ
        if not await self.is_user_in_chat(message.from_user.id, data['bot']):
            await message.answer(
                "🚫 Доступ запрещён.\n\n"
                "Для использования бота необходимо быть участником корпоративного чата.\n"
                "Команда /help доступна всем."
            )
            return
            
        return await handler(event, data)

    def get_message(self, update: Update) -> Message | None:
        """Извлекает сообщение из объекта Update"""
        if update.message:
            return update.message
        if update.callback_query and update.callback_query.message:
            return update.callback_query.message
        return None

    async def is_user_in_chat(self, user_id: int, bot) -> bool:
        try:
            member = await bot.get_chat_member(
                chat_id=self.corporate_chat_id,
                user_id=user_id
            )
            return member.status in ['member', 'administrator', 'creator']
        except Exception:
            return False