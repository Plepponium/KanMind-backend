from rest_framework import serializers, status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView, Response

from auth_app.api.serializers import EmailCheckResponseSerializer, LoginSerializer, RegistrationSerializer


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


class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")

        if not email:
            return Response(
                {"detail": "Email query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email_field = serializers.EmailField()

        try:
            email = email_field.run_validation(email)
        except serializers.ValidationError:
            return Response(
                {"detail": "Invalid email format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "User with this email was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EmailCheckResponseSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
