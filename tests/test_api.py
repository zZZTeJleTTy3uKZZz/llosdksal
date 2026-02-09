import pytest
import random
from client import ApiClient

@pytest.fixture
def client():
    return ApiClient()

@pytest.fixture
def valid_payload():
    """Генерация уникального телефона для каждого теста, чтобы избежать 422 (Duplicate)."""
    random_part = random.randint(1000000, 9999999)
    return {
        "phone": f"+7900{random_part}",
        "os_consent": True,
        "first_name": "Тест",
        "last_name": "Тестов",
        "email": f"test{random_part}@example.com",
        "comment": "Auto-test pytest"
    }

def test_01_positive_registration(client, valid_payload):
    """
    1. Позитивный кейс
    Ожидаем 201 и появление касания в CRM.
    """
    if client.secret_key == "REPLACE_WITH_YOUR_SECRET_KEY":
        pytest.skip("Secret key is missing")

    response = client.register_contact(valid_payload)
    
    assert response["status_code"] == 201, f"Expected 201, got {response['status_code']}. Resp: {response['data']}"
    assert response["data"].get("success") is True

def test_02_validation_error_no_phone(client):
    """
    2. Валидация формы
    Без телефона. Ожидаем 400.
    """
    payload = {
        "os_consent": True,
        "first_name": "БезТелефона",
        "last_name": "Ошибка"
    }
    response = client.register_contact(payload)
    assert response["status_code"] == 400, f"Expected 400, got {response['status_code']}"

def test_03_validation_error_no_consent(client):
    """
    2. Валидация формы
    Без согласия. Ожидаем 400.
    """
    payload = {
        "phone": "+79001112233",
        "os_consent": False,
        "first_name": "БезСогласия",
        "last_name": "Ошибка"
    }
    response = client.register_contact(payload)
    assert response["status_code"] == 400, f"Expected 400, got {response['status_code']}"

def test_04_auth_invalid_token(client, valid_payload):
    """
    3. Авторизация
    Подменить hash_token на неверный. Ожидаем 401 или 403.
    """
    response = client.register_contact(valid_payload, use_invalid_token=True)
    assert response["status_code"] in [401, 403], f"Expected 401/403, got {response['status_code']}"

def test_05_auth_invalid_signature(client, valid_payload):
    """
    3. Авторизация
    Сломать подпись. Ожидаем 401 или 403.
    """
    if client.secret_key == "REPLACE_WITH_YOUR_SECRET_KEY":
        pytest.skip("Secret key is missing")

    response = client.register_contact(valid_payload, use_invalid_signature=True)
    assert response["status_code"] in [401, 403], f"Expected 401/403, got {response['status_code']}"

def test_06_duplicate_registration(client, valid_payload):
    """
    4. Повторная регистрация
    Дважды отправить форму с тем же телефоном. Ожидаем 422.
    """
    if client.secret_key == "REPLACE_WITH_YOUR_SECRET_KEY":
        pytest.skip("Secret key is missing")

    # Первая отправка
    resp1 = client.register_contact(valid_payload)
    assert resp1["status_code"] == 201, "First request failed"

    # Вторая отправка (сразу же)
    resp2 = client.register_contact(valid_payload)
    assert resp2["status_code"] == 422, f"Expected 422 for duplicate, got {resp2['status_code']}"
