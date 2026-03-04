from django.urls import path

from account.api.account.views.registration import (
    ActivateEmailView,
    LoginView,
    RegistrationView,
    ResendCodeOnEmailView,
)

account_urlpatterns = [
    path(
        "register/",
        RegistrationView.as_view(),
        name="register",
    ),
    path(
        "activate/",
        ActivateEmailView.as_view(),
        name="activate",
    ),
    path(
        "resend-activation/",
        ResendCodeOnEmailView.as_view(),
        name="resend-activation",
    ),
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
]
