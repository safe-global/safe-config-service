# SPDX-License-Identifier: FSL-1.1-MIT
from django.urls import path

from chains.views import (
    ChainsDetailView,
    ChainsDetailViewByShortName,
    ChainsListView,
    GasTokensListView,
)

app_name = "chains"

urlpatterns = [
    path("", ChainsListView.as_view(), name="list"),
    path("<int:pk>/", ChainsDetailView.as_view(), name="detail"),
    path("<int:pk>/gas-tokens/", GasTokensListView.as_view(), name="gas-tokens-list"),
    path(
        "<str:short_name>/",
        ChainsDetailViewByShortName.as_view(),
        name="detail_by_short_name",
    ),
]
