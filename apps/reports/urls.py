from django.urls import path, include
from . import views

urlpatterns = [
    path(
        "create-scorecard/",
        views.CreateScorecard.as_view(),
        name="create_scorecard",
    ),
]
