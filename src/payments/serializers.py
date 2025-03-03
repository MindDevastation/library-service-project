from rest_framework import serializers

from payments.models import StripePayment, PayPalPayment


class StripePaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripePayment
        fields = "__all__"


class StripePaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripePayment
        fields = ("type", "currency", "amount", "borrowing")

    def validate(self, data):
        if data["amount"] <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return data

    def create(self, validated_data):
        payment = StripePayment.objects.create(**validated_data)
        payment.create_checkout_session()
        return payment


class PayPalPaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayPalPayment
        fields = "__all__"


class PayPalPaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayPalPayment
        fields = ("type", "currency", "amount", "borrowing")

    def validate(self, data):
        if data["amount"] <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return data

    def create(self, validated_data):
        payment = PayPalPayment.objects.create(**validated_data)
        return payment
