from rest_framework import permissions


class Authenticated:
    
    class Customer(permissions.BasePermission):
        def has_permission(self, request, view):
            if request.system != 'customer':
                return False
                
            return bool(
                request.user and
                request.user.is_authenticated and
                isinstance(request.user, request.auth_model)
            )


    class Manage(permissions.BasePermission):
        def has_permission(self, request, view):
            if request.system != 'manage':
                return False
                
            return bool(
                request.user and
                request.user.is_authenticated and
                isinstance(request.user, request.auth_model)
            )