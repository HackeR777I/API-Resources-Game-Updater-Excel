def safe_int(value, default=0):
    try:
        if value is None or str(value).strip() == "":
            return default
        return int(float(value))
    except Exception:
        return default


def build_special_building_statistics(api_data: dict) -> dict:
    special_buildings_list = api_data.get("special_buildings", [])

    special_building_rows = []

    for row in special_buildings_list:
        building_id = str(row.get("specbID", "")).strip()

        building_name = str(row.get("name", "")).strip()
        if not building_name:
            building_name = f"Special Building {building_id}"

        level = safe_int(row.get("lvl", 0))

        special_building_rows.append({
            "building_id": building_id,
            "building_name": building_name,
            "level": level,
        })

    special_building_rows = sorted(
        special_building_rows,
        key=lambda x: str(x["building_name"]).lower()
    )

    return {
        "special_building_rows": special_building_rows
    }
