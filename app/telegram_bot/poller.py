import os
import time
import django
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from telegram_bot.handlers import handle_start, handle_plan_selected

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
                    "timeout": 50,   # telegram long polling
                },
                timeout=70          # requests timeout MUST be higher
            )

            data = resp.json()

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                # MESSAGE
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")

                    if text.startswith("/start"):
                        handle_start(chat_id)

                # CALLBACK
                elif "callback_query" in update:
                    cb = update["callback_query"]
                    chat_id = cb["message"]["chat"]["id"]
                    data = cb["data"]

                    if data.startswith("PLAN_"):
                        plan_id = int(data.split("_")[1])
                        handle_plan_selected(chat_id, plan_id)

        except Exception:
            print("⚠️ Telegram poll timeout, retrying...")
            time.sleep(3)   # VERY IMPORTANT

        time.sleep(1)



if __name__ == "__main__":
    poll()
