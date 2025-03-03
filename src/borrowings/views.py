from decimal import Decimal

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.serializers import Serializer

# from borrowings.permissions import IsBorrowingOwnerOrAdmin
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
    PaymentChoiceSerializer,
)
from payments.helpers import create_stripe_payment, create_paypal_payment


class BorrowingViewSet(viewsets.ModelViewSet):
    serializer_class = BorrowingListSerializer
    queryset = Borrowing.objects.select_related("user", "book").prefetch_related(
        "book__authors"
    )
    # permission_classes = [IsBorrowingOwnerOrAdmin]

    http_method_names = ["get", "post"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "return_book":
            return PaymentChoiceSerializer
        return BorrowingListSerializer

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if is_active:
            if is_active.lower() == "true":
                queryset = queryset.filter(
                    status__in=[Borrowing.Status.PENDING, Borrowing.Status.OVERDUE]
                )
            if is_active.lower() == "false":
                queryset = queryset.filter(status__in=[Borrowing.Status.RETURNED])

        if user_id and user_id.isdigit():
            if user.is_superuser or user_id == str(user.id):
                queryset = queryset.filter(user_id=user_id)

        if not user.is_superuser:
            queryset = queryset.filter(user=user)

        return queryset

    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        with transaction.atomic():
            borrowing = self.get_object()

            if borrowing.status == Borrowing.Status.RETURNED:
                return Response(
                    {"message": "Borrowing is already returned"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            borrowing.status = Borrowing.Status.RETURNED
            borrowing.save()
            book = borrowing.book
            book.inventory += 1
            book.save()

            provider = serializer.validated_data["provider"]
            currency = serializer.validated_data["currency"]
            daily_fee = borrowing.book.daily_fee
            day_pass = (borrowing.actual_return_date - borrowing.borrow_date).days
            if day_pass == 0:
                day_pass += 1

            money_to_pay = daily_fee * Decimal(day_pass)
            payment_type = "PAYMENT"
            fine_multiplier = Decimal("2")
            days_of_overdue = Decimal(
                (borrowing.actual_return_date - borrowing.expected_return_date).days
            )
            fine_amount = days_of_overdue * daily_fee * fine_multiplier

            if borrowing.actual_return_date > borrowing.expected_return_date:
                money_to_pay += fine_amount
                payment_type = "FINE"

            if provider == "stripe":
                stripe_payment, session = create_stripe_payment(
                    borrowing, money_to_pay, currency, payment_type
                )
                return Response(
                    {
                        "message": "Borrowing returned successfully",
                        "go_to_pay": session.url,
                    },
                    status=status.HTTP_200_OK,
                )

            elif provider == "paypal":
                paypal_payment, approval_url = create_paypal_payment(
                    borrowing, money_to_pay, currency, payment_type
                )
                return Response(
                    {
                        "message": "Borrowing returned successfully",
                        "go_to_pay": approval_url,
                    },
                    status=status.HTTP_200_OK,
                )
