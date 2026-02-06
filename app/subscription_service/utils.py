import os
from typing import Union
import requests

from .models import TelegramUser


class TelegramMessageSender:
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

    # =========================
    # TELEGRAM SENDERS
    # =========================

    @classmethod
    def send_message_to_chat(
        cls,
        message: str,
        chat_id: Union[int, str],
        reply_markup=None,
    ) -> requests.Response:
        """
        Sends a text message (supports inline keyboards).
        """
        url = f"https://api.telegram.org/bot{cls.TELEGRAM_BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": message,
        }

        if reply_markup:
            payload["reply_markup"] = reply_markup.to_dict()

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            print("Failed to send message:", response.text)

        return response

    @classmethod
    def send_message_with_photo_to_chat(
        cls,
        message: str,
        photo_path: str,
        chat_id: Union[int, str],
    ) -> requests.Response:
        """
        Sends a message with a photo attachment.
        """
        url = f"https://api.telegram.org/bot{cls.TELEGRAM_BOT_TOKEN}/sendPhoto"

        with open(photo_path, "rb") as photo:
            files = {"photo": photo}
            params = {
                "chat_id": chat_id,
                "caption": message,
            }
            response = requests.post(url, params=params, files=files)

        if response.status_code != 200:
            print("Failed to send message with photo:", response.text)

        return response

    # =========================
    # MESSAGE BUILDERS
    # =========================

    @classmethod
    def create_message_about_add_user(
        cls,
        admin_of_group: TelegramUser,
        telegram_username: str,
        subscription_start_date: str,
        subscription_end_date: str,
        subscription_plan: str,
        subscription_price: int,
        payment_id: str,
    ) -> str:
        return (
            f"Hi, {admin_of_group}!\n\n"
            f"Action: 🟢 add to private group\n\n"
            f"Subscription Details 📁\n"
            f"--------------------------------------\n"
            f"User: @{telegram_username}\n"
            f"--------------------------------------\n"
            f"Purchased on: {subscription_start_date}\n"
            f"--------------------------------------\n"
            f"Will expire on: {subscription_end_date}\n"
            f"--------------------------------------\n"
            f"Subscription plan: {subscription_plan}\n"
            f"--------------------------------------\n"
            f"Subscription price: {subscription_price} USD\n"
            f"--------------------------------------\n"
            f"Payment ID: {payment_id}\n"
        )

    @classmethod
    def create_message_about_delete_user(
        cls,
        admin_of_group: TelegramUser,
        telegram_username: str,
        subscription_start_date: str,
        subscription_end_date: str,
        subscription_plan: str,
        subscription_price: int,
        payment_id: str,
    ) -> str:
        return (
            f"Hi, {admin_of_group}!\n\n"
            f"Action: 🔴 delete from private group\n\n"
            f"Subscription Details 📁\n"
            f"--------------------------------------\n"
            f"User: @{telegram_username}\n"
            f"--------------------------------------\n"
            f"Purchased on: {subscription_start_date}\n"
            f"--------------------------------------\n"
            f"Expired on: {subscription_end_date}\n"
            f"--------------------------------------\n"
            f"Subscription plan: {subscription_plan}\n"
            f"--------------------------------------\n"
            f"Subscription price: {subscription_price} USD\n"
            f"--------------------------------------\n"
            f"Payment ID: {payment_id}\n"
        )

    @classmethod
    def create_message_about_keep_user(
        cls,
        admin_of_group: TelegramUser,
        telegram_username: str,
        subscription_start_date: str,
        subscription_end_date: str,
        subscription_plan: str,
        subscription_price: int,
        payment_id: str,
    ) -> str:
        return (
            f"Hi, {admin_of_group}!\n\n"
            f"Action: 🟡 keep in private group\n\n"
            f"Subscription Details 📁\n"
            f"--------------------------------------\n"
            f"User: @{telegram_username}\n"
            f"--------------------------------------\n"
            f"Extended on: {subscription_start_date}\n"
            f"--------------------------------------\n"
            f"Will expire on: {subscription_end_date}\n"
            f"--------------------------------------\n"
            f"Subscription plan: {subscription_plan}\n"
            f"--------------------------------------\n"
            f"Subscription price: {subscription_price} USD\n"
            f"--------------------------------------\n"
            f"Payment ID: {payment_id}\n"
        )

    @classmethod
    def create_message_with_subscription_data(
        cls,
        telegram_username: str,
        subscription_plan: str,
        subscription_start_date: str,
        subscription_end_date: str,
        subscription_price: int,
    ) -> str:
        return (
            f"Вы можете продлить уже купленную вами раннее подписку. Вот ее детали:\n"
            f"-------------------------------------\n"
            f"План подписки: {subscription_plan}\n"
            f"-------------------------------------\n"
            f"Дата покупки: {subscription_start_date}\n"
            f"-------------------------------------\n"
            f"Дата окончания: {subscription_end_date}\n"
            f"-------------------------------------\n"
            f"Цена: {subscription_price} USDT\n"
            f"-------------------------------------\n\n"
            f"Вы также можете изменить план подписки просто выбрав другой тариф и оплатив его. "
            f"Таким образом подписка будет продлена согласно новому плану."
        )

    @classmethod
    def create_message_about_reminder(
        cls,
        telegram_username: str,
        day: int,
        syntax_word: str,
    ) -> str:
        if day == 7:
            return (
                f"Привет, @{telegram_username}!\n\n"
                f"Пишу с напоминанием о том, что у тебя заканчивается подписка через {day} {syntax_word} "
                f"на закрытое сообщество «Баффеты на Уораннах»\n\n"
                f"В следующий раз я напомню за 3 дня до окончания доступа.\n\n"
                f"Если сообщение пришло по ошибке — напиши @BaffetnaYorannah\n\n"
            )

        if day == 3:
            return (
                f"Осталось {day} {syntax_word} до окончания доступа в закрытое сообщество "
                f"«Баффеты на Уораннах»\n\n"
                f"Привет, @{telegram_username}!\n\n"
                f"Ты еще можешь продлить доступ на самых выгодных условиях.\n\n"
            )

        if day == 1:
            return (
                f"ОСТАЛСЯ ПОСЛЕДНИЙ {syntax_word.upper()} ДОСТУПА\n\n"
                f"Привет, @{telegram_username}!\n\n"
                f"Через 24 часа бот автоматически удалит тебя из закрытого сообщества.\n\n"
            )

        return ""
