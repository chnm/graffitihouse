from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """`?page=` plus a `?page_size=` override, capped so one call stays cheap."""

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 500
