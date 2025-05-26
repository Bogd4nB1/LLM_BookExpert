import time
from typing import Dict
from dotenv import dotenv_values
from langchain_gigachat.chat_models import GigaChat
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from database.data import stuff_database

memory = MemorySaver()

config = dotenv_values(".env")

model = GigaChat(
    credentials=config.get("GIGACHAT_KEY"),
    scope=config.get("GIGACHAT_SCOPE"),
    model=config.get("GIGACHAT_MODEL"),
    verify_ssl_certs=False,
)

system_prompt = '''Ты бот-продавец книг. Твоя задача продать книги пользователю, 
            получив от него заказ. 
            Если тебе не хватает каких-то данных, запрашивай их у пользователя.'''


@tool
def get_all_book_names() -> str:
    """Возвращает названия моделей всех телефонов ф формате json"""
    # Подсвечивает вызов функции зеленым цветом
    print("\033[92m" + "Bot requested get_all_book_names()" + "\033[0m")
    return ", ".join([stuff["name"] for stuff in stuff_database])

@tool
def get_books_by_tags(tags: str) -> Dict:
    """
    Возвращает книги по тегам.
    """
    print("\033[92m" + f"Bot requested get_book_by_tags({tags})" + "\033[0m")
    tags = tags.split(", ")
    for stuff in stuff_database:
        for tag in tags:
            if tag in stuff["tags"]:
                return stuff

    return {"error": "Книга с таким тегом не найдена"}

    

@tool
def get_book_data_by_name(name: str) -> Dict:
    """
    Возвращает цену в долларах, характеристики и описание телефона по точному названию модели.

    Args:
        name (str): Точное название книги.

    Returns:
        Dict: Словарь с информацией о книге (цена, название и описание).
    """
    # Подсвечивает вызов функции зеленым цветом
    print("\033[92m" + f"Bot requested get_book_data_by_name({name})" + "\033[0m")
    for stuff in stuff_database:
        if stuff["name"] == name.strip():
            return stuff

    return {"error": "Книга с таким названием не найдена"}

@tool
def get_book_reviews(name: str) -> Dict:
    """
    Возвращает отзывы о книге.

    Args:
        name (str): Название книги.

    Returns:
        Dict: Словарь с информацией о книге (цена, название и описание).
    """
    # Подсвечивает вызов функции зеленым цветом
    print("\033[92m" + f"Bot requested get_book_reviews({name})" + "\033[0m")
    for stuff in stuff_database:
        if stuff["name"] == name.strip():
            return stuff["reviews"]

    return {"error": "Книга с таким названием не найдена"}

@tool
def create_order(name: str, phone: str) -> None:
    """
    Создает новый заказ на книгу.

    Args:
        name (str): Название книги.
        phone (str): Телефонный номер пользователя.

    Returns:
        str: Статус заказа.
    """
    # Подсвечивает вызов функции зеленым цветом
    print("\033[92m" + f"Bot requested create_order({name}, {phone})" + "\033[0m")
    print(f"!!! NEW ORDER !!! {name} {phone}")

tools = [create_order, get_book_data_by_name,get_all_book_names, get_book_reviews, get_books_by_tags]
agent = create_react_agent(model,
                           tools=tools,
                           checkpointer=MemorySaver(),
                           prompt=system_prompt)

def chat(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    while(True):
        rq = input("\n\033[36m[Human]: \033[0m")
        if rq == "":
            break
        resp = agent.invoke({"messages": [("user", rq)]}, config=config)
        print("\n\033[35m[Assistant]: \033[0m", resp["messages"][-1].content)
        time.sleep(1) # For notebook capability

def main():
    chat("123456")

if __name__ == "__main__":
    main()