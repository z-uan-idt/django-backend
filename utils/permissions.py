from rest_framework import permissions

from helpers.token_helper import HttpSystem


class Authenticated:
    
    class Customer(permissions.BasePermission):
        def has_permission(self, request, view):
            return HttpSystem.is_customer(request) and bool(
                request.user and
                request.user.is_authenticated and
                isinstance(request.user, request.auth_model)
            )


    class Manage(permissions.BasePermission):
        def has_permission(self, request, view):
            return HttpSystem.is_manage(request) and bool(
                request.user and
                request.user.is_authenticated and
                isinstance(request.user, request.auth_model)
            )