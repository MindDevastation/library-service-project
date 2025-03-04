from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiRequest, OpenApiExample
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (AllowAny,)

    def get_object(self):
        return self.request.user


@extend_schema(
    request={
        "application/json": {
            "example": {"email": "user@example.com", "password": "securepassword123"}
        }
    },
    responses={
        200: OpenApiExample(
            name="Successful login",
            value={"detail": "Login successful"},
            response_only=True,
            status_codes=["200"],
        ),
        400: OpenApiExample(
            name="Missing email or password",
            value={"detail": "Email and password are required"},
            response_only=True,
            status_codes=["400"],
        ),
        401: OpenApiExample(
            name="Invalid credentials",
            value={"detail": "Invalid credentials"},
            response_only=True,
            status_codes=["401"],
        ),
    },
    summary="User authentication in Telegram bot",
    description="Allows users to authenticate in the system by providing an email and password.",
)
@api_view(["POST"])
def login_telegram_checkout(request):
    """
    User authentication using email and password.

    Parameters:
    - `email` (string, required) — User's email.
    - `password` (string, required) — User's password.

    Responses:
    - **200 OK**: Successful authentication.
    - **400 Bad Request**: If email or password is missing.
    - **401 Unauthorized**: If email or password is incorrect.
    """
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"detail": "Email and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=email, password=password)

    if user is not None:
        return Response({"detail": "Login successful"}, status=status.HTTP_200_OK)
    else:
        return Response(
            {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )
