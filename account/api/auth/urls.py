from django.urls import path

from account.api.auth.views import (
    JWTTokenObtainPairView,
    JWTTokenRefreshView,
    JWTTokenVerifyView,
)


auth_urlpatterns = [
    path("jwt/create/", JWTTokenObtainPairView.as_view(), name="jwt-create"),
    path("jwt/refresh/", JWTTokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", JWTTokenVerifyView.as_view(), name="jwt-verify"),
]
