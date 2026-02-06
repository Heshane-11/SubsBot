import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(plan, chat_id):
    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"{plan.period} subscription",
                    },
                    "unit_amount": int(plan.price * 100),
                },
                "quantity": 1,
            }
        ],
        success_url="https://t.me/hesahne_subs_bot?start=payment_success",
        cancel_url="https://t.me/hesahne_subs_bot?start=payment_cancelled",

        # 🔥 THIS IS THE KEY FIX
        metadata={
            "chat_id": str(chat_id),
            "plan_id": str(plan.id),
        },
    )

    return session.url
