from django.urls import path

from .views import SafeAppsListView

app_name = 'apps'

urlpatterns = [
    path('safe-apps/', SafeAppsListView.as_view()),
]
