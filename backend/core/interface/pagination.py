from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """Enveloppe unique {count, next, previous, results} pour web et mobile."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
