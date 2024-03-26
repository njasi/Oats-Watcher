from telegram import Update
from telegram.ext import ContextTypes
from helpers import load_config

START_STRING = load_config("about", config_path="data/messages.json")


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Displays the about string (which is the start string rn)
    """

    await update.effective_message.reply_html(START_STRING)
