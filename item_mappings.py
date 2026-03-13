def build_item_id_to_name(api_data: dict) -> dict:
    """
    Строит словарь соответствий itemID -> itemName
    из всех доступных источников API.
    """
    item_id_to_name = {}

    items_catalog = api_data.get("items_catalog", [])
    factory_rates = api_data.get("factory_rates", [])
    warehouses = api_data.get("warehouses", [])
    mine_resources = api_data.get("mine_output_by_resource_id", {})

    # Основной каталог предметов
    for row in items_catalog:
        item_id = str(row.get("itemID", "")).strip()
        item_name = str(row.get("itemName", row.get("itemname", ""))).strip()

        if item_id and item_name:
            item_id_to_name[item_id] = item_name

    # Иногда названия встречаются только здесь
    for row in factory_rates:
        item_id = str(row.get("itemID", "")).strip()
        item_name = str(row.get("itemName", row.get("itemname", ""))).strip()

        if item_id and item_name:
            item_id_to_name[item_id] = item_name

    # Склады
    for row in warehouses:
        resource_id = str(row.get("resourceID", "")).strip()
        resource_name = str(row.get("resourceName", "")).strip()

        if resource_id and resource_name and resource_id not in item_id_to_name:
            item_id_to_name[resource_id] = resource_name

    # Ресурсы шахт
    for resource_id, resource_name in mine_resources.items():
        resource_id = str(resource_id).strip()
        resource_name = str(resource_name).strip()

        if resource_id and resource_name and resource_id not in item_id_to_name:
            item_id_to_name[resource_id] = resource_name

    return item_id_to_name


def resolve_item_name(item_id, item_map: dict) -> str:
    """
    Безопасно возвращает имя предмета по ID.
    Если ID неизвестен — возвращает 'ID xxxx'.
    """
    item_id = str(item_id).strip()
    return item_map.get(item_id, f"ID {item_id}")
