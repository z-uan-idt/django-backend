from rest_framework.routers import DefaultRouter

from django.urls import path, include

from typing import List


class RouterHelper:
    @staticmethod
    def urlpatterns(ver: str, routers: List[DefaultRouter]):
        api_urlpatterns = []

        for router in routers:
            api_urlpatterns.append(path(f"api/{ver}/", include(router.urls)))

        return api_urlpatterns
