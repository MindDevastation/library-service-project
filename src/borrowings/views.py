from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from borrowings.schema import borrowings_schema_view
from borrowings.permissions import IsBorrowingOwnerOrAdmin, HasNoPendingPayments
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
    PaymentChoiceSerializer,
)
from borrowings.helpers import complete_return
from payments.helpers import calculate_payment, process_payment


@borrowings_schema_view
class BorrowingViewSet(viewsets.ModelViewSet):
    serializer_class = BorrowingListSerializer
    queryset = Borrowing.objects.select_related("user", "book").prefetch_related(
        "book__authors"
    )

    http_method_names = ["get", "post"]

    def get_permissions(self):
        if self.action == "create":
            return [IsBorrowingOwnerOrAdmin(), HasNoPendingPayments()]
        return [IsBorrowingOwnerOrAdmin()]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "return_book":
            return PaymentChoiceSerializer
        return BorrowingListSerializer

    def get_queryset(self):
        """
        Retrieve a filtered queryset of borrowing records
        based on query parameters and user permissions.
        """
        queryset = self.queryset
        user = self.request.user
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        filter_kwargs = {}

        if is_active:
            active_value = is_active.lower()
            if active_value == "true":
                filter_kwargs["status__in"] = [
                    Borrowing.Status.PENDING,
                    Borrowing.Status.OVERDUE,
                ]
            elif active_value == "false":
                filter_kwargs["status__in"] = [Borrowing.Status.RETURNED]

        if user.is_superuser:
            if user_id and user_id.isdigit():
                filter_kwargs["user_id"] = user_id
        else:
            filter_kwargs["user"] = user

        return queryset.filter(**filter_kwargs)

    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        """
        This action updates the borrowing record by setting its status to 'RETURNED'.
        If the borrowing is already returned, it returns a 400 Bad Request response with an appropriate message.
        Otherwise, it increments the associated book's inventory by one and saves both the borrowing and the book,
        then returns a success response.
        """
        with transaction.atomic():
            borrowing = self.get_object()

            if borrowing.status == borrowing.Status.RETURNED:
                return Response(
                    {"message": "Borrowing is already returned"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            complete_return(borrowing)

            provider = serializer.validated_data["provider"]
            currency = serializer.validated_data["currency"]

            money_to_pay, payment_type = calculate_payment(borrowing)
            go_to_pay = process_payment(
                borrowing, money_to_pay, currency, payment_type, provider
            )

            return Response(
                {
                    "message": "Borrowing returned successfully",
                    "go_to_pay": go_to_pay,
                },
                status=status.HTTP_200_OK,
            )
