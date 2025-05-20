from rest_framework.pagination import PageNumberPagination

from .constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


class CustomPagination(PageNumberPagination):
    """
    Универсальный пагинатор для всех эндпоинтов API.
    Позволяет клиенту запрашивать размер страницы через параметр limit,
    но ограничивает максимальный размер страницы.
    """
    page_size = DEFAULT_PAGE_SIZE
    max_page_size = MAX_PAGE_SIZE
    page_size_query_param = 'limit'
