from django.utils.deprecation import MiddlewareMixin
from django.apps import apps

from config.settings import JWT_CONFIG

from helpers.token_helper import HttpSystem


class MultiTableAuthMiddleware(MiddlewareMixin):
    
    def process_request(self, request):
        key, value = self.get_auth_system_name(request)

        setattr(request, key, value)

        if getattr(request, key) == HttpSystem.CUSTOMER:
            request.auth_model = apps.get_model('accounts', 'Customer')
        else:
            request.auth_model = apps.get_model('accounts', 'User')
            
    def get_auth_system_name(self, request):
        key = JWT_CONFIG.get("AUTH_SYSTEM_NAME", "HTTP_SYSTEM")
        value = request.META.get(key, HttpSystem.MANAGE)

        if value not in [HttpSystem.CUSTOMER, HttpSystem.MANAGE]:
            value = HttpSystem.MANAGE
        
        return key, value