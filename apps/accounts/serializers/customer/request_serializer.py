from helpers.serializer_helper import SerializerHelper

from apps.accounts.services.customer_service import CustomerService
from apps.accounts.models import Customer


class CustomerSerializer(SerializerHelper.ModelSerializer):

    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('code', 'status', 'is_delete', 'deleted_at', 'updated_at', 'created_at')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = CustomerService()
        
    def create(self, validated_data):
        return self.service.create(**validated_data)
        
    def update(self, instance, validated_data):
        return self.service.update(instance, **validated_data)