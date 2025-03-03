from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.serializers import Serializer

from borrowings.schema import borrowings_schema_view
from borrowings.permissions import IsBorrowingOwnerOrAdmin, HasNoPendingPayments
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
)


@borrowings_schema_view
class BorrowingViewSet(viewsets.ModelViewSet):
    serializer_class = BorrowingListSerializer
    queryset = Borrowing.objects.select_related("user", "book").prefetch_related(
        "book__authors"
    )

    http_method_names = ["get", "post"]

    def get_permissions(self):
        permission_classes = [IsBorrowingOwnerOrAdmin()]

        if self.action == "create":
            permission_classes = [IsBorrowingOwnerOrAdmin(), HasNoPendingPayments()]

        return permission_classes

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "return_book":
            return Serializer
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

            borrowing.status = Borrowing.Status.RETURNED
            borrowing.save()
            book = borrowing.book
            book.inventory += 1
            book.save()

            return Response(
                {"message": "Borrowing returned successfully"},
                status=status.HTTP_200_OK,
            )
