import requests
import time
import validators
from fast_api_app.database import SessionLocal
from fast_api_app import crud, schemas
from fast_api_app.config import get_settings

TOKEN = get_settings().telegram_token
API_URL = f"https://api.telegram.org/bot{TOKEN}"


def send_message(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })


def create_short_url(target_url):
    db = SessionLocal()
    try:
        url_data = schemas.URLBase(target_url=target_url)
        db_url = crud.create_db_url(db=db, url=url_data)

        crud.insert_creted_at(db=db, db_url=db_url)

        base_url = get_settings().base_url
        short_url = f"{base_url}/{db_url.key}"

        return short_url
    finally:
        db.close()


def run_bot():
    print("Бот запущен...")
    last_id = 0

    while True:
        try:
            resp = requests.get(f"{API_URL}/getUpdates", params={
                "offset": last_id + 1,
                "timeout": 30
            }).json()

            for update in resp.get("result", []):
                msg = update["message"]
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")

                if text.startswith(('http://', 'https://')):
                    if validators.url(text):
                        short = create_short_url(text)
                        send_message(chat_id, f"Короткая ссылка: {short}")
                    else:
                        send_message(chat_id, "Неверная ссылка")

                last_id = update["update_id"]

            time.sleep(1)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    run_bot()