from django.urls import path, include
from . import views

urlpatterns = [
    path(
        "create-scorecard/",
        views.CreateScorecard.as_view(),
        name="create_scorecard",
    ),
    path(
        "get-customer-reports/",
        views.GetCustomerReports.as_view(),
        name="get_customer_reports",
    ),
]
