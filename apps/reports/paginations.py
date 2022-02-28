from rest_framework.pagination import CursorPagination


class CustomerReportPg(CursorPagination):
    ordering = "created_at"
