from datetime import datetime
from typing import Dict, Any

from config.settings import JWT_CONFIG

import uuid
import jwt


class HttpSystem:
    KEY = "claim"
    MANAGE = "manage"
    CUSTOMER = "customer"
    
    @classmethod
    def is_manage(cls, request):
        return getattr(request, cls.KEY, None) == cls.MANAGE
    
    @classmethod
    def is_customer(cls, request):
        return getattr(request, cls.KEY, None) == cls.CUSTOMER


class Token:
    
    REFRESH_TOKEN_LIFETIME = JWT_CONFIG.get('REFRESH_TOKEN_LIFETIME', 30)  # days
    TOKEN_LIFETIME = JWT_CONFIG.get('TOKEN_LIFETIME', 5)  # minutes

    CUSTOMER_CLAIM = JWT_CONFIG.get('CUSTOMER_CLAIM', 'customer_id')
    USER_CLAIM = JWT_CONFIG.get('USER_CLAIM', 'user_id')

    ALGORITHM = JWT_CONFIG.get('ALGORITHM', 'HS256')
    SIGNING_KEY = JWT_CONFIG.get('SIGNING_KEY', '')
    
    HTTP_SYSTEM = HttpSystem.MANAGE
    
    def __init__(self, user_id: str, request):
        self.claim_key = self.__get_claim_key(request)
        self.user_id = user_id
            
    def __get_claim_key(self, request):
        AUTH_SYSTEM_NAME = JWT_CONFIG.get("AUTH_SYSTEM_NAME", "HTTP_SYSTEM")
        self.HTTP_SYSTEM = request.META.get(AUTH_SYSTEM_NAME, HttpSystem.MANAGE)
        if self.HTTP_SYSTEM == HttpSystem.CUSTOMER:
            return self.CUSTOMER_CLAIM
        return self.USER_CLAIM
        
    def __get_lifetime(self, token_type) -> datetime:
        return datetime.now() + (self.REFRESH_TOKEN_LIFETIME if token_type == "refresh" else self.TOKEN_LIFETIME)
        
    def __get_payload(self, token_type: str) -> Dict[str, Any]:
        expiry = self.__get_lifetime(token_type)
        
        payload = {
            self.claim_key: self.user_id,
            "exp": int(expiry.timestamp()),
            "jti": str(uuid.uuid4().hex)[:8],
        }
        
        return payload
        
    def __str__(self) -> str:
        return self.refresh_token
    
    @property
    def refresh_token(self) -> str:
        return jwt.encode(self.__get_payload("refresh"), self.SIGNING_KEY, self.ALGORITHM)
    
    @property
    def access_token(self) -> str:
        return jwt.encode(self.__get_payload("access"), self.SIGNING_KEY, self.ALGORITHM)
    
    @classmethod
    def decode_token(cls, token: str) -> Dict[str, Any]:
        return jwt.decode(
            token, 
            cls.SIGNING_KEY,
            algorithms=[cls.ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True
            }
        )