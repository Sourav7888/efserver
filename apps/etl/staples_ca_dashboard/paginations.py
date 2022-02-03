from rest_framework.pagination import CursorPagination


class RenewablesPg(CursorPagination):
    ordering = "year"


class LedListPg(CursorPagination):
    ordering = "retrofit_date"


class BillAuditPg(CursorPagination):
    ordering = "facility"
