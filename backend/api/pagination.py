from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """
    Универсальный пагинатор для всех эндпоинтов API.
    Позволяет клиенту запрашивать размер страницы через параметр limit,
    но ограничивает максимальный размер страницы.
    """
    page_size = settings.DEFAULT_PAGE_SIZE
    max_page_size = settings.MAX_PAGE_SIZE
    page_size_query_param = 'limit'
