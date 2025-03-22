from rest_framework import exceptions, authentication, HTTP_HEADER_ENCODING
from rest_framework import HTTP_HEADER_ENCODING

from django.conf import settings

import jwt

import helpers


class MultiAuthentication(authentication.BaseAuthentication):

    token_prefix = 'Bearer'
    
    def authenticate(self, request):
        authorization = self.verify_authorization_header(request)
        
        if not authorization:
            return None
            
        if helpers.equal(authorization, 1):
            raise exceptions.AuthenticationFailed('Invalid token header. No credentials provided')
        elif helpers.bigger(authorization, 2):
            raise exceptions.AuthenticationFailed('Invalid token header. Token string should not contain spaces')
            
        try:
            token = authorization[1].decode()
        except UnicodeError:
            raise exceptions.AuthenticationFailed('Invalid token header. Token string should not contain invalid characters')
            
        return self.authenticate_credentials(request, token)
        
    def authenticate_credentials(self, request, token):
        auth_system = getattr(request, 'system', 'manage')
        auth_model = getattr(request, 'auth_model')
        
        if not auth_model:
            raise exceptions.AuthenticationFailed('Invalid token')
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            token_system = payload.get('system', 'manage')
            token_user_id = payload.get('user_id')
            
            if not token_user_id or auth_system != token_system:
                raise exceptions.AuthenticationFailed('Invalid token')
            
            try:
                user = auth_model.objects.get(pk=token_user_id)
            except auth_model.DoesNotExist:
                raise exceptions.AuthenticationFailed('Invalid token')
            
            if not user.is_delete:
                raise exceptions.AuthenticationFailed('Invalid token')
            
            return (user, token)
        except jwt.exceptions.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.exceptions.DecodeError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except jwt.exceptions.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')

    def verify_authorization_header(self, request):
        auth = self.get_authorization_header(request).split()
        
        if not auth or auth[0].lower() != self.token_prefix.lower().encode():
            return None
        
        return auth
    
    def get_authorization_header(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', b'')
        if isinstance(auth, str):
            auth = auth.encode(HTTP_HEADER_ENCODING)
        return auth