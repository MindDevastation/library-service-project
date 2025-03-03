from rest_framework.permissions import BasePermission
from payments.models import Payment


class HasNoPendingPayments(BasePermission):
    message = "You have pending payments. You cannot create a new booking until they are paid."

    def has_permission(self, request, view):
        if request.method == "POST":
            user = request.user
            if not user or not user.is_authenticated:
                return False
            return not Payment.objects.filter(
                borrowing__user=user, status="PENDING"
            ).exists()
        return True


class IsBorrowingOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user == obj.user
