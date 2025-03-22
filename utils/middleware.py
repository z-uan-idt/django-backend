from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.apps import apps

import jwt

from helpers import bigger, smaller


class MultiTableAuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.system = request.META.get('HTTP_SYSTEM', 'manage')
        
        if request.system == 'customer':
            request.auth_model = apps.get_model('accounts', 'Customer')
        else:
            request.auth_model = apps.get_model('accounts', 'User')