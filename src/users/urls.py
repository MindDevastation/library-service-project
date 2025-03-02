from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import RegisterUserView, UserProfileView

urlpatterns = [
    path("", RegisterUserView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", UserProfileView.as_view(), name="profile"),
]
