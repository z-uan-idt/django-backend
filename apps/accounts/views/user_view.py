from utils.permissions import Authenticated
from utils.views import APIGenericView
from utils.decorators import api

from django.db import transaction

from ..serializers.user import request_serializer, response_serializer

from ..services.user_service import UserService


SWAGGER_TAGS = ["Accounts: User"]


class UserAPIGenericView(APIGenericView):
    permission_classes = [Authenticated.Manage]
    
    action_serializers = {
        'list_response': response_serializer.UserShortDetailSerializer,
        'retrieve_response': response_serializer.UserDetailSerializer,
        'create_request': request_serializer.UserSerializer,
        'create_response': response_serializer.UserShortDetailSerializer,
        'update_request': request_serializer.UserSerializer,
        'update_response': response_serializer.UserDetailSerializer,
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserService()

    @api.swagger(
        tags=SWAGGER_TAGS,
        operation_id="User List",
    )
    def list(self, request):
        instances = self.service.get_objects()
        return self.paginator(instances, many=True)

    @api.swagger(
        tags=SWAGGER_TAGS,
        operation_id="User Retrieve",
    )
    def retrieve(self, request, pk):
        instance = self.service.get_by_id(pk)
        return self.get_response_serializer(instance).data

    @api.swagger(
        tags=SWAGGER_TAGS,
        operation_id="User Create",
    )
    @transaction.atomic
    def create(self, request):
        serializer = self.get_request_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return self.get_response_serializer(instance).data

    @api.swagger(
        tags=SWAGGER_TAGS,
        operation_id="User Update",
    )
    @transaction.atomic
    def update(self, request, pk):
        instance = self.service.get_by_id(pk)
        serializer = self.get_request_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance_updated = serializer.save()
        return self.get_response_serializer(instance_updated).data

    @api.swagger(
        tags=SWAGGER_TAGS,
        operation_id="User Destroy",
    )
    @transaction.atomic
    def destroy(self, request, pk):
        self.service.delete_by_id(pk)
