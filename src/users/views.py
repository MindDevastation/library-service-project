from rest_framework import generics
from rest_framework.permissions import AllowAny
from users.models import User
from users.serializers import UserRegistrationSerializer, UserProfileSerializer
from rest_framework.permissions import BasePermission


class IsBorrowingOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user == obj.user


class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        return self.request.user
