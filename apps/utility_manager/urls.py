from django.urls import path, include
from . import views

patterns = [
    path(
        "bulk-create-utility/",
        views.BulkCreateUtility.as_view(),
        name="bulk_create_utility",
    )
]

urlpatterns = [path("", include(patterns))]
