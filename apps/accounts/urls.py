from rest_framework.routers import DefaultRouter

from .views.authentiation_view import AuthenticationAPIGenericView
from .views.customer_view import CustomerAPIGenericView
from .views.user_view import UserAPIGenericView

account_v1_router = DefaultRouter(trailing_slash=False)
account_v1_router.register(prefix="customer", viewset=CustomerAPIGenericView, basename="customer")
account_v1_router.register(prefix="auth", viewset=AuthenticationAPIGenericView, basename="auth")
account_v1_router.register(prefix="user", viewset=UserAPIGenericView, basename="user")
