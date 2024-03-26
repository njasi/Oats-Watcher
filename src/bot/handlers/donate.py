import os

from random import choice
from telegram import Update
from telegram.ext import ContextTypes

from database.Users import Users
from helpers import load_config, usage_generator, update_config

DONATION_MESSAGES = load_config("donate", config_path="data/messages.json")
GOAL_MESSAGES = load_config("goals", config_path="data/messages.json")
OATS_CHAT_ID = os.environ["OATS_CHAT_ID"]
GOAL = os.environ["DONATION_GOAL"]


usage = usage_generator(
    "<b>Usage:</b>\n/donate [amount]\n\t\tamount: positive float amount to donate.\n\t\tIf no amount is given, displays how much you have donated."
)


async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    allow users to donate
    """
    global GOAL_MESSAGES
    amount = 0

    # validate arguments
    if not len(context.args) < 2:
        await usage(update, context)
        return

    if len(context.args) == 0:
        donation = Users.get_donation(update.effective_user)
        await update.effective_message.reply_html(
            "You have pledged ${0:.2f}.".format(donation),
            reply_to_message_id=update.effective_message.id,
        )
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
    Users.donation(update.effective_user, amount)

    # pick random donation message to send
    await update.effective_message.reply_html(
        choice(DONATION_MESSAGES), reply_to_message_id=update.effective_message.id
    )

    # check if any goals have been reached
    percent = Users.get_total_donations() / GOAL
    change = False
    for goal in GOAL_MESSAGES:
        if not goal["percent"] >= percent and not goal["reached"]:
            await context.bot.send_message(text=goal["message"], chat_id=OATS_CHAT_ID)

            goal["reached"] = True
            change = True

    # update the goals
    if change:
        GOAL_MESSAGES = update_config(
            GOAL_MESSAGES, key="goals", config_path="./data/messages.json"
        )
