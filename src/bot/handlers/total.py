import os
from telegram import Update
from telegram.ext import ContextTypes
from helpers import load_config
from database.Users import Users

TOTAL_STRING = load_config("total", config_path="data/messages.json")
NONE_STRING = load_config("none", config_path="data/messages.json")
GOAL = os.environ["DONATION_GOAL"]


async def total(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays total donation information, see the string above."""

    tot = Users.get_total_donations()

    if tot <= 0:
        await update.effective_message.reply_html(NONE_STRING)
        return

    await update.effective_message.reply_html(TOTAL_STRING.format(tot))
