from collections import defaultdict


def safe_float(value, default=0.0):
    try:
        if value is None or str(value).strip() == "":
            return default
        return float(str(value).replace(",", "."))
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        if value is None or str(value).strip() == "":
            return default
        return int(float(value))
    except Exception:
        return default


def resolve_item_name(item_id, item_id_to_name: dict) -> str:
    item_id = str(item_id).strip()
    return item_id_to_name.get(item_id, f"ID {item_id}")

def build_factory_statistics(api_data: dict, item_id_to_name: dict) -> dict:
    factories_list = api_data.get("factories", [])
    factory_rates_list = api_data.get("factory_rates", [])

    # Рецепты по factoryID
    rates_by_factory_id = {}
    for row in factory_rates_list:
        factory_id = str(row.get("factoryID", "")).strip()
        if factory_id:
            rates_by_factory_id[factory_id] = row

    factory_rows = []

    factory_output_by_resource = defaultdict(float)
    factory_consumption_by_resource = defaultdict(float)
    
    total_credits_cost_per_day = 0.0

    for row in factories_list:
        factory_id = str(row.get("factoryID", "")).strip()
        factory_name = str(row.get("name", "")).strip()

        if not factory_name:
            factory_name = f"Factory {factory_id}"

        level = safe_int(row.get("lvl", 0))
        strike = str(row.get("strike", "")).strip().lower()

        rate_row = rates_by_factory_id.get(factory_id, {})

        output_item_id = str(rate_row.get("itemID", "")).strip()
        output_item_name = str(rate_row.get("itemName", "")).strip()
        if not output_item_name and output_item_id:
            output_item_name = resolve_item_name(output_item_id, item_id_to_name)

        base_output_per_hour = safe_float(rate_row.get("baseOutputPerHour", 0))
        output_per_cycle = safe_float(rate_row.get("outputPerCycle", 0))
        credits_per_cycle = safe_float(rate_row.get("creditsPerCycle", 0))

        # Если завод в strike, можно при желании обнулять выпуск
        is_active = strike != "yes"
        
        output_per_hour = base_output_per_hour * level if is_active else 0.0
        output_per_day = output_per_hour * 24

        cycles_per_hour = (base_output_per_hour / output_per_cycle) if output_per_cycle else 0.0
        cycles_per_day = cycles_per_hour * 24

        credits_cost_per_hour = credits_per_cycle * cycles_per_hour * level
        credits_cost_per_day = credits_cost_per_hour * 24

        total_credits_cost_per_day += credits_cost_per_day

        inputs = []

        for idx in (1, 2, 3):
            input_item_id = str(rate_row.get(f"itemID{idx}", "")).strip()
            qty_per_cycle = safe_float(rate_row.get(f"item{idx}QtyPerCycle", 0))

            if input_item_id and input_item_id.lower() != "null" and qty_per_cycle:
                input_item_name = resolve_item_name(input_item_id, item_id_to_name)
                
                is_active = strike != "yes"
                effective_level = level if is_active else 0

                amount_per_hour = qty_per_cycle * cycles_per_hour * effective_level
                amount_per_day = qty_per_cycle * cycles_per_day * effective_level

                inputs.append({
                    "item_id": input_item_id,
                    "item_name": input_item_name,
                    "qty_per_cycle": qty_per_cycle,
                    "amount_per_hour": amount_per_hour,
                    "amount_per_day": amount_per_day,
                })

                factory_consumption_by_resource[input_item_name] += amount_per_hour

        if output_item_name and output_per_hour:
            factory_output_by_resource[output_item_name] += output_per_hour

        factory_rows.append({
            "factory_id": factory_id,
            "factory_name": factory_name,
            "level": level,
            "strike": strike,

            "output_item_id": output_item_id,
            "output_item_name": output_item_name,

            "base_output_per_hour": base_output_per_hour,
            "output_per_cycle": output_per_cycle,
            "credits_per_cycle": credits_per_cycle,

            "output_per_hour": output_per_hour,
            "output_per_day": output_per_day,

            "cycles_per_hour": cycles_per_hour,
            "cycles_per_day": cycles_per_day,
            "credits_cost_per_hour": credits_cost_per_hour,
            "credits_cost_per_day": credits_cost_per_day,

            "inputs": inputs,
        })

    factory_rows = sorted(factory_rows, key=lambda x: str(x["factory_name"]).lower())

    return {
        "factory_rows": factory_rows,
        "factory_output_by_resource": dict(factory_output_by_resource),
        "factory_consumption_by_resource": dict(factory_consumption_by_resource),
        "total_credits_cost_per_day": total_credits_cost_per_day,
    }
