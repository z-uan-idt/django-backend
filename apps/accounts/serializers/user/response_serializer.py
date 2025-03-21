from rest_framework import serializers

from apps.accounts.models import User


class UserShortDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'phone_number', 'code', 'full_name')


class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
