from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    page_size = 5
    max_page_size = 20
    page_size_query_param = 'limit'


class IngredientResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
