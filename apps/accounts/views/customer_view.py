from utils.permissions import Authenticated
from utils.views import APIGenericView
from utils.decorators import api

from django.db import transaction

from ..serializers.customer import request_serializer, response_serializer

from ..services.customer_service import CustomerService

from helpers.token_helper import Token


SWAGGER_TAGS = ["Accounts: Customer"]


class CustomerAPIGenericView(APIGenericView):
    
    action_serializers = {
        'list_response': response_serializer.CustomerShortDetailSerializer,
        'retrieve_response': response_serializer.CustomerDetailSerializer,
        'create_request': request_serializer.CustomerSerializer,
        'create_response': response_serializer.CustomerShortDetailSerializer,
        'update_request': request_serializer.CustomerSerializer,
        'update_response': response_serializer.CustomerDetailSerializer,
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CustomerService()

    @api.swagger(
        tags=SWAGGER_TAGS,
        operation_id="Customer List",
    )
    def list(self, request):
        instances = self.service.get_objects()
        return self.paginator(instances, many=True)

    @api.swagger(
        tags=SWAGGER_TAGS,
        operation_id="Customer Retrieve",
    )
    def retrieve(self, request, pk):
        instance = self.service.get_by_id(pk)
        return self.get_response_serializer(instance).data

    @api.swagger(
        tags=SWAGGER_TAGS,
        operation_id="Customer Create",
    )
    @transaction.atomic
    def create(self, request):
        serializer = self.get_request_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return self.get_response_serializer(instance).data

    @api.swagger(
        tags=SWAGGER_TAGS,
        operation_id="Customer Update",
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
        operation_id="Customer Destroy",
    )
    @transaction.atomic
    def destroy(self, request, pk):
        self.service.delete_by_id(pk)
