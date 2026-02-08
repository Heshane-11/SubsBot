import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from subscription_service.models import Plan, Subscription, TelegramUser
from subscription_service.utils import TelegramMessageSender

# ✅ REQUIRED
stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        print("❌ Webhook verification failed:", e)
        return HttpResponse(status=400)

    print("🔥 STRIPE WEBHOOK HIT 🔥")
    print("📦 EVENT TYPE:", event["type"])

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        metadata = session.get("metadata", {})
        chat_id = metadata.get("chat_id")
        plan_id = metadata.get("plan_id")
        payment_id = session.get("payment_intent")

        if not chat_id or not plan_id:
            print("❌ Missing metadata")
            return HttpResponse(status=200)

        user, _ = TelegramUser.objects.get_or_create(
            chat_id=int(chat_id),
            defaults={"telegram_username": f"user_{chat_id}"}
        )

        plan = Plan.objects.get(id=int(plan_id))

        Subscription.objects.update_or_create(
            customer=user,
            defaults={
                "plan": plan,
                "payment_id": payment_id,
            },
        )

        print("✅ Subscription saved")

        try:
            user.add_to_private_group()
        except Exception as e:
            print("⚠️ Group add failed:", e)

        TelegramMessageSender.send_message_to_chat(
            chat_id=int(chat_id),
            message="🎉 Payment verified!\n✅ Subscription ACTIVE."
        )

    return HttpResponse(status=200)
