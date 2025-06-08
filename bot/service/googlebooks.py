import requests # type: ignore
import json

class GoogleBooksUniversalSearch:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/books/v1/volumes"
    
    def search_books(self, query: str):
        """Выполняет поиск книг по запросу"""
        params = {
            'q': query,
            'maxResults': 10,
            'printType': 'books'
        }
        response = requests.get(self.base_url, params=params)
        return response.json()
    
    def parse_book_data(self, raw_data: dict) -> list:
        """Парсит сырые данные и возвращает структурированную информацию"""
        parsed_books = []
        
        if not raw_data.get('items'):
            return parsed_books
        
        for book in raw_data['items']:
            volume_info = book.get('volumeInfo', {})
            sale_info = book.get('saleInfo', {})
            
            # Извлекаем только год из даты публикации
            published_date = volume_info.get('publishedDate', '')
            if '-' in published_date:
                published_date = published_date.split('-')[0]
            
            parsed_book = {
                'title': volume_info.get('title', 'Название не указано'),
                'authors': volume_info.get('authors', ['Автор не указан']),
                'publishedDate': published_date,
                'categories': volume_info.get('categories', ['Жанр не указан']),
                'publisher': volume_info.get('publisher', 'Издатель не указан'),
                'description': volume_info.get('description', 'Описание отсутствует'),
                'BuyLink': sale_info.get('buyLink', 'Недоступно для покупки')
            }
            parsed_books.append(parsed_book)
        
        return parsed_books
    
    def get_books_info(self, query: str) -> dict:
        """Основной метод для получения информации о книгах"""
        raw_data = self.search_books(query)
        parsed_data = self.parse_book_data(raw_data)
        
        return {
            'query': query,
            'count': len(parsed_data),
            'books': parsed_data
        }

class GoogleBooksSearcherByGenre:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/books/v1/volumes"
    
    def search_by_genre(self, genre_query: str):
        """
        Выполняет поиск книг по указанному жанру с использованием Google Books API.
        Возвращает JSON-данные о найденных книгах.
        """
        params = {
            'q': f'subject:{genre_query}',
            'maxResults': 10,
            'printType': 'books'
        }
        response = requests.get(self.base_url, params=params)
        return response.json()
    
    def _clean_published_date(self, date_str):
        """Очищает строку с датой публикации, оставляя только год."""
        if isinstance(date_str, str) and '-' in date_str:
            return date_str.split('-')[0]
        return date_str
    
    def parse_book_data(self, books_json):
        """
        Парсит полученные от API данные и формирует удобный словарь с информацией о книгах.
        """
        parsed_books = []
        
        # Проверяем наличие книг в ответе
        if not books_json.get('items'):
            return {"error": "No books found", "count": 0, "books": []}
        
        for book in books_json['items']:
            volume_info = book.get('volumeInfo', {})
            
            # Извлекаем основную информацию о книге
            book_data = {
                "title": volume_info.get('title', 'Название не указано'),
                "authors": volume_info.get('authors', ['Автор не указан']),
                "publishedDate": self._clean_published_date(volume_info.get('publishedDate', 'Год не указан')),
                "categories": volume_info.get('categories', ['Жанр не указан']),
                "publisher": volume_info.get('publisher', 'Издатель не указан'),
                "description": volume_info.get('description', 'Описание отсутствует'),
                "BuyLink": volume_info.get('infoLink', ''),
            }
            
            parsed_books.append(book_data)
        
        return {
            "count": len(parsed_books),
            "books": parsed_books
        }
    
    def parse_and_return(self, genre_query: str):
        """
        Полностью обрабатывает запрос — ищет книги по жанру и парсит данные.
        Возвращает готовый JSON с результатами.
        """
        books_data = self.search_by_genre(genre_query)
        parsed_data = self.parse_book_data(books_data)
        return json.dumps(parsed_data, indent=2, ensure_ascii=False)
