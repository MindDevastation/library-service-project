import paypalrestsdk
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import StripePayment, PayPalPayment
from payments.serializers import (
    StripePaymentSerializer,
    StripePaymentStatusUpdateSerializer,
    PayPalPaymentSerializer,
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
            "amount": payment.amount,
            "currency": payment.currency,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class CreatePayPalPaymentView(APIView):
    serializer_class = PayPalPaymentSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            payment, approval_url = serializer.save()
            return Response(
                {
                    "message": "Payment created successfully!",
                    "payment_id": payment.payment_id,
                    "paypal_order_id": payment.paypal_order_id,
                    "approval_url": approval_url,
                    "amount": payment.amount,
                    "currency": payment.currency,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )


class PayPalPaymentSuccessView(APIView):
    def get(self, request):
        token = request.GET.get("token")
        payer_id = request.GET.get("PayerID")

        if token and payer_id:
            try:
                paypalrestsdk.configure(
                    {
                        "mode": settings.PAYPAL_MODE,
                        "client_id": settings.PAYPAL_CLIENT_ID,
                        "client_secret": settings.PAYPAL_CLIENT_SECRET,
                    }
                )

                paypal_payment = PayPalPayment.objects.get(paypal_order_id=token)
                paypal_payment.payer_id = payer_id

                order = paypalrestsdk.Order.find(token)

                if order:
                    capture = order.capture()
                    if capture:
                        paypal_payment.status = PayPalPayment.Status.PAID
                        paypal_payment.save()
                        return Response(
                            {"status": "Payment completed successfully!"},
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {"error": "Payment capture failed."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    return Response(
                        {"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND
                    )

            except ObjectDoesNotExist:
                return Response(
                    {"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND
                )
        return Response(
            {"error": "Missing payment or payer ID"}, status=status.HTTP_400_BAD_REQUEST
        )


class PayPalPaymentCancelView(APIView):
    def get(self, request):
        return Response({"status": "Payment was canceled"}, status=status.HTTP_200_OK)
