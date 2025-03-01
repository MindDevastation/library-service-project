from django.urls import path, include
from rest_framework import routers

from payments.views import (
    PaymentViewSet,
    StripePaymentViewSet,
    CreatePayPalPaymentView,
    PayPalPaymentSuccessView,
    PayPalPaymentCancelView,
)

app_name = "payments"

router = routers.DefaultRouter()
router.register("payments", PaymentViewSet, basename="payments")
router.register("stripe", StripePaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("paypal-create/", CreatePayPalPaymentView.as_view(), name="paypal-create"),
    path("paypal/success/", PayPalPaymentSuccessView.as_view(), name="paypal-success"),
    path("paypal/cancel/", PayPalPaymentCancelView.as_view(), name="paypal-cancel"),
]
