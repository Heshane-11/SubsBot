from datetime import datetime, timedelta

import pytest
import pytz
from django.utils import timezone

from subscription_service.models import Plan, Subscription, TelegramUser
from subscription_service.serializers import (
    GetSubscriptionSerializer,
    PostSubscriptionSerializer,
    TelegramUserSerializer,
)


@pytest.mark.django_db
def test_valid_telegram_user_serializer():
    data = {
        "chat_id": 2141241241245,
        "telegram_username": "@TestUser",
        "first_name": "Conor",
        "last_name": "McGregor",
    }
    serializer = TelegramUserSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == data


@pytest.mark.django_db
def test_invalid_telegram_user_serializer():
    serializer = TelegramUserSerializer(data={"chat_id": 2141241241245})
    assert not serializer.is_valid()
    assert "telegram_username" in serializer.errors


@pytest.mark.django_db
def test_valid_post_subscription_serializer():
    user = TelegramUser.objects.create(
        chat_id=67890,
        telegram_username="@test_user",
    )
    plan = Plan.objects.create(period="1 month", price=100)

    data = {
        "customer": user.chat_id,
        "plan": plan.id,
        "payment_id": "pi_test_123",
    }

    serializer = PostSubscriptionSerializer(data=data)
    assert serializer.is_valid()
    subscription = serializer.save()

    assert Subscription.objects.filter(payment_id="pi_test_123").exists()
    assert subscription.customer == user
    assert subscription.plan == plan
    assert subscription.end_date == subscription.start_date + timedelta(days=30)


@pytest.mark.django_db
def test_invalid_post_subscription_serializer_missing_payment_id():
    user = TelegramUser.objects.create(
        chat_id=67890,
        telegram_username="@test_user",
    )
    plan = Plan.objects.create(period="1 month", price=100)

    serializer = PostSubscriptionSerializer(
        data={"customer": user.chat_id, "plan": plan.id}
    )

    assert not serializer.is_valid()
    assert "payment_id" in serializer.errors


@pytest.mark.django_db
def test_valid_get_subscription_serializer():
    user = TelegramUser.objects.create(
        chat_id=67890,
        telegram_username="test_user",
    )
    plan = Plan.objects.create(period="1 month", price=100)

    start_date = datetime(2024, 3, 1, 0, 0, tzinfo=pytz.UTC)
    subscription = Subscription.objects.create(
        customer=user,
        plan=plan,
        payment_id="pi_get_test",
        start_date=start_date,
    )

    serializer = GetSubscriptionSerializer(instance=subscription)

    expected_data = {
        "customer": "test_user",
        "plan": "1 month",
        "price": 100,
        "payment_id": "pi_get_test",
        "start_date": start_date.astimezone(
            pytz.timezone("Europe/Moscow")
        ).strftime("%d/%m/%Y %H:%M:%S"),
        "end_date": (start_date + timedelta(days=30)).astimezone(
            pytz.timezone("Europe/Moscow")
        ).strftime("%d/%m/%Y %H:%M:%S"),
    }

    assert serializer.data == expected_data


@pytest.mark.django_db
def test_invalid_get_subscription_serializer():
    serializer = GetSubscriptionSerializer(
        data={
            "plan": "1 month",
            "price": 100,
        }
    )

    assert not serializer.is_valid()
    assert "customer" in serializer.errors
