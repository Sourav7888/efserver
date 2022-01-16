from rest_framework.pagination import CursorPagination


class RenewablesPg(CursorPagination):
    ordering = "year"
