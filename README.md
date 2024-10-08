# TGAdvertiserBOT for Telegram
This is a telegram user-bot based off the [Pyrogram](https://github.com/pyrogram/pyrogram) library in Python3. 

# How it works

This user-bot will send predefined messages at chats every certain amount of time automatically, as long as the user is a participant of the chat and has permissions to send a message.

# Installation

You can run this bot on your own, install the required lib by running this command: 

```bash
pip install pyrogram
```

# Configuration (config.json)

In the `config.json` file you will find `api_id` and `api_hash` variables, get your [API credentials from Telegram's official website](https://my.telegram.org/auth).

You can add an image that would be sent with the `message_text` as caption, for example `image_name.png`:
```json
"message_image": "image_name.png",
```

Now you can simply run the bot by running `main.py`
