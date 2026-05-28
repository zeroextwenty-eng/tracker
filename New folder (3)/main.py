import asyncio
import websockets
import json
import aiohttp
import os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home():
    return "Webhook Monitor Online"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

WS_URL = "wss://neriumsearch.onrender.com/"
FREE_WEBHOOK = os.getenv('FREE_WEBHOOK')
PAID_WEBHOOK = os.getenv('PAID_WEBHOOK')
FREE_ROLE = os.getenv('FREE_ROLE')
PAID_ROLE = os.getenv('PAID_ROLE')

async def send_webhook(url, role_id, item):
    async with aiohttp.ClientSession() as session:
        payload = {
            "content": f"<@&{role_id}>",
            "embeds": [{
                "title": item.get("name", "New Item Found"),
                "url": item.get("link", ""),
                "color": 65280 if role_id == FREE_ROLE else 16711680,
                "fields": [
                    {"name": "Price", "value": str(item.get("price", "N/A")), "inline": True},
                    {"name": "Status", "value": "Free" if role_id == FREE_ROLE else "Paid", "inline": True}
                ],
                "footer": {"text": "Nerium Search Monitor"}
            }]
        }
        async with session.post(url, json=payload) as resp:
            return resp.status

async def monitor():
    while True:
        try:
            async with websockets.connect(WS_URL) as ws:
                while True:
                    data = await ws.recv()
                    item = json.loads(data)
                    price = str(item.get("price", "0")).lower()
                    
                    if price == "0" or "free" in price:
                        await send_webhook(FREE_WEBHOOK, FREE_ROLE, item)
                    else:
                        await send_webhook(PAID_WEBHOOK, PAID_ROLE, item)
        except Exception:
            await asyncio.sleep(5)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    asyncio.run(monitor())
