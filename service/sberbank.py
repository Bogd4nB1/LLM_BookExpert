import requests # type: ignore

def get_and_parse_categories(url="https://api.book.benifits.ru/custom/api/v1/category/all"):
    """
    Fetches and parses book categories from the specified API endpoint.

    Args:
        url (str): The API endpoint to fetch categories from. Defaults to 
        "https://api.book.benifits.ru/custom/api/v1/category/all".

    Returns:
        list: A list of categories obtained from the API response.
    """
    response = requests.get(url)
    categories = response.json()['body']
    return " | ".join(category['name'] for category in categories)

def get_and_parse_books(url="https://api.book.benifits.ru/custom/api/v1/books/"):
    """
    Fetches and parses books from the specified API endpoint.

    Args:
        url (str): The API endpoint to fetch books from. Defaults to 
        "https://api.book.benifits.ru/custom/api/v1/books/".

    Returns:
        list: A list of books obtained from the API response.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка HTTP-статуса
        books = response.json()['body']
        
        return [
            {
                "id": book['id'],
                "link": f"https://api.book.benifits.ru/custom/api/v1/books/{book['id']}",
                "isReserved": book['isReserved'],
                "all": f"{book['name']} | {book['author']} | {book['category']['name']}",
                "desccription": book['description']
            }
            for book in books
            if all(key in book for key in ['id', 'isReserved', 'name', 'author', 'category', 'description'])
        ]
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
        return books if 'books' in locals() else []
