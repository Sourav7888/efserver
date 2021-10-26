from rest_framework.pagination import CursorPagination


class GetInvestigationsPg(CursorPagination):
    ordering = "investigation_date"
