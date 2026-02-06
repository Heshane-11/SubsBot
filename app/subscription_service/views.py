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
    except Exception as e:
        print("❌ Webhook signature error:", e)
        return HttpResponse(status=400)

    print("🔥 STRIPE WEBHOOK HIT 🔥")
    print("📦 EVENT TYPE:", event["type"])

    if event["type"] == "checkout.session.completed":
        print("✅ CHECKOUT COMPLETED EVENT RECEIVED")

        session = event["data"]["object"]

        metadata = session.get("metadata", {})
        chat_id = metadata.get("chat_id")
        plan_id = metadata.get("plan_id")
        payment_id = session.get("payment_intent")

        if not chat_id or not plan_id:
            print("❌ Missing metadata in Stripe session")
            return HttpResponse(status=200)

        chat_id = int(chat_id)
        plan_id = int(plan_id)

        # 🔥 FIX: GET OR CREATE USER
        user, created = TelegramUser.objects.get_or_create(
            chat_id=chat_id,
            defaults={
                "telegram_username": f"user_{chat_id}"
            }
        )

        if created:
            print("🆕 TelegramUser created via webhook:", chat_id)

        plan = Plan.objects.get(id=plan_id)

        Subscription.objects.update_or_create(
            customer=user,
            defaults={
                "plan": plan,
                "payment_id": payment_id,
            },
        )

        print("✅ Subscription saved")

        # OPTIONAL: auto add to group
        try:
            user.add_to_private_group()
            print("✅ User added to private group")
        except Exception as e:
            print("⚠️ Group add failed:", e)

        TelegramMessageSender.send_message_to_chat(
            chat_id=chat_id,
            message="🎉 Payment verified successfully!\n✅ Your subscription is now ACTIVE."
        )

    return HttpResponse(status=200)
