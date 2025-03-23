from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import log_view


extentions_v1_router = DefaultRouter(trailing_slash=False)

admin_logs_urlpatterns = [
    path('logs/<str:filename>/', log_view.LogFileDetailView.as_view(), name='admin_log_file_detail'),
    path('logs/', log_view.LogFilesView.as_view(), name='admin_log_files'),
]
