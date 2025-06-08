import time
from dotenv import dotenv_values # type: ignore
from langchain_gigachat.chat_models import GigaChat # type: ignore
from langchain_core.tools import tool # type: ignore
from langgraph.prebuilt import create_react_agent # type: ignore
from langgraph.checkpoint.memory import MemorySaver # type: ignore
from langgraph.checkpoint.postgres import PostgresSaver # type: ignore
from service.googlebooks import GoogleBooksSearcherByGenre, GoogleBooksUniversalSearch
from service.duckduck_search import duckduckgo_search
import json

memory = MemorySaver()

config = dotenv_values(".env")

model = GigaChat(
    credentials=config.get("GIGACHAT_KEY"),
    scope=config.get("GIGACHAT_SCOPE"),
    model=config.get("GIGACHAT_MODEL"),
    verify_ssl_certs=False,
)

system_prompt = '''Ты бот-помошник по подбору книг. Твоя задача помочь человеку найти книгу по его критериям.
            Если тебе не хватает каких-то данных, запрашивай их у пользователя. Ты можешь выдавать ссылки на книги.'''

@tool
def get_books_by_genre(genre: str):
    """
    Поиск книг по жанру.
    title - название книги
    authors - авторы
    publishedDate - год издания
    categories - жанры
    publisher - издатель
    description - описание
    BuyLink - ссылка на покупку
    thumbnail - ссылка на обложку
    """
    print("\033[92m" + "get_books_by_genre()" + "\033[0m")
    print("\033[92m" + "args: " + genre + "\033[0m")
    searcher = GoogleBooksSearcherByGenre()
    books_by_google = searcher.parse_and_return(genre)
    return books_by_google

@tool
def get_books_universal_search(query: str):
    '''
    Поиск по любым запросам пользователя: название, автор, жанр, описание.
    title - название книги
    authors - авторы
    publishedDate - год издания
    categories - жанры
    publisher - издатель
    description - описание
    BuyLink - ссылка на покупку
    thumbnail - ссылка на обложку
    '''
    print("\033[92m" + "get_books_universal_search()" + "\033[0m")
    print("\033[92m" + "args: " + query + "\033[0m")
    parser = GoogleBooksUniversalSearch()
    parse_result = parser.get_books_info(query)
    result = json.dumps(parse_result, ensure_ascii=False, indent=4)
    return result

@tool
def get_link_on_book(query: str, site: str = "ozon.ru"):
    """
    Поиск ссылки на книгу или автора. Используется когда пользователь хочет узнать ссылку на книгу или автора.
    "title" - Название книги
    "href": - Ссылка на книгу
    "body": - О книге
    """
    print("\033[92m" + "get_link_on_book_or_author()" + "\033[0m")
    print("\033[92m" + "args: " + query + "\033[0m")
    return duckduckgo_search(query=query, site=site)

@tool
def get_links_to_additional_information(query: str):
    """
    Используется когда пользователь хочеть узнать дополниетельную информацию из внешних источников или
    когда у ИИ нет описания или информации о книге.
    "title" - Название статьи
    "href": - Ссылка на статью
    "body": - О статье
    """
    print("\033[92m" + "get_links_to_additional_information()" + "\033[0m")
    print("\033[92m" + "args: " + query + "\033[0m")
    return duckduckgo_search(query=query)

tools = [get_books_by_genre,
         get_books_universal_search,
         get_link_on_book,
         get_links_to_additional_information,
         ]

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
    chat("123456789")

if __name__ == "__main__":
    main()