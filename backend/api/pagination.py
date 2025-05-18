from rest_framework.pagination import PageNumberPagination

from .constants import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    PAGE_SIZE_QUERY_PARAM,
    INGREDIENTS_PAGE_SIZE,
    INGREDIENTS_PAGE_SIZE_QUERY_PARAM,
    INGREDIENTS_MAX_PAGE_SIZE
)


class Pagination(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    max_page_size = MAX_PAGE_SIZE
    page_size_query_param = PAGE_SIZE_QUERY_PARAM


class IngredientResultsPagination(PageNumberPagination):
    page_size = INGREDIENTS_PAGE_SIZE
    page_size_query_param = INGREDIENTS_PAGE_SIZE_QUERY_PARAM
    max_page_size = INGREDIENTS_MAX_PAGE_SIZE