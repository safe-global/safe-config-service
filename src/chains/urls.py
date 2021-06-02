from django.urls import path

from chains.views import ChainsDetailView, ChainsListView

app_name = "chains"

urlpatterns = [
    path("chains/", ChainsListView.as_view(), name="list"),
    path("chains/<pk>", ChainsDetailView.as_view(), name="detail"),
]
