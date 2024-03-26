from telegram import Update
from telegram.ext import ContextTypes
from helpers import load_config
from database.Users import Users
from helpers import usage_generator

TOTAL_STRING = load_config("total", config_path="data/messages.json")
NO_VIEWS_STRING = load_config("no_views", config_path="data/messages.json")


usage = usage_generator(
    "<b>Usage:</b>\n/leaderboard [page]\n\t\tpage: page of the leaderboard to view, int."
)


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    sends the leaderboard of total user oat views
    """

    page = 1

    if len(context.args) > 1:
        await usage(update, context)
        return
    if len(context.args) == 1:
        try:
            page = int(context.args[0])
        except:
            await usage(update, context)
            return

    leaderboard = Users.views_to_message(page=page - 1)

    if leaderboard == False:
        leaderboard = NO_VIEWS_STRING

    await update.effective_message.reply_html(leaderboard)
