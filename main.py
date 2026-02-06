import hashlib
import hmac
import json
import time

import requests
from dotenv import load_dotenv

load_dotenv()
import os


# Формирование подписи HMAC SHA256
def sign_request(body, secret_key):
    timestamp = int(time.time())
    body_json = json.dumps(body, separators=(",", ":"))
    print(f"body json {body_json}")
    payload = f"{timestamp}.{body_json}"

    signature = hmac.new(
        secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    return timestamp, signature


# Отправка в External Contact Registration API
def send_external_registration(body):
    timestamp, signature = sign_request(body, os.getenv("EXTERNAL_SECRET_KEY"))

    response = requests.post(
        f"{
            os.getenv('EXTERNAL_BASE_URL', 'https://p.newpeople.pro/app')
        }/external/contact/register",
        headers={
            "Authorization": f"Bearer {os.getenv('EXTERNAL_HASH_TOKEN')}",
            "X-Timestamp": str(timestamp),
            "X-Signature": signature,
            "Content-Type": "application/json",
        },
        data=json.dumps(body),
    )

    try:
        data = response.json()
    except ValueError:
        data = None

    # Проверка успешного статуса
    if response.status_code == 201:
        print("✅ Успешная регистрация:", data)
        return {"success": True, "data": data}

    # Вывод ошибок
    print("❌ Ошибка регистрации")
    print("HTTP статус:", response.status_code)
    print("Ответ сервера:", data)

    print("\n" + "=" * 60)
    print("ЗАПРОС К API")
    print("=" * 60)

    print("\n[3] Заголовки:")
    print(f"    Authorization: Bearer {f'Bearer {os.getenv("EXTERNAL_HASH_TOKEN")}'}")
    print(f"    X-Timestamp: {str(timestamp)}")
    print(f"    X-Signature: {signature}")
    print("    Content-Type: application/json")

    print("\n[4] Тело запроса (отправляется):")
    print(f"    {body}")

    print("\n[5] Тело для подписи (JSON без пробелов):")
    print(f"    {json.dumps(body, separators=(',', ':'))}")

    print("\n[8] Результат HMAC-SHA256:")
    print(f"    {signature}")

    print(f"\n[9] Статус ответа: {response.status_code}")
    print("\n[10] Заголовки ответа:")
    for key, value in response.headers.items():
        print(f"     {key}: {value}")

    print("\n[11] Тело ответа:")
    print(f"     {response.text}")
    print("=" * 60 + "\n")
    print("\nОтвет json")

    return {"success": False, "status": response.status_code, "data": data}


# ===== Пример использования =====
def main():
    body = {"phone": "+79001234567", "os_consent": True, "first_name": "Ivan"}

    result = send_external_registration(body)

    if not result["success"]:
        # Можно вывести кастомное сообщение для фронтенда
        print("Ошибка отправки:", result)


main()
