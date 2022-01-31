from rest_framework.pagination import CursorPagination


class HCPg(CursorPagination):
    ordering = "usage_increase"
    page_size = 1000
