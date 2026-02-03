from django.contrib import admin
from .models import TelegramUser, Plan, Subscription


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("chat_id", "telegram_username", "at_private_group", "is_staff")
    search_fields = ("telegram_username",)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("period", "price")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "plan",
        "start_date",
        "end_date",
    )
