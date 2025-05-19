from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "ads"  # Namespace for templates

# DRF Router
router = DefaultRouter()
router.register(r"api/ads", views.AdViewSet, basename="api_ad")
router.register(
    r"api/proposals", views.ExchangeProposalViewSet, basename="api_proposal"
)

# HTML Views
urlpatterns = [
    path("", views.AdListView.as_view(), name="ad_list"),  # Root of /ads/
    path("my-ads/", views.my_ads_view, name="my_ads"),
    path("create/", views.AdCreateView.as_view(), name="ad_create"),
    path("<int:pk>/", views.AdDetailView.as_view(), name="ad_detail"),
    path("<int:pk>/edit/", views.AdUpdateView.as_view(), name="ad_edit"),
    path("<int:pk>/delete/", views.AdDeleteView.as_view(), name="ad_delete"),
    # Exchange Proposals HTML
    path(
        "propose/<int:ad_receiver_pk>/",
        views.create_exchange_proposal,
        name="proposal_create",
    ),
    path("my-proposals/", views.my_proposals_view, name="my_proposals"),
    path(
        "proposal/<int:proposal_pk>/update/<str:new_status>/",
        views.update_proposal_status,
        name="proposal_update_status",
    ),
    # DRF API URLs
    path("", include(router.urls)),
]
