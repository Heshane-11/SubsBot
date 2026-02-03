import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(plan, chat_id):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": f"{plan.period} Subscription",
                },
                "unit_amount": plan.price * 100,  # cents
            },
            "quantity": 1,
        }],
        metadata={
            "chat_id": chat_id,
            "plan_id": plan.id,
        },
        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
    )
    return session.url
