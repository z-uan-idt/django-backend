from rest_framework import exceptions, authentication, HTTP_HEADER_ENCODING

from config.settings import JWT_CONFIG

import helpers
import jwt

from helpers.token_helper import Token, HttpSystem



class MultiAuthentication(authentication.BaseAuthentication):

    prefix = JWT_CONFIG.get('AUTH_HEADER_TYPE', 'Bearer')
    algorithm = JWT_CONFIG.get('ALGORITHM', 'HS256')
    signing_key = JWT_CONFIG.get('SIGNING_KEY', '')
    
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
        auth_model = getattr(request, 'auth_model')
        claim_key = self.get_claim_key(request)
        
        if not auth_model:
            raise exceptions.AuthenticationFailed('Invalid token')
        
        try:
            unverified_payload = Token.decode_token(token)
            payload_user_id = unverified_payload.get(claim_key)

            if not payload_user_id:
                raise exceptions.AuthenticationFailed('Invalid token')
            
            try:
                user = auth_model.objects.get(pk=payload_user_id)
            except auth_model.DoesNotExist:
                raise exceptions.AuthenticationFailed('Invalid token')
            
            if user.is_delete:
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
        
        if not auth or auth[0].lower() != self.prefix.lower().encode():
            return None
        
        return auth
    
    def get_authorization_header(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', b'')
        if isinstance(auth, str):
            auth = auth.encode(HTTP_HEADER_ENCODING)
        return auth
            
    def get_claim_key(self, request):
        HTTP_SYSTEM = JWT_CONFIG.get("AUTH_SYSTEM_NAME", "HTTP_SYSTEM")
        claim_key = request.META.get(HTTP_SYSTEM, HttpSystem.MANAGE)
        setattr(request, HttpSystem.KEY, claim_key)
        if claim_key == HttpSystem.CUSTOMER:
            return JWT_CONFIG["CUSTOMER_CLAIM"]
        return JWT_CONFIG["USER_CLAIM"]