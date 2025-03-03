from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.models import User
from borrowings.models import Borrowing
from payments.models import Payment



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "first_name", "last_name", "password", "is_staff")
        read_only_fields = ("is_staff",)
        required_fields = ("first_name", "last_name")
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "style": {"input_type": "password"},
                "label": _("Password"),
            }
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user

    def to_representation(self, instance):

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "date_joined",
        )
        read_only_fields = ("email", "is_staff", "date_joined")


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = "__all__"

    def validate(self, attrs):
        user = self.context["request"].user

        if Payment.objects.filter(borrowing__user=user, status="PENDING").exists():
            raise serializers.ValidationError(
                "You have pending payments. You cannot create a new booking until they are paid.."
            )
        return attrs
     
