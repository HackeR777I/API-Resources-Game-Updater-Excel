from pathlib import Path
from datetime import datetime
from openpyxl import Workbook
import shutil

from api_client import fetch_all_api_data
from item_mappings import build_item_id_to_name
from resource_classifier import build_resource_groups, sort_resources_for_balance
from mine_stats import build_mine_statistics
from mine_excel_builder import build_mine_workbook_part
from factory_stats import build_factory_statistics
from special_buildings_stats import build_special_building_statistics
from warehouse_stats import build_warehouse_statistics
from buildings_excel_builder import build_buildings_workbook_part
from production_balance import build_production_balance
from production_balance_excel_builder import build_production_balance_sheet
from market_rates import build_market_price_map
from profit_calculator import build_daily_profit_report




api_key = "f760a8f5bc91b3f74dd93ebd05c6fc03699cecbce8239"

def archive_old_reports(report_dir:Path):
    archive_dir = report_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    
    for file in report_dir.glob("*.xlsx"):
        target = archive_dir / file.name
        shutil.move(str(file), str(target))

def main() -> None:
    print("=== Resources Game API Report ===")
    api_data = fetch_all_api_data(api_key)
    market_prices = parse_market_rates(api_data["market_rates"])
    
    item_id_to_name = build_item_id_to_name(api_data)
    print("Словарь ресурсов построен.")
    print("Всего известных ресурсов:", len(item_id_to_name))
    
    mine_stats = build_mine_statistics(api_data, item_id_to_name)
    
    factory_stats = build_factory_statistics(api_data, item_id_to_name)
    print("Статистика по заводам построена")
    print("Заводов:", len(factory_stats["factory_rows"]))
    
    special_building_stats = build_special_building_statistics(api_data)
    print("Статистика по спецзданиям построена.")
    print("Спецзданий:", len(special_building_stats["special_building_rows"]))
    
    warehouse_stats = build_warehouse_statistics(api_data, item_id_to_name)
    print("Статистика по складам построена.")
    print("Складов:", len(warehouse_stats["warehouse_rows"]))
    
    production_balance = build_production_balance(mine_stats, factory_stats)
    print("Расчёт производства построен.")
    print("Ресурсы в балансе", len(production_balance["balance_rows"]))

market_price_by_resource = build_market_price_map(api_data)

print("Рыночные ставки загружены.")
print("Ресурсов с рыночными ставками:", len(market_price_by_resource))

daily_profit_report = build_daily_profit_report(
    production_balance=production_balance,
    market_price_by_resource=market_price_by_resource,
    factory_stats=factory_stats,
    special_building_stats=special_building_stats,
)

print("Расчёт чистой прибыли (оценка) построен.")
print("Логистика:", f"{daily_profit_report['logistics_percent'] * 100:.2f}%")
print("Итоговая чистая прибыль (оценка):", round(daily_profit_report["total_net_profit_day"], 2))

    profit_stats = calculate_profit(
    production_per_day,
    consumption_per_day,
    market_prices,
    logistics_percent=15
    )

    wb = Workbook()
    default_sheet = wb.active
    wb.remove(default_sheet)

    build_mine_workbook_part(wb, mine_stats)
    build_buildings_workbook_part(
    wb,
    factory_stats,
    special_building_stats,
    warehouse_stats
    )
    
    build_production_balance_sheet(wb, production_balance)

    ws_profit = wb.create_sheet("Profit")

ws_profit.append(["Income per day", profit_stats["income"]])
ws_profit.append(["Expenses per day", profit_stats["expenses"]])
ws_profit.append(["Net profit (estimate)", profit_stats["net_profit"]])

    output_dir = Path("E:/RG Data API/")
    output_dir.mkdir(exist_ok=True)
    archive_old_reports(output_dir)
    print("Статистика по шахтам построена.")
    print("Ресурсов шахт:", len(mine_stats["summary_rows"]))

    print("Данные загружены.")
    print("Ключи api_data:", list(api_data.keys()))

    output_dir = Path("E:/RG Data API/")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print(f"Тестовый запуск завершён: {timestamp}")
    
    filename = f"rg_report_{timestamp}.xlsx"
    filepath = output_dir / filename
    
    wb.save(filepath)
    
    print("Файл отчёта создан:", filepath)

if __name__ == "__main__":
    main()
