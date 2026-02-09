import os
import json
import time
import hmac
import hashlib
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class ApiClient:
    def __init__(self):
        self.hash_token = os.getenv("EXTERNAL_HASH_TOKEN")
        self.secret_key = os.getenv("EXTERNAL_SECRET_KEY")
        # Читаем настройки домена (если есть)
        self.origin = os.getenv("EXTERNAL_ORIGIN")
        self.referer = os.getenv("EXTERNAL_REFERER")

        self.base_url = os.getenv(
            "EXTERNAL_BASE_URL", "https://p.newpeople.pro/app"
        ).rstrip("/")

        if not self.hash_token:
            raise ValueError("EXTERNAL_HASH_TOKEN is not set in .env")
        if not self.secret_key or self.secret_key == "REPLACE_WITH_YOUR_SECRET_KEY":
            print(
                "WARNING: EXTERNAL_SECRET_KEY is not set correctly. Requests will fail signature check."
            )

    def sign_request(self, body):
        """Формирует timestamp и HMAC SHA256 подпись."""
        timestamp = int(time.time())

        # Для подписи - без пробелов (как сервер может ожидать)
        body_json_for_sign = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
        payload = f"{timestamp}.{body_json_for_sign}"

        signature = hmac.new(
            self.secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # Для отправки - с пробелами (как в примере ТЗ)
        body_json_for_send = json.dumps(body, ensure_ascii=False)

        return timestamp, signature, body_json_for_send, body_json_for_sign, payload

    def register_contact(
        self, body, use_invalid_token=False, use_invalid_signature=False
    ):
        """Отправляет запрос регистрации контакта."""
        timestamp, signature, body_json, body_json_for_sign, payload = (
            self.sign_request(body)
        )

        token = "INVALID_TOKEN" if use_invalid_token else self.hash_token

        if use_invalid_signature:
            signature = "0" * 64  # Неверная подпись

        headers = {
            "Authorization": f"Bearer {token}",
            "X-Timestamp": str(timestamp),
            "X-Signature": signature,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        }

        # Если задан домен в .env - добавляем заголовки
        if self.origin:
            headers["Origin"] = self.origin
        if self.referer:
            headers["Referer"] = self.referer

        url = f"{self.base_url}/external/contact/register"

        # Детальный вывод каждого шага
        print("\n" + "=" * 60)
        print("ЗАПРОС К API")
        print("=" * 60)

        print(f"\n[1] URL: {url}")
        print(f"[2] Метод: POST")

        print(f"\n[3] Заголовки:")
        print(f"    Authorization: Bearer {token[:20]}...")
        print(f"    X-Timestamp: {timestamp}")
        print(f"    X-Signature: {signature[:20]}...")
        print(f"    Content-Type: application/json")
        print(f"    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0")
        if self.origin:
            print(f"    Origin: {self.origin}")
        if self.referer:
            print(f"    Referer: {self.referer}")

        print(f"\n[4] Тело запроса (отправляется):")
        print(f"    {body_json}")

        print(f"\n[5] Тело для подписи (JSON без пробелов):")
        print(f"    {body_json_for_sign}")

        print(f"\n[6] Payload для HMAC (timestamp.body):")
        print(f"    {payload}")

        print(f"\n[7] Secret Key:")
        print(f"    {self.secret_key}")

        print(f"\n[8] Результат HMAC-SHA256:")
        print(f"    {signature}")

        print("\n" + "-" * 60)
        print("ОТПРАВКА ЗАПРОСА...")
        print("-" * 60)

        response = requests.post(url, headers=headers, data=body_json)

        print(f"\n[9] Статус ответа: {response.status_code}")
        print(f"\n[10] Заголовки ответа:")
        for key, value in response.headers.items():
            print(f"     {key}: {value}")

        print(f"\n[11] Тело ответа:")
        print(f"     {response.text}")
        print("=" * 60 + "\n")

        try:
            data = response.json()
        except ValueError:
            data = response.text

        return {
            "status_code": response.status_code,
            "data": data,
            "headers": response.headers,
        }
