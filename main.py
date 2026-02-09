import hashlib
import hmac
import json
import time
import random

import requests
from dotenv import load_dotenv

load_dotenv()
import os


# Формирование подписи HMAC SHA256
def sign_request(body, secret_key):
    timestamp = int(time.time())
    # ensure_ascii=False для поддержки кириллицы, separators=(",", ":") для удаления пробелов
    body_json = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
    print(f"body json {body_json}")
    payload = f"{timestamp}.{body_json}"

    signature = hmac.new(
        secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    return timestamp, signature, body_json


# Отправка в External Contact Registration API
def send_external_registration(body):
    timestamp, signature, body_signed = sign_request(body, os.getenv("EXTERNAL_SECRET_KEY"))

    response = requests.post(
        f"{
            os.getenv('EXTERNAL_BASE_URL', 'https://p.newpeople.pro/api')
        }/external/contact/register",
        headers={
            "Authorization": f"Bearer {os.getenv('EXTERNAL_HASH_TOKEN')}",
            "X-Timestamp": str(timestamp),
            "X-Signature": signature,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        },
        data=body_signed,
    )

    try:
        data = response.json()
        print(f"data {data}")
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

    print("\n[2] URL:")
    print(
        f"    {os.getenv('EXTERNAL_BASE_URL', 'https://p.newpeople.pro/api')}/external/contact/register"
    )

    print("\n[3] Заголовки:")
    print(f"    Authorization: Bearer {f'{os.getenv("EXTERNAL_HASH_TOKEN")}'}")
    print(f"    X-Timestamp: {str(timestamp)}")
    print(f"    X-Signature: {signature}")
    print("    Content-Type: application/json")
    print("    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0")

    print("\n[4] Тело запроса (отправляется):")
    print(f"    {body_signed}")

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
    random_part = random.randint(1000000, 9999999)
    phone = f"+7900{random_part}"
    body = {"phone": phone, "os_consent": True, "first_name": "Ivan"}

    result = send_external_registration(body)

    if not result["success"]:
        # Можно вывести кастомное сообщение для фронтенда
        print("Ошибка отправки:", result)


main()
