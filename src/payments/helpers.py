from decimal import Decimal
from payments.models import StripePayment, PayPalPayment


def create_stripe_payment(borrowing, amount, currency, payment_type):
    """
    Creates a Stripe payment instance and returns the payment and checkout session.
    """
    payment = StripePayment(
        borrowing=borrowing, amount=amount, currency=currency, type=payment_type
    )
    session = payment.create_checkout_session()
    return payment, session


def create_paypal_payment(borrowing, amount, currency, payment_type):
    """
    Creates a PayPal payment instance and returns the payment and approval URL.
    """
    payment = PayPalPayment(
        borrowing=borrowing, amount=amount, currency=currency, type=payment_type
    )
    approval_url = payment.create_order()
    return payment, approval_url


def calculate_payment(borrowing):
    """
    Calculates the total amount to be paid and determines the payment type
    based on the borrowing record.
    """
    daily_fee = borrowing.book.daily_fee
    day_pass = (borrowing.actual_return_date - borrowing.borrow_date).days
    if day_pass == 0:
        day_pass = 1

    money_to_pay = daily_fee * Decimal(day_pass)
    fine_multiplier = Decimal("2")
    days_overdue = (borrowing.actual_return_date - borrowing.expected_return_date).days

    if days_overdue > 0:
        fine_amount = Decimal(days_overdue) * daily_fee * fine_multiplier
        money_to_pay += fine_amount
        payment_type = "FINE"
    else:
        payment_type = "PAYMENT"

    return money_to_pay, payment_type


def process_payment(borrowing, money_to_pay, currency, payment_type, provider):
    """
    Processes the payment based on the specified provider and returns the URL for payment.
    """
    if provider == "stripe":
        _, session = create_stripe_payment(
            borrowing, money_to_pay, currency, payment_type
        )
        return session.url
    elif provider == "paypal":
        _, approval_url = create_paypal_payment(
            borrowing, money_to_pay, currency, payment_type
        )
        return approval_url
    else:
        raise ValueError("Unsupported payment provider")
