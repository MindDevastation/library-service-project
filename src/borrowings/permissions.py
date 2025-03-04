from rest_framework.permissions import BasePermission, SAFE_METHODS
from payments.models import PayPalPayment, StripePayment


class HasNoPendingPayments(BasePermission):
    message = "You have pending payments. You cannot create a new booking until they are paid."

    def has_permission(self, request, view):
        if request.method == "POST":
            user = request.user
            if not user or not user.is_authenticated:
                return False
            return not PayPalPayment.objects.filter(
                borrowing__user=user, status="PENDING"
            ).exists() and not StripePayment.objects.filter(
                borrowing__user=user, status="PENDING"
            )
        return True


class IsSelfOrAdmin(BasePermission):
    message = "You must be the owner or an admin to perform this action."

    def has_object_permission(self, request, view, obj):
        return obj == request.user or (request.user and request.user.is_staff)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsBorrowingOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user == obj.user
