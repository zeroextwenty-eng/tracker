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
FREE_WEBHOOK = "https://discord.com/api/webhooks/1509514636968333362/EbisfRIBwpz7MwqdOL7sD22OPzo_WpYKPLkjqTUNC-5LHcxgrpm7XIgLsDaA_aevgng4"
PAID_WEBHOOK = "https://discord.com/api/webhooks/1509514722297253920/FD_wJKwOoOFWfbHh4DWGKPzAYu75TxERq3AwYRmZBgREHFzVs6Zkzv4TDLNuf2IV7Bld"

FREE_ROLE = "1509514820913729557"
PAID_ROLE = "1509514936165076992"

async def send_webhook(url, role_id, item):
    async with aiohttp.ClientSession() as session:
        payload = {
            "content": f"<@&{role_id}>",
            "embeds": [{
                "title": item.get("name", "New Item"),
                "url": item.get("link", ""),
                "color": 65280 if role_id == FREE_ROLE else 16711680,
                "fields": [
                    {"name": "Price", "value": str(item.get("price", "N/A")), "inline": True},
                    {"name": "Source", "value": "Nerium Search", "inline": True}
                ],
                "footer": {"text": "Nerium Search Monitor"}
            }]
        }
        await session.post(url, json=payload)

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
        except:
            await asyncio.sleep(5)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    asyncio.run(monitor())