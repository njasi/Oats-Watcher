import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


# import handlers
from .handlers.error import error
from .handlers.about import about
from .handlers.donate import donate
from .handlers.undonate import undonate
from .handlers.view import view
from .handlers.plea import plea
from .handlers.total import total
from .handlers.leaderboard import leaderboard
from .handlers.help import help
from .handlers.venmo import venmo


# load in the needed constants
TOKEN = os.environ["BOT_TOKEN"]

application = None
loop = None


def init() -> None:
    """init & run the bot."""
    global application, loop
    loop = asyncio.get_event_loop()
    application = Application.builder().token(TOKEN).build()

    # Register commands
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("donate", donate))
    application.add_handler(CommandHandler("undonate", undonate))
    application.add_handler(CommandHandler(["v", "view", "IWANTTHEOATS"], view))
    application.add_handler(CommandHandler("plea", plea))
    application.add_handler(CommandHandler("total", total))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("venmo", venmo))

    # the error handler
    application.add_error_handler(error)


def start() -> None:
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
