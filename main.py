import json
import os
from pyrogram import Client
from pyrogram.errors import FloodWait
import asyncio
from pathlib import Path

def load_json_cfg():
    with open('config.json', encoding='utf-8') as f:
        return json.load(f)

def create_default_config():
    default_config = {
        "api_id": "",
        "api_hash": "",
        "message_interval": 120,
        "message_text": "Auto Telegram Chat Advertiser by @nertigel",
        "message_image": "",
        "chats": []
    }
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=4)

async def send_messages(client, config):
    chats = config["chats"]
    message_text = config["message_text"]
    message_image = config["message_image"]
    
    while True:
        for chat in chats:
            try:
                await asyncio.sleep(2)
                print(f"Sending message at {chat}...")
                if message_image and Path(message_image).exists():
                    await client.send_photo(chat, photo=message_image, caption=message_text)
                else:
                    await client.send_message(chat, message_text)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"Failed to send message to {chat}: {e}")

        await asyncio.sleep(config["message_interval"])

async def main():
    if not Path('config.json').exists():
        create_default_config()
    
    config = load_json_cfg()
    session_name = input("Enter the session name: ")
    
    async with Client(session_name, workdir="sessions", api_id=config["api_id"], api_hash=config["api_hash"]) as app:
        if config["chats"]:
            await send_messages(app, config)
        else:
            print("Please fill your chats variable at config.json!")

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
