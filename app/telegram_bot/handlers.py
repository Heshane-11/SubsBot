from django.utils import timezone
from subscription_service.models import Plan, Subscription, TelegramUser
from subscription_service.utils import TelegramMessageSender
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from subscription_service.stripe_service import create_checkout_session


def handle_start(chat_id, text=None):
    """
    /start is NEVER trusted for subscription logic.
    """

    if text and text.startswith("/start"):
        TelegramMessageSender.send_message_to_chat(
            chat_id=chat_id,
            message=(
                "👋 Welcome!\n\n"
                "Use /verify to check your subscription status.\n"
                "Or choose a plan below 👇"
            )
        )

    plans = Plan.objects.all()

    if not plans.exists():
        TelegramMessageSender.send_message_to_chat(
            chat_id=chat_id,
            message="⚠️ No subscription plans available right now."
        )
        return

    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{plan.period} — ${plan.price}",
                callback_data=f"PLAN_{plan.id}",
            )
        ]
        for plan in plans
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    TelegramMessageSender.send_message_to_chat(
        chat_id=chat_id,
        message="💳 Available subscription plans:",
        reply_markup=reply_markup,
    )


def handle_verify(chat_id):
    """
    /verify command
    """

    try:
        user = TelegramUser.objects.get(chat_id=chat_id)
    except TelegramUser.DoesNotExist:
        TelegramMessageSender.send_message_to_chat(
            chat_id=chat_id,
            message="⚠️ You have never purchased a subscription."
        )
        return

    try:
        subscription = Subscription.objects.get(customer=user)
    except Subscription.DoesNotExist:
        TelegramMessageSender.send_message_to_chat(
            chat_id=chat_id,
            message="⚠️ No active subscription found."
        )
        return

    now = timezone.now()

    if subscription.end_date >= now:
        TelegramMessageSender.send_message_to_chat(
            chat_id=chat_id,
            message=(
                "✅ Subscription ACTIVE\n\n"
                f"📦 Plan: {subscription.plan.period}\n"
                f"⏳ Valid till: {subscription.end_date.strftime('%d %b %Y, %H:%M')}\n\n"
                "You have full access 🎉"
            )
        )
    else:
        TelegramMessageSender.send_message_to_chat(
            chat_id=chat_id,
            message=(
                "❌ Subscription EXPIRED\n\n"
                f"📦 Plan: {subscription.plan.period}\n"
                f"⏰ Expired on: {subscription.end_date.strftime('%d %b %Y, %H:%M')}\n\n"
                "Please renew your subscription."
            )
        )


def handle_plan_selected(chat_id, plan_id):
    plan = Plan.objects.get(id=plan_id)
    checkout_url = create_checkout_session(plan, chat_id)

    message = (
        "✅ You selected:\n\n"
        f"📦 Plan: {plan.period}\n"
        f"💰 Price: ${plan.price}\n\n"
        "👉 Click below to pay securely:\n"
        f"{checkout_url}\n\n"
        "💳 Test card:\n"
        "4242 4242 4242 4242\n"
        "Any future expiry • Any CVC\n\n"
        "⏳ After payment, use /verify to confirm access."
    )

    TelegramMessageSender.send_message_to_chat(
        chat_id=chat_id,
        message=message,
    )
