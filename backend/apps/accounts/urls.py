from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, LogoutView, MeView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
]
