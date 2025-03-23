from django.urls import path, include

from .accounts.urls import accounts_v1_router
from .extentions.urls import extentions_v1_router


version_routers = {
    "v1": [
        accounts_v1_router,
        extentions_v1_router
    ]
}

app_urlpatterns = [
    path(f"api/{ver}/", include(api_ver_router.urls))
    for ver, routers in version_routers.items()
    for api_ver_router in routers
]