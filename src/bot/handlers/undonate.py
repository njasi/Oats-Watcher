from telegram import Update
from telegram.ext import ContextTypes
from random import choice

from helpers import load_config, usage_generator
from database.Users import Users


UNDONATION_MESSAGES = load_config("undonate", config_path="data/messages.json")
THEFT_MESSAGES = load_config("theft", config_path="data/messages.json")
usage = usage_generator(
    "<b>Usage:</b>\n/undonate amount\n\t\tamount: positive float amount to undonate."
)


async def undonate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    allow users to undonate
    """
    global GOAL_MESSAGES
    amount = 0

    # validate arguments
    if not len(context.args) == 1:
        await usage(update, context)
        return
    try:
        amount = float(context.args[0])
        if amount <= 0:
            await usage(update, context)
            return
    except:
        await usage(update, context)
        return

    # make the donation
    res = Users.donation(update.effective_user, -1 * amount)

    if res:
        # successful undonation
        await update.effective_message.reply_html(
            choice(UNDONATION_MESSAGES), reply_to_message_id=update.effective_message.id
        )
    else:
        await update.effective_message.reply_html(
            choice(THEFT_MESSAGES), reply_to_message_id=update.effective_message.id
        )
