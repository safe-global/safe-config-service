from django.urls import path

from chains.views import ChainsListView

app_name = "chains"

urlpatterns = [
    path("chains/", ChainsListView.as_view(), name=app_name),
]
