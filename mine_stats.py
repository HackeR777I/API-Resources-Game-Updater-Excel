from collections import defaultdict
from datetime import datetime


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


def format_timestamp(value) -> str:
    try:
        ts = int(float(value))
        return datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M:%S")
    except Exception:
        return ""


def calculate_effective_output(fullrate: float) -> float:
    """
    Эффективная добыча = 96% от fullrate
    """
    return fullrate * 0.96


def build_mine_statistics(api_data: dict, item_id_to_name: dict) -> dict:
    mines_list = api_data.get("mines", [])

    mines_by_resource = defaultdict(list)
    mine_output_by_resource = defaultdict(float)
    mine_output_by_resource_id = {}

    for row in mines_list:
        resource_id = str(row.get("resourceID", "")).strip()
        resource_name = item_id_to_name.get(
            resource_id,
            str(row.get("resourceName", "")).strip()
        )

        if not resource_name:
            resource_name = f"ID {resource_id}"

        hq_boost = safe_float(row.get("HQboost"))
        tech_factor = safe_float(row.get("techfactor"))
        rawrate = safe_float(row.get("rawrate"))
        fullrate = safe_float(row.get("fullrate"))
        condition = safe_float(row.get("condition"))
        quality = safe_float(row.get("quality"))

        last_maintenance = format_timestamp(row.get("lastmaintenance"))
        build_date = format_timestamp(row.get("builddate"))

        effective_output_hour = calculate_effective_output(fullrate)
        effective_output_day = effective_output_hour * 24

        mine_row = {
            "resource_id": resource_id,
            "resource_name": resource_name,

            "hq_boost": hq_boost,
            "tech_factor": tech_factor,
            "rawrate": rawrate,
            "fullrate": fullrate,
            "condition": condition,
            "quality": quality,
            "last_maintenance": last_maintenance,
            "build_date": build_date,
            "effective_output_hour": effective_output_hour,
            "effective_output_day": effective_output_day,
        }

        mines_by_resource[resource_name].append(mine_row)
        mine_output_by_resource[resource_name] += effective_output_hour

        if resource_id and resource_name:
            mine_output_by_resource_id[resource_id] = resource_name

    summary_rows = []

    for resource_name in sorted(mines_by_resource.keys(), key=lambda x: str(x).lower()):
        rows = mines_by_resource[resource_name]

        count = len(rows)
        qualities = [r["quality"] for r in rows]
        conditions = [r["condition"] for r in rows]
        rawrates = [r["rawrate"] for r in rows]
        fullrates = [r["fullrate"] for r in rows]
        outputs_hour = [r["effective_output_hour"] for r in rows]
        outputs_day = [r["effective_output_day"] for r in rows]

        summary_rows.append({
            "resource_name": resource_name,
            "mine_count": count,
            "avg_quality": sum(qualities) / count if count else 0.0,
            "min_quality": min(qualities) if qualities else 0.0,
            "max_quality": max(qualities) if qualities else 0.0,
            "avg_condition": sum(conditions) / count if count else 0.0,
            "total_rawrate_hour": sum(rawrates),
            "total_fullrate_hour": sum(fullrates),
            "total_effective_output_hour": sum(outputs_hour),
            "total_effective_output_day": sum(outputs_day),
        })

    resource_sheets = {}

    for resource_name, rows in mines_by_resource.items():
        sorted_rows = sorted(
            rows,
            key=lambda r: (-r["quality"], -r["effective_output_hour"])
        )

        numbered_rows = []
        for idx, row in enumerate(sorted_rows, start=1):
            numbered_row = {
                "number": idx,
                **row
            }
            numbered_rows.append(numbered_row)

        resource_sheets[resource_name] = numbered_rows

    return {
        "summary_rows": summary_rows,
        "resource_sheets": resource_sheets,
        "mine_output_by_resource": dict(mine_output_by_resource),
        "mine_output_by_resource_id": mine_output_by_resource_id,
    }
