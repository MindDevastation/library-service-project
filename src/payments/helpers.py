from payments.models import StripePayment, PayPalPayment


def create_stripe_payment(borrowing, amount, currency, payment_type):
    payment = StripePayment(borrowing=borrowing, amount=amount, currency=currency, type=payment_type)
    session = payment.create_checkout_session()
    return payment, session


def create_paypal_payment(borrowing, amount, currency, payment_type):
    payment = PayPalPayment(borrowing=borrowing, amount=amount, currency=currency, type=payment_type)
    approval_url = payment.create_order()
    return payment, approval_url
