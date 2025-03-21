from rest_framework import permissions

from django.urls import re_path

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from decouple import config


commit_description = f"Commit: {config('COMMIT_SHA', 'Unknown')}\n \
Author: {config('COMMIT_AUTHOR', 'Unknown')}\n \
Date: {config('COMMIT_TIMESTAMP', 'Unknown')}"

schema_view = get_schema_view(
    openapi.Info(
        title="Pharmago API",
        default_version="v1",
        description=commit_description,
        license=openapi.License(name=config("COMMIT_TITLE", "Unknown")),
    ),
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(),
    public=True,
)

swaggers_urlpatterns = [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$|^swagger$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$|^redoc$",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
