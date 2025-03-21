from django.urls import path, include

from .accounts.urls import account_v1_router

version_routers = {
    "v1": [account_v1_router]
}

api_urlpatterns = [
    path(f"api/{ver}/", include(api_ver_router.urls))
    for ver, routers in version_routers.items()
    for api_ver_router in routers
]