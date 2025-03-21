from django.views.static import serve
from django.urls import re_path, path
from django.contrib import admin
from django.conf import settings

from .openapi import swaggers_urlpatterns
from apps.api_urls import api_urlpatterns


urlpatterns = [
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    path("admin/", admin.site.urls),
]

urlpatterns += swaggers_urlpatterns
urlpatterns += api_urlpatterns
