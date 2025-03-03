from django.contrib import admin

from payments.models import StripePayment, PayPalPayment

admin.site.register(StripePayment)
admin.site.register(PayPalPayment)
