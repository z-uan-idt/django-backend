from rest_framework import serializers

from apps.accounts.models import Customer


class CustomerShortDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ('id', 'phone_number', 'code', 'full_name')


class CustomerDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = '__all__'
