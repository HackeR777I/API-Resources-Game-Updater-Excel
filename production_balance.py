MINE_RESOURCE_ORDER = [
    "Глина",
    "Гравий",
    "Железная руда",
    "Известняк",
    "Ильменит",
    "Медная руда",
    "Уголь",
    "Сырая нефть",
    "Кварцевый песок",
    "Боксит",
    "Литиевая руда",
    "Серебряная руда",
    "Золотая руда",
    "Необработанные алмазы",
]

FACTORY_PRODUCT_ORDER = [
    "Кирпичи",
    "Бетон",
    "Минеральные удобрения",
    "Сталь",
    "Ископаемое топливо",
    "Стекло",
    "Медь",
    "Инсектициды",
    "Алюминий",
    "Пластик",
    "Литий",
    "Аккумуляторы",
    "Оружие",
    "Кремний",
    "Микросхемы",
    "Титан",
    "Медицинские технологии",
    "Серебро",
    "Золото",
    "Украшения",
    "Грузовики",
    "Скан-дроны",
]


def build_production_balance(mine_stats: dict, factory_stats: dict) -> dict:
    mine_output_by_resource = mine_stats.get("mine_output_by_resource", {})
    factory_output_by_resource = factory_stats.get("factory_output_by_resource", {})
    factory_consumption_by_resource = factory_stats.get("factory_consumption_by_resource", {})

    all_resources = (
        set(mine_output_by_resource.keys())
        | set(factory_output_by_resource.keys())
        | set(factory_consumption_by_resource.keys())
    )

    mine_resources_ordered = []
    factory_resources_ordered = []

    # 1. Шахтные ресурсы — строго сверху
    for resource_name in MINE_RESOURCE_ORDER:
        if resource_name in all_resources:
            mine_resources_ordered.append(resource_name)

    # 2. Заводские товары — строго снизу
    for resource_name in FACTORY_PRODUCT_ORDER:
        if resource_name in all_resources:
            factory_resources_ordered.append(resource_name)

    # 3. Всё, что вдруг не попало в списки — докидываем в хвост соответствующего блока
    known_resources = set(mine_resources_ordered) | set(factory_resources_ordered)

    for resource_name in sorted(all_resources, key=lambda x: str(x).lower()):
        if resource_name not in known_resources:
            if resource_name in mine_output_by_resource:
                mine_resources_ordered.append(resource_name)
            else:
                factory_resources_ordered.append(resource_name)

    balance_rows = []

    # Верхний блок — шахты
    for resource_name in mine_resources_ordered:
        mine_output_hour = float(mine_output_by_resource.get(resource_name, 0.0))
        factory_output_hour = float(factory_output_by_resource.get(resource_name, 0.0))
        consumption_hour = float(factory_consumption_by_resource.get(resource_name, 0.0))

        production_hour = mine_output_hour + factory_output_hour
        production_day = production_hour * 24
        consumption_day = consumption_hour * 24
        balance_day = production_day - consumption_day

        balance_rows.append({
            "resource_name": resource_name,
            "production_hour": production_hour,
            "production_day": production_day,
            "consumption_hour": consumption_hour,
            "consumption_day": consumption_day,
            "balance_day": balance_day,
            "group": "mine",
        })

    # Разделитель между блоками
    if mine_resources_ordered and factory_resources_ordered:
        balance_rows.append({
            "resource_name": "",
            "production_hour": "",
            "production_day": "",
            "consumption_hour": "",
            "consumption_day": "",
            "balance_day": "",
            "group": "separator",
        })

    # Нижний блок — заводы
    for resource_name in factory_resources_ordered:
        mine_output_hour = float(mine_output_by_resource.get(resource_name, 0.0))
        factory_output_hour = float(factory_output_by_resource.get(resource_name, 0.0))
        consumption_hour = float(factory_consumption_by_resource.get(resource_name, 0.0))

        production_hour = mine_output_hour + factory_output_hour
        production_day = production_hour * 24
        consumption_day = consumption_hour * 24
        balance_day = production_day - consumption_day

        balance_rows.append({
            "resource_name": resource_name,
            "production_hour": production_hour,
            "production_day": production_day,
            "consumption_hour": consumption_hour,
            "consumption_day": consumption_day,
            "balance_day": balance_day,
            "group": "factory",
        })

    return {
        "balance_rows": balance_rows
    }