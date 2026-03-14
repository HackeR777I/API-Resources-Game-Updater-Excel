def safe_float(value, default=0.0):
    try:
        if value is None or str(value).strip() == "":
            return default
        return float(str(value).replace(",", "."))
    except Exception:
        return default


def build_market_price_map(api_data: dict) -> dict:
    market_rates_list = api_data.get("market_rates", [])

    market_price_by_resource = {}

    for row in market_rates_list:
        item_name = str(row.get("itemName", "")).strip()
        player_price = safe_float(row.get("price", 0))
        system_price = safe_float(row.get("KIprice", 0))

        if item_name:
            market_price_by_resource[item_name] = {
                "player_price": player_price,
                "system_price": system_price,
            }

    return market_price_by_resource