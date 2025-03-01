from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import RegisterUserView, UserProfileView

urlpatterns = [
    # Регистрация нового пользователя
    path("", RegisterUserView.as_view(), name="user-register"),
    # Получение JWT токена (с заголовком Authorize)
    path("token/", TokenObtainPairView.as_view(), name="token-obtain"),
    # Обновление JWT токена
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", UserProfileView.as_view(), name="user-profile"),
]
