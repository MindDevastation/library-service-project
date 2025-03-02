from django.urls import path, include
from rest_framework import routers

from payments.views import (
    PaymentViewSet,
    StripePaymentViewSet,
    PayPalPaymentViewSet,
    PayPalPaymentSuccessView,
    PayPalPaymentCancelView,
)

app_name = "payments"

router = routers.DefaultRouter()
router.register("payments", PaymentViewSet, basename="payments")
router.register("stripe", StripePaymentViewSet, basename="stripe")
router.register("paypal", PayPalPaymentViewSet, basename="paypal")


urlpatterns = [
    path("", include(router.urls)),
    path("paypal/success/", PayPalPaymentSuccessView.as_view(), name="paypal-success"),
    path("paypal/cancel/", PayPalPaymentCancelView.as_view(), name="paypal-cancel"),
]
