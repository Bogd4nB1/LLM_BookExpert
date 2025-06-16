from duckduckgo_search import DDGS # type: ignore
import json

def duckduckgo_search(
    query: str,
    site: str = None,
    region: str = "ru-ru",
    safesearch: str = "off",
    timelimit: str = "y",
    max_results: int = 5,
    json_indent: int = 2,
    status: bool = None
) -> str:
    """
    Выполняет поиск через DuckDuckGo и возвращает результаты в формате JSON.
    
    Args:
        query: Поисковый запрос
        site: Ограничить поиск конкретным сайтом (например 'ozon.ru')
        region: Регион для поиска (по умолчанию 'ru-ru')
        safesearch: Фильтр безопасного поиска ('on', 'moderate', 'off')
        timelimit: Ограничение по времени ('d', 'w', 'm', 'y')
        max_results: Максимальное количество результатов
        json_indent: Отступ для форматирования JSON
    
    Returns:
        Строка с результатами поиска в формате JSON
    """
    if status:
        full_query = f"Купить книгу {query}, site:{site}" if site else query
    else:
        full_query = f"{query}, site:{site}" if site else query
    
    try:
        # Выполняем поиск
        results = DDGS().text(
            full_query,
            region=region,
            safesearch=safesearch,
            timelimit=timelimit,
            max_results=max_results
        )
        print("Query: " + full_query)
        print(f"DuckDuckGO: {results}")
        return results
    
    except Exception as e:
        # В случае ошибки возвращаем JSON с описанием ошибки
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=json_indent)
    

