from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from account.api.account.urls.registration import account_urlpatterns
from account.api.auth.urls import auth_urlpatterns
from habit.api.urls.habits import habit_urlpatterns

apps_urlpatterns = [
    path("auth/", include((auth_urlpatterns, "auth"))),
    path("account/", include((account_urlpatterns, "account"), namespace="account")),
    path("habit/", include((habit_urlpatterns, "habit"))),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-v1/", include((apps_urlpatterns, "api-v1"))),
    path("api-v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api-v1/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
