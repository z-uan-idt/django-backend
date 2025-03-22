from django.views.static import serve
from django.urls import re_path, path
from django.contrib import admin
from django.conf import settings

from .openapi import swaggers_urlpatterns
from apps.api_urls import api_urlpatterns
from apps.extentions.views import log_view


urlpatterns = [
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),

    path('admin/extentions/logs/<str:filename>/', log_view.LogFileDetailView.as_view(), name='admin_log_file_detail'),
    path('admin/extentions/logs/', log_view.LogFilesView.as_view(), name='admin_log_files'),
    path("admin/", admin.site.urls),
]

urlpatterns += swaggers_urlpatterns
urlpatterns += api_urlpatterns
