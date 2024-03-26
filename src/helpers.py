import json
from telegram import Update
from telegram.ext import ContextTypes


def load_config(key=None, config_path="./config.json"):
    """Load in the config file, or a var from the file"""
    with open(config_path) as file:
        data = json.load(file)
        if key is None:
            return data
        else:
            return data[key]


def update_config(value, key=None, config_path="./config.json"):
    """update the config file"""
    with open(config_path, "r+") as file:
        if key is None:
            json.dump(value, file, indent=4)
            return json.load(file)
        else:
            og = json.load(file)
            file.seek(0)
            og[key] = value
            json.dump(og, file, indent=4)
            return value


def usage_generator(text):
    """shortcut to making a usage message dispatcher"""

    async def usage_function(update, context):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode="HTML",
            reply_to_message_id=update.effective_message.id,
        )

    return usage_function
