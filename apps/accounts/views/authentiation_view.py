from utils.views import APIGenericView
from utils.decorators import api

from ..serializers import serializer

from ..services.user_service import UserService


SWAGGER_TAGS = ["Accounts: Authentication"]


class AuthenticationAPIGenericView(APIGenericView):
    authentication_action_classes = {}
    permission_action_classes = {}
    authentication_classes = ()
    permission_classes = ()
    
    action_serializers = {
        'login_request': serializer.AuthenticationSerializer
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserService()

    @api.post()
    @api.swagger(
        tags=SWAGGER_TAGS,
        operation_id="Auth Login",
    )
    def login(self, request):
        auth = self.get_request_serializer(data=request.data, context={'request': request})
        auth.is_valid(raise_exception=True)
        return auth.validated_data