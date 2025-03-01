from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from payments.models import StripePayment
from payments.serializers import (
    StripePaymentSerializer,
    StripePaymentStatusUpdateSerializer,
)


class PaymentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    def list(self, request, *args, **kwargs):
        stripe_payments = StripePayment.objects.all()
        stripe_serializer = StripePaymentSerializer(stripe_payments, many=True)

        return Response(
            {
                "stripe_payments": stripe_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class StripePaymentViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    queryset = StripePayment.objects.all()

    def get_serializer_class(self):
        if self.action == "partial_update":
            return StripePaymentStatusUpdateSerializer
        return StripePaymentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        response_data = {
            "message": "Payment created successfully!",
            "payment_id": payment.id,
            "payment_intent_id": payment.payment_intent_id,
            "amount": payment.money_to_pay,
            "currency": payment.currency,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
