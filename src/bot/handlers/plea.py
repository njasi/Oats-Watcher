import os
from telegram import Update
from telegram.ext import ContextTypes
from helpers import load_config

PLEA_STRING = load_config("plea", config_path="data/messages.json")
OATS_CHAT_ID = os.environ["OATS_CHAT_ID"]


async def plea(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends the initial plea message
        note that this message gets sent to oats chat, not the chat the command was sent from
    """

    await context.bot.send_message(text=PLEA_STRING, chat_id=OATS_CHAT_ID)
