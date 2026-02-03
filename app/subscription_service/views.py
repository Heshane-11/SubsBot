import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from subscription_service.models import Plan, Subscription, TelegramUser
from subscription_service.utils import TelegramMessageSender


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        chat_id = int(session["metadata"]["chat_id"])
        plan_id = int(session["metadata"]["plan_id"])
        payment_id = session["payment_intent"]

        user = TelegramUser.objects.get(chat_id=chat_id)
        plan = Plan.objects.get(id=plan_id)

        Subscription.objects.update_or_create(
            customer=user,
            defaults={
                "plan": plan,
                "payment_id": payment_id,
            },
        )

        user.add_to_private_group()

        TelegramMessageSender.send_message_to_chat(
            chat_id=chat_id,
            message="🎉 Payment successful!\n✅ Subscription activated."
        )

    return HttpResponse(status=200)
