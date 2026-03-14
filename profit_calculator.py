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


def choose_sell_price(group: str, player_price: float, system_price: float) -> float:
    """
    Для шахтных ресурсов используем KIprice.
    Для товаров используем цену игроков, если она есть, иначе KIprice.
    """
    if group == "mine":
        return system_price

    if group == "factory":
        return player_price if player_price > 0 else system_price

    return system_price


def choose_buy_price(group: str, player_price: float, system_price: float) -> float:
    """
    Для закупки пока используем KIprice.
    Это даёт более консервативную и стабильную оценку.
    """
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

        player_price = float(price_info.get("player_price", 0.0))
        system_price = float(price_info.get("system_price", 0.0))

        sell_price = choose_sell_price(group, player_price, system_price)
        buy_price = choose_buy_price(group, player_price, system_price)

        income_day = 0.0
        expense_day = 0.0
        net_profit_day = 0.0

        if balance_day > 0:
            income_day = balance_day * sell_price
            net_profit_day = income_day

        elif balance_day < 0:
            base_expense = abs(balance_day) * buy_price
            expense_day = base_expense * (1 + logistics_percent)
            net_profit_day = -expense_day

        if group == "mine":
            mine_income_day += income_day
            mine_expense_day += expense_day
            mine_net_profit_day += net_profit_day

        elif group == "factory":
            factory_income_day += income_day
            factory_expense_day += expense_day
            factory_net_profit_day += net_profit_day

        profit_rows.append({
            "resource_name": resource_name,
            "group": group,
            "balance_day": balance_day,
            "player_price": player_price,
            "system_price": system_price,
            "sell_price": sell_price,
            "buy_price": buy_price,
            "income_day": income_day,
            "expense_day": expense_day,
            "net_profit_day": net_profit_day,
        })

    total_credits_cost_per_day = float(factory_stats.get("total_credits_cost_per_day", 0.0))

    total_market_net_profit_day = mine_net_profit_day + factory_net_profit_day
    total_net_profit_day = total_market_net_profit_day - total_credits_cost_per_day

    return {
        "profit_rows": profit_rows,
        "logistics_percent": logistics_percent,

        "mine_income_day": mine_income_day,
        "mine_expense_day": mine_expense_day,
        "mine_net_profit_day": mine_net_profit_day,

        "factory_income_day": factory_income_day,
        "factory_expense_day": factory_expense_day,
        "factory_net_profit_day": factory_net_profit_day,

        "total_market_net_profit_day": total_market_net_profit_day,
        "total_credits_cost_per_day": total_credits_cost_per_day,
        "total_net_profit_day": total_net_profit_day,
    }