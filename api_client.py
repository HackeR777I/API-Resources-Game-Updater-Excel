import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import (
    API_KEY,
    BASE_URL,
    API_LANG,
    API_FORMAT,
    TIMEOUT_CONNECT,
    TIMEOUT_READ,
    API_RETRY_COUNT,
)

if not API_KEY:
    raise ValueError("В config.py не указан API_KEY")


def create_session() -> requests.Session:
    retry = Retry(
        total=API_RETRY_COUNT,
        connect=API_RETRY_COUNT,
        read=API_RETRY_COUNT,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    adapter = HTTPAdapter(max_retries=retry)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


SESSION = create_session()


def fetch_api_json(query_code: int, extra_params: dict | None = None) -> list | dict:
    params = {
        "q": query_code,
        "k": API_KEY,
        "f": API_FORMAT,
        "l": API_LANG,
    }

    if extra_params:
        params.update(extra_params)

    last_error = None

    for attempt in range(1, API_RETRY_COUNT + 1):
        try:
            response = SESSION.get(
                BASE_URL,
                params=params,
                timeout=(TIMEOUT_CONNECT, TIMEOUT_READ),
            )

            print(f"[API DEBUG] q={query_code}")
            print(f"[API DEBUG] URL: {response.url}")
            print(f"[API DEBUG] Status code: {response.status_code}")
            print(f"[API DEBUG] Content-Type: {response.headers.get('Content-Type')}")
            print(f"[API DEBUG] Response text (first 200 chars): {response.text[:200]!r}")

            response.raise_for_status()

            if not response.text.strip():
                raise RuntimeError(f"Пустой ответ API для q={query_code}")

            content_type = response.headers.get("Content-Type", "")
            if "json" not in content_type.lower():
                raise RuntimeError(
                    f"API вернул не JSON для q={query_code}: {response.text[:200]!r}"
                )

            return response.json()

        except Exception as error:
            last_error = error
            print(f"[API] Ошибка запроса q={query_code}, попытка {attempt}/{API_RETRY_COUNT}: {error}")

            if attempt < API_RETRY_COUNT:
                time.sleep(3)

    raise RuntimeError(f"Не удалось получить данные API для q={query_code}: {last_error}")


def fetch_all_api_data() -> dict:
    return {
        "factories": fetch_api_json(1),
        "warehouses": fetch_api_json(2),
        "special_buildings": fetch_api_json(3),
        "mines": fetch_api_json(5),
        "items_catalog": fetch_api_json(1001),
        "factory_rates": fetch_api_json(1002),
        "market_rates": fetch_api_json(1006, {"d": 3}),
    }