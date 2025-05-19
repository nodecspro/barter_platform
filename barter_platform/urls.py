from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # For login/logout
from ads import views as ads_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ads/", include("ads.urls")),  # Ads app URLs
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="ads:ad_list"),
        name="logout",
    ),
    path("accounts/signup/", ads_views.SignUpView.as_view(), name="signup"),
    path("", include("ads.urls")),  # Make ads app the root or redirect
]
