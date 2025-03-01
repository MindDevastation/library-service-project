from rest_framework import routers

from payments.views import PaymentViewSet, StripePaymentViewSet

app_name = "payments"

router = routers.DefaultRouter()
router.register("payments", PaymentViewSet, basename="payments")
router.register("stripe", StripePaymentViewSet)

urlpatterns = router.urls
