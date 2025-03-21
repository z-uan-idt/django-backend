from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

import jwt

from helpers import bigger, smaller

from apps.accounts.models import Customer, User


class MultiTableAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.user = AnonymousUser()

        auth_header: str = request.META.get('HTTP_AUTHORIZATION', '')
        parse_auth_header = auth_header.split(' ')
        
        if bigger(parse_auth_header, 2) or smaller(parse_auth_header, 2):
            return None

        token = parse_auth_header[1]
        system = parse_auth_header[0].lower()
            
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get(settings.SIMPLE_JWT.get('USER_ID_CLAIM', 'user_id'))
            
            if user_id is None:
                return None
            
            if system == 'Token':
                user = Customer.objects.get(pk=user_id)
            else:
                user = User.objects.get(pk=user_id)
            
            request.user = user
            
        except (InvalidToken, TokenError, jwt.PyJWTError, User.DoesNotExist, Customer.DoesNotExist):
            pass
            
        return None