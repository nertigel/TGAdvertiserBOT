import asyncio
import json
import os
import re
from pathlib import Path
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.enums import ChatType

CONFIG_FILE = "config.json"

# Load data from config.json
def load_json_cfg():
    with open(CONFIG_FILE, encoding='utf-8') as f:
        return json.load(f)

# Create a default config.json file in-case it does not exist
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
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=4)

# Create directory if does not exist
def create_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Iterate through the sessions folder and find all .session files
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

# Remove emojis from a provided string
def remove_emojis(text):
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

# Get all available groups for posting from the .session and print as a table
async def get_available_groups(client):
    id_width = 20
    name_width = 64
    username_width = 20

    # Print the header
    print(f"{'ID':<{id_width}} | {'Name':<{name_width}} | {'Username':<{username_width}}")
    print("-" * (id_width + name_width + username_width + 6))  # Separator line

    available_groups = []
    try:
        async for dialog in client.get_dialogs():
            await asyncio.sleep(0.3)
            if dialog.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
                continue
            if not dialog.chat.permissions.can_send_messages:
                continue
            
            chat_id = str(dialog.chat.id)
            username = str(dialog.chat.username) or None
            title = remove_emojis(str(dialog.chat.title)[:name_width])
            if username not in (None, "None"):
                available_groups.append(username)
                print(f"{chat_id:<{id_width}} | {title:<{name_width}} | {username:<{username_width}}")

    except FloodWait as e:
        print(f"You have been flooded, waiting {e.value}s")
        await asyncio.sleep(e.value)
    except Exception as e:
        print(f"Failed to print available groups: {e}")

    return available_groups

async def send_messages(client, config, chats):
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
                print(f"You have been flooded, waiting for {e.value}s")
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"Failed to send message to {chat}: {e}")

        print(f"Finished sending {message_count} messages at {chat}, waiting {config['message_interval']}s")
        await asyncio.sleep(config["message_interval"])

async def main():
    if not Path(CONFIG_FILE).exists():
        create_default_config()
    
    create_dir_if_not_exists("sessions")

    config = load_json_cfg()
    chats = config["chats"]
    while True:
        sessions = list_sessions()
        if sessions:
            session_choice = input("Enter the session name or select by number: \n")
            
            if session_choice.isdigit():
                try:
                    session_name = sessions[int(session_choice)]
                except IndexError:
                    session_name = input("Could not index session. Enter a new session name: \n")
            else:
                session_name = session_choice
        else:
            session_name = input("No sessions available. Enter a new session name: \n")

        if Path(f"sessions/{session_name}.session").exists():
            print(f"Using already created {session_name}.session")
        else:
            print("Creating a new session...")
        
        async with Client(session_name, workdir="sessions", api_id=config["api_id"], api_hash=config["api_hash"]) as app:
            get_auto = input("Enter [1] to automatically get available groups or nothing to continue: \n")
            if int(get_auto) == 1:
                chats = await get_available_groups(app)

            if chats:
                await send_messages(app, config, chats)
            else:
                print(f"No chats! Please fill your chats variable at {CONFIG_FILE}!")

        print(f"Finished working with {session_name}.session")

# Run the bot
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError): 
        print("File closed.")