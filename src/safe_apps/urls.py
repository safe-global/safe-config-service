from django.urls import path

from .views import SafeAppsListView

app_name = "apps"

urlpatterns = [
    path("", SafeAppsListView.as_view(), name="list"),
]
