from django.urls import re_path, path, include
from django.views.static import serve
from django.contrib import admin
from django.conf import settings

from .openapi import swaggers_urlpatterns
from apps.app_urls import app_urlpatterns
from apps.extentions.urls import admin_logs_urlpatterns


urlpatterns = [
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    path("admin/extentions/", include(admin_logs_urlpatterns)),
    path("admin/", admin.site.urls),
]

urlpatterns += swaggers_urlpatterns
urlpatterns += app_urlpatterns
