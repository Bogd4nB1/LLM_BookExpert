from dotenv import dotenv_values # type: ignore
from langchain_gigachat.chat_models import GigaChat # type: ignore
from langchain_core.tools import tool # type: ignore
from langgraph.prebuilt import create_react_agent # type: ignore
from langgraph.checkpoint.postgres import PostgresSaver # type: ignore
from service.sberbank import get_and_parse_categories, get_and_parse_books


config_dotenv = dotenv_values(".env")

system_prompt_sberbank = '''Ты бот-помошник по подбору книг в библиотеке Сбербанка. Рекодмендуй книгу по запросу пользователя.
            Если тебе не хватает каких-то данных, запрашивай их у пользователя. Если пользователь запрашивает книгу, то сразу
            выдавай ссылку на нее. Выдавай всю информацию про книгу, которую найдешь.
            '''

# Tools for agent Sberbank

@tool
def get_books_sberbank():
    """
    Возвращение книг из библиотеки Сбербанка. Выдавай стразу все эти данные пользователю.
    isReserved - если False, то книга доступна.
    link - ссылка на книги на их сайте, если пользователь просит ссылку, то выдавай ссылку на сайт.
    description - описание.
    all - все данные.
    """
    print("\033[92m" + "get_books_by_genre_of_sberbank()" + "\033[0m")
    all_books = get_and_parse_books()
    return all_books

@tool
def get_genres_of_sberbank():
    """
    Поиск категорий в библиотеке Сбербанка
    Используется когда пользователь хочеть узнать жанры книг, которые есть в библиотеке Сбербанка.
    Output: name - название категории
    """
    print("\033[92m" + "get_genres_of_sberbank()" + "\033[0m")
    return get_and_parse_categories()


def agent_sberbank(message, config):  
    """
    This function creates and invokes a Sberbank library book recommendation agent.
    
    It utilizes the GigaChat model to process a user's message and recommend books 
    based on the user's criteria. It employs tools specifically for retrieving genres 
    and books from the Sberbank library. The agent operates within a context that 
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
                get_genres_of_sberbank,
                get_books_sberbank,
        ]
        agent = create_react_agent(model,
                                tools=tools,
                                checkpointer=checkpointer,
                                prompt=system_prompt_sberbank)
        resp = agent.invoke({"messages": [("user", message)]}, config=config)
        return resp["messages"][-1].content
