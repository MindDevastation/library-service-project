import paypalrestsdk
import stripe
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import StripePayment, PayPalPayment
from payments.serializers import (
    StripePaymentCreateSerializer,
    StripePaymentListSerializer,
    PayPalPaymentListSerializer,
    PayPalPaymentCreateSerializer,
)


class PaymentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    def list(self, request, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            stripe_payments = StripePayment.objects.filter(borrowing__user_id=user.id)
            paypal_payments = PayPalPayment.objects.filter(borrowing__user_id=user.id)
        else:
            stripe_payments = StripePayment.objects.all()
            paypal_payments = PayPalPayment.objects.all()

        stripe_serializer = StripePaymentListSerializer(stripe_payments, many=True)
        paypal_serializer = PayPalPaymentListSerializer(paypal_payments, many=True)

        return Response(
            {
                "stripe_payments": stripe_serializer.data,
                "paypal_payments": paypal_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class StripePaymentViewSet(viewsets.ModelViewSet):
    queryset = StripePayment.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset

        if not user.is_staff:
            queryset = StripePayment.objects.filter(borrowing__user_id=user.id)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return StripePaymentCreateSerializer
        return StripePaymentListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        response_data = {
            "message": "Payment created successfully!",
            "payment_id": payment.id,
            "session_id": payment.session_id,
            "session_url": payment.session_url,
            "amount": payment.amount,
            "currency": payment.currency,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class PayPalPaymentViewSet(viewsets.ModelViewSet):
    queryset = PayPalPayment.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset

        if not user.is_staff:
            queryset = PayPalPayment.objects.filter(borrowing__user_id=user.id)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return PayPalPaymentCreateSerializer
        return PayPalPaymentListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            approval_url = payment.create_order()
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


class StripePaymentSuccessView(APIView):
    def get(self, request):
        session_id = request.query_params.get("session_id")
        if session_id:
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                payment = StripePayment.objects.get(session_id=session_id)
                payment.status = StripePayment.Status.PAID
                payment.save()
                return Response(
                    {"status": "Payment completed successfully!"},
                    status=status.HTTP_200_OK,
                )
            except ObjectDoesNotExist:
                return Response(
                    {"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND
                )
            except stripe.error.StripeError as error:
                return Response(
                    {"error": f"Stripe error occurred: {error.user_message}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            {"error": "Missing session ID"}, status=status.HTTP_400_BAD_REQUEST
        )


class StripePaymentCancelView(APIView):
    def get(self, request):
        return Response({"status": "Payment was canceled"}, status=status.HTTP_200_OK)


class PayPalPaymentSuccessView(APIView):
    def get(self, request):
        token = request.GET.get("paymentId")
        payer_id = request.GET.get("PayerID")

        if token and payer_id:
            try:
                paypalrestsdk.configure(
                    {
                        "mode": settings.PAYPAL_MODE,
                        "client_id": settings.PAYPAL_CLIENT_ID,
                        "client_secret": settings.PAYPAL_SECRET,
                    }
                )

                paypal_payment = PayPalPayment.objects.get(paypal_order_id=token)
                paypal_payment.payer_id = payer_id

                payment = paypalrestsdk.Payment.find(token)

                if payment:
                    if payment.execute({"payer_id": payer_id}):
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
