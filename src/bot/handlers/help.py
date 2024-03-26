from telegram import Update
from telegram.ext import ContextTypes

HELP_STRING = """<b>Commands:</b>
/about:
    Learn about Oats Watcher
/donate [amount]
    Donate to help Oats Watcher, displays how much you have donated if no amount is given.
/undonate amount
    Take back donation money from Oats Watcher
/view:
    View the oats
/total
    See the total donation count
/leaderboard [page]:
    See the given page (default 1) of the oats viewing leaderboard
/venmo:
    Oat Watcher's venmo to donate to
/help:
    ...
"""


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Displays help message, see the string above.
    """

    await update.effective_message.reply_html(HELP_STRING)


"""
about - /about: Learn about Oats Watcher
donate - /donate amount: Donate to help Oats Watcher
undonate - /undonate amount: Take back donation money from Oats Watcher
view - /view: View the oats
total - /total: See the total donation count
leaderboard - /leaderboard [page]: See the given page (default 1) of the oats viewing leaderboard
help - /help: ...
"""
