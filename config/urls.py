from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from .views import health_check

urlpatterns = [
    path("graffiti/", include("graffiti.urls")),
    path(
        "admin/login/",
        RedirectView.as_view(pattern_name="account_login", query_string=True),
    ),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("health/", health_check, name="health"),
    path("", include("pages.urls")),
    path("people/", include("people.urls")),
    path("prose/", include("prose.urls")),
    re_path(r"^taggit/", include("taggit_selectize.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEV_TOOLS:
    urlpatterns += [path("__reload__", include("django_browser_reload.urls"))]
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]

handler404 = "pages.views.handler404"
