def build_resource_groups(
    mine_output_by_resource: dict,
    factory_output_by_resource: dict,
    factory_consumption_by_resource: dict,
) -> dict:
    """
    Классифицирует ресурсы по группам:
    - mine_resources: ресурсы шахт
    - factory_products: товары/ресурсы, производимые заводами
    - consumption_only: ресурсы, которые только потребляются
    """
    mine_resources = set(mine_output_by_resource.keys())
    factory_products = set(factory_output_by_resource.keys())
    consumption_resources = set(factory_consumption_by_resource.keys())

    consumption_only = consumption_resources - mine_resources - factory_products

    return {
        "mine_resources": mine_resources,
        "factory_products": factory_products,
        "consumption_only": consumption_only,
    }


def sort_resources_for_balance(
    all_resources,
    mine_resources: set,
    factory_products: set,
    consumption_only: set,
):
    """
    Возвращает ресурсы в удобном порядке:
    1. шахтные ресурсы
    2. товары заводов
    3. прочие/только потребляемые ресурсы

    Внутри каждой группы — сортировка по имени.
    """

    def sort_key(resource):
        resource_name = str(resource).lower()

        if resource in mine_resources:
            group_order = 0
        elif resource in factory_products:
            group_order = 1
        elif resource in consumption_only:
            group_order = 2
        else:
            group_order = 3

        return (group_order, resource_name)

    return sorted(all_resources, key=sort_key)