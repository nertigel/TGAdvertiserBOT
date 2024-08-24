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
        "message_limit": 20,
        "message_text": "Auto Telegram Chat Advertiser by @nertigel",
        "message_image": "",
        "chats": []
    }
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=4)

def create_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def list_sessions():
    session_files = Path("sessions").glob("*.session")
    sessions = [session_file.stem for session_file in session_files]

    if not sessions:
        print("No sessions found in the 'sessions' folder")
    else:
        print("Available sessions:")
        for index, session_name in enumerate(sessions, start=0):
            print(f"[{index}] {session_name}")
    
    return sessions

async def send_messages(client, config):
    chats = config["chats"]
    message_text = config["message_text"]
    message_image = config["message_image"]
    message_limit = config.get("message_limit", 20)
    message_count = 0
    
    while message_count < message_limit:
        for chat in chats:
            try:
                await asyncio.sleep(2)
                print(f"Sending message #{message_count} at {chat}...")
                if message_image and Path(message_image).exists():
                    await client.send_photo(chat, photo=message_image, caption=message_text)
                else:
                    await client.send_message(chat, message_text)

                message_count += 1
                if message_count >= message_limit:
                    break
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"Failed to send message to {chat}: {e}")

        await asyncio.sleep(config["message_interval"])

async def main():
    if not Path('config.json').exists():
        create_default_config()
    
    create_dir_if_not_exists("sessions")
    config = load_json_cfg()

    sessions = list_sessions()
    if sessions:
        session_choice = input("Enter the session name or select by number: ")
        
        if session_choice.isdigit():
            session_name = sessions[int(session_choice)]
        else:
            session_name = session_choice
    else:
        session_name = input("No sessions available. Enter a new session name: ")

    while True:
        if Path(f"sessions/{session_name}.session").exists():
            print(f"Using already created {session_name}.session")
        else:
            print("Creating new session...")
        
        async with Client(session_name, workdir="sessions", api_id=config["api_id"], api_hash=config["api_hash"]) as app:
            if config["chats"]:
                await send_messages(app, config)
            else:
                print("Please fill your chats variable at config.json!")

        print(f"Finished working with {session_name}.session")

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())