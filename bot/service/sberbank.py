import requests # type: ignore

def get_and_parse_categories(url="https://api.book.benifits.ru/custom/api/v1/category/all"):
    response = requests.get(url)
    categories = response.json()['body']
    return categories

def get_and_parse_books(url="https://api.book.benifits.ru/custom/api/v1/books/"):
    response = requests.get(url)
    books = response.json()['body']
    return books
