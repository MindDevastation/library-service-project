from rest_framework import serializers

from payments.models import Payment, StripePayment


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
        fields = ("status", )
