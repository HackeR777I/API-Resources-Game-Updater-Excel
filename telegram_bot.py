import requests
import time

from config import BOT_TOKEN, CHAT_ID
from report_runner import build_and_send_report
from telegram_sender import send_telegram_message

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

last_update_id = None
report_in_progress = False


def get_updates():
    global last_update_id

    params = {"timeout": 30}
    if last_update_id:
        params["offset"] = last_update_id + 1

    response = requests.get(f"{API_URL}/getUpdates", params=params, timeout=35)
    return response.json()


def handle_command(chat_id: int, text: str):
    global report_in_progress

    # 🔒 защита: только твой chat_id
    if str(chat_id) != str(CHAT_ID):
        return

    # --- команды ---
    if text == "/report":
        if report_in_progress:
            send_telegram_message(
                BOT_TOKEN,
                CHAT_ID,
                "Отчёт уже формируется 😄"
            )
            return

        report_in_progress = True

        send_telegram_message(
            BOT_TOKEN,
            CHAT_ID,
            "Запускаю формирование полного отчёта..."
        )

        try:
            build_and_send_report()

            send_telegram_message(
                BOT_TOKEN,
                CHAT_ID,
                "Отчёт успешно сформирован и отправлен ✅"
            )

        except Exception as e:
            send_telegram_message(
                BOT_TOKEN,
                CHAT_ID,
                f"Ошибка при формировании отчёта:\n{e}"
            )

        finally:
            report_in_progress = False

    elif text == "/ping":
        send_telegram_message(
            BOT_TOKEN,
            CHAT_ID,
            "Я жив 😄"
        )

    elif text == "/status":
        status = "занят" if report_in_progress else "свободен"
        send_telegram_message(
            BOT_TOKEN,
            CHAT_ID,
            f"Статус: {status}"
        )


def run_bot():
    global last_update_id

    while True:
        try:
            data = get_updates()

            for update in data.get("result", []):
                last_update_id = update["update_id"]

                message = update.get("message")
                if not message:
                    continue

                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                handle_command(chat_id, text)

        except Exception as e:
            print("Ошибка в боте:", e)

        time.sleep(1)


if __name__ == "__main__":
    run_bot()