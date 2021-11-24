from rest_framework.pagination import CursorPagination


class UtilityPg(CursorPagination):
    ordering = "billing_date"
