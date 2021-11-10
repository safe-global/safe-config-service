from django.urls import path

from chains.views import ChainsDetailView, ChainsDetailViewByShortName, ChainsListView

app_name = "chains"

urlpatterns = [
    path("", ChainsListView.as_view(), name="list"),
    path("<int:pk>/", ChainsDetailView.as_view(), name="detail"),
    path(
        "<str:short_name>/",
        ChainsDetailViewByShortName.as_view(),
        name="detail_by_short_name",
    ),
]
