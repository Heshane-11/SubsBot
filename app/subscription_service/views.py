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
def stripe_webhook(request):
    payload = request.body
    sig = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        print("❌ SIGNATURE FAILED:", str(e))
        return HttpResponse(status=400)

    print("🔥 STRIPE WEBHOOK HIT 🔥", event["type"])

    return HttpResponse(status=200)