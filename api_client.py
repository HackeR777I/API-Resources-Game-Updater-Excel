import requests


BASE_URL = "https://api.resources-game.ch/"


def fetch_api_json(query_id: int, api_key: str):
    params = {
        "q": query_id,
        "k": api_key,
        "f": 1,
        "l": "ru",
        "d": 3
    }

    response = requests.get(BASE_URL, params=params, timeout=(10, 120))

    print(f"\n=== API DEBUG q={query_id} ===")
    print("URL:", response.url)
    print("Status code:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Response preview:", repr(response.text[:500]))

    response.raise_for_status()

    try:
        return response.json()
    except Exception:
        raise RuntimeError(
            f"API вернул не JSON для q={query_id}. "
            f"Status={response.status_code}, "
            f"Content-Type={response.headers.get('Content-Type')}, "
            f"Body={repr(response.text[:500])}"
        )

    return response.json()


def fetch_all_api_data(api_key: str):
    return {
        "mines": fetch_api_json(5, api_key),
        "factories": fetch_api_json(1, api_key),
        "factory_rates": fetch_api_json(1002, api_key),
        "warehouses": fetch_api_json(2, api_key),
        "special_buildings": fetch_api_json(3, api_key),
        "items_catalog": fetch_api_json(1001, api_key),
        "market_rates": fetch_api_json(1006, api_key),
           }