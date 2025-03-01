from rest_framework import viewsets
from rest_framework import mixins

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingDetailSerializer, BorrowingListSerializer


class BorrowingViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingListSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingListSerializer
