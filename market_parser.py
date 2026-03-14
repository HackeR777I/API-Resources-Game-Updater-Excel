def parse_market_rates(market_json):

    market_prices = {}

    for row in market_json:

        item_id = str(row.get("itemID"))

        market_prices[item_id] = {
            "price": float(row.get("price", 0)),
            "KIprice": float(row.get("KIprice", 0))
        }

    return market_prices