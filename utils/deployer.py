import os
import requests

def deploy_to_telegram(game_name: str):
    files = {'document': open(f'games/{game_name}/game.py', 'rb')}
    requests.post(
        f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendDocument",
        files=files,
        data={"chat_id": YOUR_CHAT_ID}
    )
    print(f"🚀 {game_name} टेलीग्राम पर डेप्लॉय हुआ!")
