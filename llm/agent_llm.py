from dotenv import dotenv_values # type: ignore
from langchain_gigachat.chat_models import GigaChat # type: ignore
from langchain_core.tools import tool # type: ignore
from langgraph.prebuilt import create_react_agent # type: ignore
from langgraph.checkpoint.postgres import PostgresSaver # type: ignore
from service.googlebooks import GoogleBooksSearcherByGenre, GoogleBooksUniversalSearch, search_google
from service.duckduck_search import duckduckgo_search
import json


config_dotenv = dotenv_values(".env")

system_prompt_llm = '''Ты бот-помошник по подбору книг. Твоя задача помочь человеку найти книгу по его критериям.
            Если тебе не хватает каких-то данных, запрашивай их у пользователя. Выдавай сразу всю информацию о книге, которую нашел.
            Пример: Если пользователь задал вопрос: Я хочу почитать книгу Понедельник начинается в субботу.
            Ответ: Ты вызываешь метод get_books_universal_search и метод для покупки этой книги get_link_on_book
            '''

# Tools for agent LLM

@tool
def get_books_by_genre(genre: str):
    """
    Поиск книг по жанру. Переводи жанр на английский язык. Если результатов нет, то вызывай метод get_books_universal_search
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
    Поиск по любым запросам пользователя: название, автор, жанр, описание. Переводи жанр на английский язык.
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
def get_link_on_book(query: str):
    """
    Поиск ссылок на покупку книги. Используется когда пользователь хочет узнать ссылки на книгу.
    Выдавай все ссылки, которые найдешь.
    "title" - Название книги
    "href": - Ссылка на книгу
    "body": - О книге
    """
    print("\033[92m" + "get_link_on_book()" + "\033[0m")
    print("\033[92m" + "args: " + query + "\033[0m")
    duck = duckduckgo_search(query=query, site="ozon.ru", status=True)
    return duck

@tool
def get_links_to_additional_information(query: str):
    """
    Используется когда пользователь хочеть узнать дополниетельную информацию из внешних источников или
    когда у ИИ нет описания или информации о книге. Выдавай все результаты.
    "title" - Название статьи
    "href": - Ссылка на статью
    "body": - О статье
    """
    print("\033[92m" + "get_links_to_additional_information()" + "\033[0m")
    print("\033[92m" + "args: " + query + "\033[0m")
    duck = duckduckgo_search(query=query, status=False)
    return duck


def agent_llm(message, config):
    """
    This function creates and invokes a LLM library book recommendation agent.
    
    It utilizes the GigaChat model to process a user's message and recommend books 
    based on the user's criteria. It employs tools specifically for retrieving genres 
    and books from the LLM library. The agent operates within a context that 
    manages a Postgres checkpoint to ensure data integrity.
    
    Args:
        message (str): The input message from the user containing book search criteria.
        config (dict): Configuration settings for the agent, including database and 
                       model credentials.
    
    Returns:
        str: The content of the agent's response, which is a book recommendation or 
             additional information request.
    """
    with PostgresSaver.from_conn_string(config_dotenv.get("DB")) as checkpointer:
        model = GigaChat(
            credentials=config_dotenv.get("GIGACHAT_KEY"),
            scope=config_dotenv.get("GIGACHAT_SCOPE"),
            model=config_dotenv.get("GIGACHAT_MODEL"),
            verify_ssl_certs=False,
        )
        tools = [
                get_books_by_genre,
                get_link_on_book,
                get_links_to_additional_information,
                get_books_universal_search,
        ]
        agent = create_react_agent(model,
                                tools=tools,
                                checkpointer=checkpointer,
                                prompt=system_prompt_llm)
        resp = agent.invoke({"messages": [("user", message)]}, config=config)
        return resp["messages"][-1].content