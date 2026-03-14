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


def build_warehouse_statistics(api_data: dict, item_id_to_name: dict) -> dict:
    warehouses_list = api_data.get("warehouses", [])

    warehouse_rows = []

    for row in warehouses_list:
        resource_id = str(row.get("resourceID", "")).strip()

        resource_name = str(row.get("resourceName", "")).strip()
        if not resource_name and resource_id:
            resource_name = resolve_item_name(resource_id, item_id_to_name)
        if not resource_name:
            resource_name = f"ID {resource_id}"

        level = safe_int(
            row.get("warehouseLevel", row.get("level", 0))
        )

        stored_amount = safe_float(
            row.get("resourceAmount", row.get("amount", 0))
        )

        capacity = safe_float(
            row.get("storageCapacity", row.get("capacity", 0))
        )

        warehouse_rows.append({
            "resource_id": resource_id,
            "resource_name": resource_name,
            "level": level,
            "stored_amount": stored_amount,
            "capacity": capacity,
        })

    warehouse_rows = sorted(
        warehouse_rows,
        key=lambda x: str(x["resource_name"]).lower()
    )

    return {
        "warehouse_rows": warehouse_rows
    }