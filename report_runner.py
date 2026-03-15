from pathlib import Path
from datetime import datetime

from openpyxl import Workbook

from config import OUTPUT_DIR, BOT_TOKEN, CHAT_ID

from api_client import fetch_all_api_data
from item_mappings import build_item_id_to_name
from mine_stats import build_mine_statistics
from factory_stats import build_factory_statistics
from special_buildings_stats import build_special_building_statistics
from warehouse_stats import build_warehouse_statistics
from market_rates import build_market_price_map
from production_balance import build_production_balance
from profit_calculator import build_daily_profit_report

from mine_excel_builder import build_mine_workbook_part
from buildings_excel_builder import build_buildings_workbook_part
from production_balance_excel_builder import build_production_balance_sheet
from profit_calculator_excel_builder import build_profit_summary_sheet
from telegram_sender import send_telegram_message, send_telegram_document



def format_number(value: float) -> str:
    return f"{value:,.2f}".replace(",", " ")



def build_report() -> dict:
    """
    Формирует полный отчёт и возвращает:
    {
        "file_path": Path,
        "summary_text": str,
        "daily_profit_report": dict,
    }
    """
    
    #1. Получение данных API
    api_data = fetch_all_api_data()
    print("Данные API загружены.")
    print("Заводы:", len(api_data["factories"]))
    print("Шахты:", len(api_data["mines"]))
    print("Склады:", len(api_data["warehouses"]))
    print("Спецздания:", len(api_data["special_buildings"]))
    print("Справочник предметов:", len(api_data["items_catalog"]))
    print("Рыночные ставки:", len(api_data["market_rates"]))
    
    #2. Словарь имён
    item_id_to_name = build_item_id_to_name(api_data)
    
    #3. Расчёты
    mine_stats = build_mine_statistics(api_data, item_id_to_name)
    factory_stats = build_factory_statistics(api_data, item_id_to_name)
    special_building_stats = build_special_building_statistics(api_data)
    warehouse_stats = build_warehouse_statistics(api_data, item_id_to_name)
    
    production_balance = build_production_balance(mine_stats, factory_stats)
    
    market_price_by_resource = build_market_price_map(api_data)
    
    daily_profit_report = build_daily_profit_report(
        production_balance=production_balance,
        
        market_price_by_resource=market_price_by_resource,
        factory_stats=factory_stats,
        special_building_stats=special_building_stats,
        )
    
    #4. Excel
    wb = Workbook()
    default_sheet = wb.active
    wb.remove(default_sheet)
    
    build_mine_workbook_part(wb, mine_stats)
    
    build_buildings_workbook_part(
        wb,
        factory_stats,
        special_building_stats,
        warehouse_stats,
        )
    
    build_production_balance_sheet(wb, production_balance)
    build_profit_summary_sheet(wb, daily_profit_report)
    
    #5. Сохранение
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = output_dir / f"Отчёт_Resources_Game_{timestamp}.xlsx"
    
    wb.save(file_path)
    
    #6. Сводка для Telegram / консоли
    summary_text = (
        "Новый отчёт Resources Game готов.\n\n"
        f"Итоговая чистая прибыль (оценка): {format_number(daily_profit_report['total_net_profit_day'])} €\n"
        f"Доход по товарам / сутки {format_number(daily_profit_report['factory_income_day'])} €\n"
        f"Расход по ресурсам / сутки: {format_number(daily_profit_report['mine_expense_day'])} €\n"
        f"Стоимость запуска заводов / сутки: {format_number(daily_profit_report['total_credits_cost_per_day'])} €\n"
        f"Логистика: {daily_profit_report['logistics_percent'] * 100:.2f}%"
    )
    
    return {
        "file_path": file_path,
        "summary_text": summary_text,
        "daily_profit_report": daily_profit_report,
    }

def build_and_send_report() -> dict:
    result = build_report()
    send_telegram_message(BOT_TOKEN, CHAT_ID, result["summary_text"])
    
    send_telegram_document(
        BOT_TOKEN,
        CHAT_ID,
        str(result["file_path"]),
        caption="Новый отчёт Resources Game"
    )
    
    return result
    
    
    
    if __name__ == "__main__":
        result = build_report() 
        
        print("Отчёт успешно сформирован.")
        print("файл:", result["summary_text"])