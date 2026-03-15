import requests


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": text,
    }
    
    response = requests.post(url, data=data, timeout=30)
    response.raise_for_status()
    
    
    
def send_telegram_document(
    bot_token: str,
    chat_id: str,
    file_path: str,
    caption: str = ""
) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    
    with open(file_path, "rb") as file:
        files = {
            "document": file
        }
        
        data = {
            "chat_id": chat_id,
            "caption": caption,
        }
        
        response = requests.post(
        url,
        data=data,
        files=files,
        timeout=120
    )
    response.raise_for_status()