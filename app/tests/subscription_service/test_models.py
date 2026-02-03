from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone

from subscription_service.models import Plan, Subscription, TelegramUser


@pytest.mark.django_db
def test_telegram_user_model():
    telegram_user = TelegramUser(
        chat_id=2141241241245,
        telegram_username="@TestUser",
        first_name="Conor",
        last_name="McGregor",
        at_private_group=False,
    )
    assert telegram_user.chat_id == 2141241241245
    assert telegram_user.telegram_username == "@TestUser"
    assert telegram_user.first_name == "Conor"
    assert telegram_user.last_name == "McGregor"
    assert telegram_user.at_private_group is False
    assert telegram_user.is_staff is False
    assert telegram_user.date_joined.date() == timezone.now().date()


@pytest.mark.django_db
def test_telegram_user_str_method():
    user = TelegramUser.objects.create(
        chat_id=32896732649,
        telegram_username="@user1",
    )
    assert str(user) == "@user1"


@pytest.mark.django_db
def test_create_plan():
    plan = Plan.objects.create(period="1 month", price=100)
    assert Plan.objects.count() == 1
    assert plan.period == "1 month"
    assert plan.price == 100


@pytest.mark.django_db
def test_unique_period():
    Plan.objects.create(period="1 month", price=100)
    with pytest.raises(Exception):
        Plan.objects.create(period="1 month", price=100)


@pytest.mark.django_db
def test_plan_string_representation():
    plan = Plan.objects.create(period="1 month", price=100)
    assert str(plan) == "1 month Plan - $100"


@pytest.mark.django_db
def test_subscription_model():
    plan = Plan.objects.create(period="1 month", price=100)
    user = TelegramUser.objects.create(
        chat_id=123456789,
        telegram_username="@test_user",
    )

    subscription = Subscription.objects.create(
        customer=user,
        plan=plan,
        payment_id="pi_test_123",
        start_date=timezone.now(),
    )

    saved_subscription = Subscription.objects.get(payment_id="pi_test_123")

    expected_end_date = subscription.start_date + timedelta(days=30)
    assert saved_subscription.end_date == expected_end_date


@pytest.mark.django_db
def test_subscription_save():
    plan = Plan.objects.create(period="1 month", price=100)
    user = TelegramUser.objects.create(
        chat_id=123456789,
        telegram_username="@test_user",
    )

    subscription = Subscription.objects.create(
        customer=user,
        plan=plan,
        payment_id="pi_test_save",
        start_date=timezone.now(),
    )

    assert subscription.pk is not None
    assert subscription.customer == user
    assert subscription.plan == plan
    assert subscription.payment_id == "pi_test_save"
    assert subscription.end_date is not None


@pytest.mark.django_db
def test_subscription_end_date_calculation():
    start_date = timezone.now()

    user = TelegramUser.objects.create(
        chat_id=111,
        telegram_username="@user",
    )

    plan_1_month = Plan.objects.create(period="1 month", price=29)
    sub_1 = Subscription.objects.create(
        customer=user,
        plan=plan_1_month,
        payment_id="pi_1",
        start_date=start_date,
    )
    assert sub_1.end_date == start_date + timedelta(days=30)

    plan_3 = Plan.objects.create(period="3 months", price=79)
    sub_3 = Subscription.objects.create(
        customer=user,
        plan=plan_3,
        payment_id="pi_3",
        start_date=start_date,
    )
    assert sub_3.end_date == start_date + timedelta(days=90)

    plan_6 = Plan.objects.create(period="6 months", price=149)
    sub_6 = Subscription.objects.create(
        customer=user,
        plan=plan_6,
        payment_id="pi_6",
        start_date=start_date,
    )
    assert sub_6.end_date == start_date + timedelta(days=180)

    plan_1y = Plan.objects.create(period="1 year", price=279)
    sub_1y = Subscription.objects.create(
        customer=user,
        plan=plan_1y,
        payment_id="pi_1y",
        start_date=start_date,
    )
    assert sub_1y.end_date == start_date + timedelta(days=365)


@pytest.mark.django_db
def test_unique_payment_id():
    plan = Plan.objects.create(period="1 month", price=100)
    user = TelegramUser.objects.create(
        chat_id=999,
        telegram_username="@unique_user",
    )

    Subscription.objects.create(
        customer=user,
        plan=plan,
        payment_id="pi_unique",
        start_date=timezone.now(),
    )

    with pytest.raises(Exception):
        Subscription.objects.create(
            customer=user,
            plan=plan,
            payment_id="pi_unique",
            start_date=timezone.now(),
        )


@pytest.mark.django_db
def test_negative_plan_price():
    with pytest.raises(IntegrityError):
        Plan.objects.create(period="1 month", price=-10)


@pytest.mark.django_db
def test_subscription_model_relationships():
    user = TelegramUser.objects.create(
        chat_id=777,
        telegram_username="@rel_user",
    )
    plan = Plan.objects.create(period="1 month", price=100)

    subscription = Subscription.objects.create(
        customer=user,
        plan=plan,
        payment_id="pi_rel",
        start_date=timezone.now(),
    )

    assert subscription.customer == user
    assert subscription.plan == plan
