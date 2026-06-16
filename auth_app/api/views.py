from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView, Response

from auth_app.api.serializers import LoginSerializer, RegistrationSerializer

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.create(user=user)

        return Response(
            {
                "token": token.key,
                "fullname": self._get_fullname(user),
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_201_CREATED,
        )

    def _get_fullname(self, user):
        return f"{user.first_name} {user.last_name}".strip()
    
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "fullname": self._get_fullname(user),
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_200_OK,
        )

    def _get_fullname(self, user):
        return f"{user.first_name} {user.last_name}".strip()
