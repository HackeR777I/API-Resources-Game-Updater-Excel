def calculate_logistics_percent(special_building_stats: dict) -> float:
    """
    Базовая логистика = 15%
    Каждый уровень 'Транспортной компании' снижает её на 1%
    Минимум = 5%
    """
    transport_level = 0

    for row in special_building_stats.get("special_building_rows", []):
        if str(row["building_name"]).strip().lower() == "транспортная компания":
            transport_level = int(row["level"])
            break

    logistics_percent = 0.15 - (transport_level * 0.01)
    return max(logistics_percent, 0.05)


def choose_effective_price(player_price: float, system_price: float) -> float:
    """
    Если есть ставка игроков, берём её.
    Иначе берём системную ставку.
    """
    if player_price > 0:
        return player_price
    return system_price


def build_daily_profit_report(
    production_balance: dict,
    market_price_by_resource: dict,
    factory_stats: dict,
    special_building_stats: dict,
) -> dict:
    logistics_percent = calculate_logistics_percent(special_building_stats)

    profit_rows = []

    mine_income_day = 0.0
    mine_expense_day = 0.0
    mine_net_profit_day = 0.0

    factory_income_day = 0.0
    factory_expense_day = 0.0
    factory_net_profit_day = 0.0

    for row in production_balance.get("balance_rows", []):
        if row.get("group") == "separator":
            continue

        resource_name = row["resource_name"]
        group = row["group"]
        balance_day = float(row["balance_day"])

        price_info = market_price_by_resource.get(
            resource_name,
            {"player_price": 0.0, "system_price": 0.0}
        )

        player_price = float(price_info.get("player_price", 0