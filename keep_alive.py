from flask import Flask
from threading import Thread
import requests
import os

import main  # main.py dagi bot ishga tushadi

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def ping_self():
    import time
    url = os.environ.get("RENDER_EXTERNAL_URL") or "https://reminder-bot.onrender.com"
    while True:
        try:
            requests.get(url)
        except:
            pass
        time.sleep(300)  # har 5 daqiqada ping

if __name__ == "__main__":
    Thread(target=run).start()
    Thread(target=ping_self).start()
