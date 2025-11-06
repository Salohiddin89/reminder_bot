# keep_alive.py
from flask import Flask
from threading import Thread
import os
import requests
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def ping_self():
    url = os.environ.get("RENDER_EXTERNAL_URL") or "https://reminder-bot.onrender.com"
    while True:
        try:
            requests.get(url)
        except:
            pass
        time.sleep(300)

def keep_alive():
    Thread(target=run).start()
    Thread(target=ping_self).start()
