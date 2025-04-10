import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

urlpatterns = [
    path("graffiti/", include("graffiti.urls")),
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
    path("people/", include("people.urls")),
    path("__reload__", include("django_browser_reload.urls")),
    path("prose/", include("prose.urls")),
    re_path(r"^taggit/", include("taggit_selectize.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
