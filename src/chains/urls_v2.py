from django.urls import path

from chains.views import ChainsDetailViewV2, ChainsListViewV2

app_name = "chains"

urlpatterns = [
    path("", ChainsListViewV2.as_view(), name="list"),
    path("<pk>/", ChainsDetailViewV2.as_view(), name="detail"),
]
