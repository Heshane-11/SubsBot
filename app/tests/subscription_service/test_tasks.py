from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from subscription_service.models import Plan, Subscription, TelegramUser
from subscription_service.tasks import (
    delete_expired_subscriptions,
    notify_about_expiring_subscriptions_1_day,
    notify_about_expiring_subscriptions_3_days,
    notify_about_expiring_subscriptions_7_days,
)


@pytest.mark.django_db
@patch("subscription_service.tasks.TelegramMessageSender")
def test_delete_expired_subscriptions(mock_sender):
    admin = TelegramUser.objects.create(
        chat_id=1,
        telegram_username="admin",
        is_staff=True,
        at_private_group=True,
    )

    plan = Plan.objects.create(period="1 month", price=100)

    Subscription.objects.create(
        customer=admin,
        plan=plan,
        payment_id="pi_expired_test",
        start_date=timezone.now() - timedelta(days=40),
    )

    mock_sender.create_message_about_delete_user.return_value = "msg"
    mock_sender.send_message_to_chat.return_value.status_code = 200

    delete_expired_subscriptions()

    assert not Subscription.objects.filter(customer=admin).exists()
    admin.refresh_from_db()
    assert admin.at_private_group is False


@pytest.mark.django_db
def test_notify_about_expiring_subscriptions_1_day():
    user = TelegramUser.objects.create(
        telegram_username="expiring_user",
        chat_id=100,
        at_private_group=True,
    )

    plan = Plan.objects.create(period="1 month", price=100)

    Subscription.objects.create(
        customer=user,
        plan=plan,
        payment_id="pi_1_day",
        start_date=timezone.now() - timedelta(days=29),
    )

    notify_about_expiring_subscriptions_1_day()

    subscription = Subscription.objects.get(customer=user)
    assert subscription.customer.telegram_username == "expiring_user"


@pytest.mark.django_db
def test_notify_about_expiring_subscriptions_3_days():
    user = TelegramUser.objects.create(
        telegram_username="expiring_user_3",
        chat_id=101,
        at_private_group=True,
    )

    plan = Plan.objects.create(period="1 month", price=100)

    Subscription.objects.create(
        customer=user,
        plan=plan,
        payment_id="pi_3_day",
        start_date=timezone.now() - timedelta(days=27),
    )

    notify_about_expiring_subscriptions_3_days()

    subscription = Subscription.objects.get(customer=user)
    assert subscription.customer.telegram_username == "expiring_user_3"


@pytest.mark.django_db
def test_notify_about_expiring_subscriptions_7_days():
    user = TelegramUser.objects.create(
        telegram_username="expiring_user_7",
        chat_id=102,
        at_private_group=True,
    )

    plan = Plan.objects.create(period="1 month", price=100)

    Subscription.objects.create(
        customer=user,
        plan=plan,
        payment_id="pi_7_day",
        start_date=timezone.now() - timedelta(days=23),
    )

    notify_about_expiring_subscriptions_7_days()

    subscription = Subscription.objects.get(customer=user)
    assert subscription.customer.telegram_username == "expiring_user_7"
