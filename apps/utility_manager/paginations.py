from rest_framework.pagination import CursorPagination


class DivisionUtilityPg(CursorPagination):
    ordering = "billing_date"
