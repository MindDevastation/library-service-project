from rest_framework import viewsets
from rest_framework import mixins

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = BorrowingListSerializer
    queryset = Borrowing.objects.select_related("user", "book").prefetch_related(
        "book__authors"
    )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingListSerializer

    def get_queryset(self):
        queryset = Borrowing.objects.select_related("user", "book").prefetch_related(
            "book__authors"
        )

        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if is_active:
            if is_active.lower() == "true":
                queryset = queryset.filter(
                    status__in=[Borrowing.Status.PENDING, Borrowing.Status.OVERDUE]
                )
            if is_active.lower() == "false":
                queryset = queryset.filter(status__in=[Borrowing.Status.RETURNED])

        if (
            user_id
            and self.request.user.is_superuser
            or user_id
            and user_id == str(self.request.user.id)
        ):
            if user_id.isdigit():
                queryset = queryset.filter(user_id=user_id)

        return queryset
