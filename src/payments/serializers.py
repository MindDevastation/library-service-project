from rest_framework import serializers

from payments.models import Payment, StripePayment, PayPalPayment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class StripePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripePayment
        fields = "__all__"
        read_only_fields = ("id", "status", "payment_intent_id")

    def validate(self, data):
        if data["amount"] <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return data

    def create(self, validated_data):
        payment = StripePayment.objects.create(**validated_data)
        payment.create_payment_intent()
        return payment


class StripePaymentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripePayment
        fields = ("status",)


class PayPalPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayPalPayment
        fields = "__all__"
        read_only_fields = [
            "id",
            "status",
            "paypal_order_id",
            "payer_id",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        if data["amount"] <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return data

    def create(self, validated_data):
        payment = PayPalPayment.objects.create(**validated_data)
        approval_url = payment.create_order()
        return payment, approval_url
