import os
import redis
from subscription_service.models import TelegramUser, Plan, Subscription
from subscription_service.utils import TelegramMessageSender
from django.utils import timezone
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from subscription_service.stripe_service import create_checkout_session


def handle_start(chat_id, text=None):
    if text == "/start payment_success":
        TelegramMessageSender.send_message_to_chat(
            chat_id,
            "🎉 Payment successful!\n✅ Subscription activated.\n\nWelcome aboard 🚀"
        )
        return

    if text == "/start payment_cancelled":
        TelegramMessageSender.send_message_to_chat(
            chat_id,
            "❌ Payment cancelled.\nYou can try again using /start"
        )
        return

    # existing plan logic


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
        "⏳ Subscription activates automatically after payment."
    )

    TelegramMessageSender.send_message_to_chat(
        chat_id=chat_id,
        message=message
    )
