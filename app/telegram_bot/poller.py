import os
import time
import django
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from telegram_bot.handlers import (
    handle_start,
    handle_plan_selected,
    handle_verify,
)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


def poll():
    offset = 0

    while True:
        try:
            resp = requests.get(
                f"{BASE_URL}/getUpdates",
                params={
                    "offset": offset,
                    "timeout": 50,   # Telegram long polling
                },
                timeout=70          # Requests timeout MUST be higher
            )

            data = resp.json()

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                # -----------------------
                # MESSAGE HANDLING
                # -----------------------
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "").strip()

                    if text.startswith("/start"):
                        handle_start(chat_id, text)

                    elif text == "/verify":
                        handle_verify(chat_id)

                # -----------------------
                # CALLBACK HANDLING
                # -----------------------
                elif "callback_query" in update:
                    cb = update["callback_query"]
                    chat_id = cb["message"]["chat"]["id"]
                    data = cb["data"]

                    if data.startswith("PLAN_"):
                        plan_id = int(data.split("_")[1])
                        handle_plan_selected(chat_id, plan_id)

        except Exception as e:
            print(f"⚠️ Telegram poll error: {e}")
            time.sleep(3)   # IMPORTANT backoff

        time.sleep(1)


if __name__ == "__main__":
    poll()
