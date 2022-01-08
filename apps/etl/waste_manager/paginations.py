from rest_framework.pagination import CursorPagination


class WasteDataPg(CursorPagination):
    ordering = "pickup_date"
