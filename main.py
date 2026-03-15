from report_runner import build_and_send_report

def main():
    result = build_and_send_report()
    
    print("Отчёт успешно сформирован.")
    print("Файл:", result["file_path"])
    print ()
    print(result["summary_text"])
    
    
    
if __name__ == "__main__":
    main()