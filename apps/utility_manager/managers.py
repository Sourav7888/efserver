from django.db import models
from django.db.models import Sum, F, When, Case, DecimalField
from django.db.models.functions import TruncYear


class MonthlyUtilityBillManager(models.Manager):
    """
    Manager for monthly data, returns the monthly usage
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .values("billing_date__month", "billing_date__year", "utility_type")
            .annotate(
                cost=Sum("cost"),
                usage=Sum("usage"),
                unit_cost=Case(
                    When(usage=0.0, then=0.0),
                    When(
                        usage__gt=0.0,
                        then=F("cost") / F("usage"),
                    ),
                    output_field=DecimalField(),
                ),
            )
            .order_by("utility_type")
        )


class YearlyUtilityBillManager(models.Manager):
    """
    Manager for yearly data
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(year=TruncYear("billing_date"))
            .values("year", "utility_type")
            .annotate(
                cost=Sum("cost"),
                usage=Sum("usage"),
                unit_cost=Case(
                    When(usage=0.0, then=0.0),
                    When(
                        usage__gt=0.0,
                        then=F("cost") / F("usage"),
                    ),
                    output_field=DecimalField(),
                ),
            )
            .order_by("year")
        )
