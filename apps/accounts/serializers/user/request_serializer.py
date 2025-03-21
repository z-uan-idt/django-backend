from helpers.serializer_helper import SerializerHelper

from apps.accounts.services.user_service import UserService
from apps.accounts.models import User


class UserSerializer(SerializerHelper.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by','deleted_by', 'created_at',
                            'updated_at', 'deleted_at', 'code', 'status', 'is_delete')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = UserService()
        
    def create(self, validated_data):
        return self.service.create(**validated_data)
        
    def update(self, instance, validated_data):
        return self.service.update(instance, **validated_data)