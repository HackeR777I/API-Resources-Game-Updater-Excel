from typing import Dict


def calculate_profit(
    production_per_day: Dict[str, float],
    consumption_per_day: Dict[str, float],
    market_prices: Dict[str, Dict[str, float]],
    logistics_percent: float = 15.0
) -> Dict[str, float]:

    logistics_multiplier = 1 + (logistics_percent / 100)

    income = 0.0
    expenses = 0.0

    for item, amount in production_per_day.items():

        if amount <= 0:
            continue

        price_data = market_prices.get(item)

        if not price_data:
            continue

        price = price_data.get("price", 0)
        ki_price = price_data.get("KIprice", 0)

        sell_price = max(price, ki_price)

        income += amount * sell_price

    for item, amount in consumption_per_day.items():

        if amount <= 0:
            continue

        price_data = market_prices.get(item)

        if not price_data:
            continue

        price = price_data.get("price", 0)
        ki_price = price_data.get("KIprice", 0)

        buy_price = max(price, ki_price)

        expenses += amount * buy_price * logistics_multiplier

    net_profit = income - expenses

    return {
        "income": income,
        "expenses": expenses,
        "net_profit": net_profit
    }
