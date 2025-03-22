from rest_framework import serializers

from constants.error_messages import ErrorMessages
from helpers.token_helper import Token

from ..models.utils.validators import validate_phone_number

from .customer.response_serializer import CustomerDetailSerializer
from .user.response_serializer import UserDetailSerializer


class AuthenticationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        error_messages=ErrorMessages.CharField('Số điện thoại', 128),
        validators=[validate_phone_number],
        allow_blank=False,
        max_length=128,
        required=True,
    )
    password = serializers.CharField(
        error_messages=ErrorMessages.CharField('Mật khẩu', 128),
        allow_blank=False,
        max_length=128,
        required=True,
    )
    
    def get_user_json(self, system):
        if system == "customer":
            return CustomerDetailSerializer(self.user).data
        return UserDetailSerializer(self.user).data
        
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError('Vui lòng truyền request trong context')

        try:
            self.user = request.auth_model.objects.get(phone_number=phone_number, is_delete=False)

            if not self.user.check_password(password):
                raise serializers.ValidationError('Thông tin đăng nhập không chính xác')
        except:
            raise serializers.ValidationError(f'Thông tin đăng nhập không chính xác')

        token = Token(user_id=self.user.id, request=request)
        
        return {
            "access_token": token.access_token,
            "refresh_token": token.refresh_token,
            "user": self.get_user_json(token.HTTP_SYSTEM)
        }