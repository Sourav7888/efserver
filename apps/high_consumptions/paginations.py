from rest_framework.pagination import CursorPagination


class HCPg(CursorPagination):
    ordering = "usage_increase"
    page_size = 5000


class HCReportTrackerPg(CursorPagination):
    ordering = "created_at"
    page_size = 5000
