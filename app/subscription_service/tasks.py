import os
from datetime import timedelta

import pytz
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from subscription_service.utils import TelegramMessageSender
from .models import Subscription, TelegramUser


MOSCOW_TZ = pytz.timezone("Europe/Moscow")


@shared_task
def delete_expired_subscriptions() -> None:
    admins_of_group = TelegramUser.objects.filter(is_staff=True)

    now = timezone.now()

    expired_subscriptions = (
        Subscription.objects
        .select_related("customer", "plan")
        .filter(end_date__lt=now)
    )

    for subscription in expired_subscriptions:
        customer = subscription.customer

        subscription_start_date = subscription.start_date.astimezone(
            MOSCOW_TZ
        ).strftime("%d/%m/%Y %H:%M:%S")

        subscription_end_date = subscription.end_date.astimezone(
            MOSCOW_TZ
        ).strftime("%d/%m/%Y %H:%M:%S")

        for admin in admins_of_group:
            try:
                message = TelegramMessageSender.create_message_about_delete_user(
                    admin_of_group=admin.telegram_username,
                    telegram_username=customer.telegram_username,
                    subscription_start_date=subscription_start_date,
                    subscription_end_date=subscription_end_date,
                    subscription_plan=subscription.plan.period,
                    subscription_price=subscription.plan.price,
                    payment_id=subscription.payment_id,
                )

                response = TelegramMessageSender.send_message_to_chat(
                    chat_id=admin.chat_id,
                    message=message,
                )

                if response.status_code == 200:
                    subscription.delete()
                    customer.delete_from_private_group()

            except Exception as e:
                print(
                    f"[DELETE TASK ERROR] User @{customer.telegram_username}: {str(e)}"
                )


def _get_subscriptions_expiring_in_days(days: int):
    now = timezone.now()
    start = now + timedelta(days=days)
    end = start + timedelta(days=1)

    return (
        Subscription.objects
        .select_related("customer", "plan")
        .filter(end_date__gte=start, end_date__lt=end)
    )


@shared_task
def notify_about_expiring_subscriptions_1_day() -> None:
    _notify(days=1, syntax_word="день", image="1-day.jpg")


@shared_task
def notify_about_expiring_subscriptions_3_days() -> None:
    _notify(days=3, syntax_word="дня", image="3-days.jpg")


@shared_task
def notify_about_expiring_subscriptions_7_days() -> None:
    _notify(days=7, syntax_word="дней", image="7-days.jpg")


def _notify(days: int, syntax_word: str, image: str) -> None:
    admins_of_group = TelegramUser.objects.filter(is_staff=True)

    subscriptions = _get_subscriptions_expiring_in_days(days)

    for subscription in subscriptions:
        customer = subscription.customer

        subscription_start_date = subscription.start_date.astimezone(
            MOSCOW_TZ
        ).strftime("%d/%m/%Y %H:%M:%S")

        subscription_end_date = subscription.end_date.astimezone(
            MOSCOW_TZ
        ).strftime("%d/%m/%Y %H:%M:%S")

        try:
            reminder_message = TelegramMessageSender.create_message_about_reminder(
                telegram_username=customer.telegram_username,
                day=days,
                syntax_word=syntax_word,
            )

            subscription_data_message = (
                TelegramMessageSender.create_message_with_subscription_data(
                    telegram_username=customer.telegram_username,
                    subscription_plan=subscription.plan.period,
                    subscription_start_date=subscription_start_date,
                    subscription_end_date=subscription_end_date,
                    subscription_price=subscription.plan.price,
                )
            )

            photo_response = TelegramMessageSender.send_message_with_photo_to_chat(
                chat_id=customer.chat_id,
                message=reminder_message,
                photo_path=os.path.join(settings.MEDIA_ROOT, image),
            )

            text_response = TelegramMessageSender.send_message_to_chat(
                chat_id=customer.chat_id,
                message=subscription_data_message,
            )

            if photo_response.status_code == 200 and text_response.status_code == 200:
                for admin in admins_of_group:
                    TelegramMessageSender.send_message_to_chat(
                        chat_id=admin.chat_id,
                        message=(
                            f"Hi, {admin.telegram_username}!\n\n"
                            f"Reminder ({days} days) sent to "
                            f"@{customer.telegram_username}"
                        ),
                    )

        except Exception as e:
            print(
                f"[REMINDER {days}D ERROR] User @{customer.telegram_username}: {str(e)}"
            )
