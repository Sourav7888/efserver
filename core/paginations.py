from rest_framework.pagination import CursorPagination


class DivisionPg(CursorPagination):
    ordering = "division_name"


class FacilityPg(CursorPagination):
    ordering = "facility_name"
