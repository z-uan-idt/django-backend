from rest_framework_simplejwt.authentication import JWTAuthentication


class MutilAuthentication(JWTAuthentication):

    def authenticate(self, request):
        authenticated = super().authenticate(request)
        return authenticated
