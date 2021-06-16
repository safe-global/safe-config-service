from django.urls import path

from chains.views import ChainsDetailView, ChainsListView

app_name = "chains"

urlpatterns = [
    path("", ChainsListView.as_view(), name="list"),
    path("<pk>/", ChainsDetailView.as_view(), name="detail"),
]
