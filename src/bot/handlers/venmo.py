from telegram import Update
from telegram.ext import ContextTypes
from helpers import load_config
from database.Users import Users

VENMO_STRING = """Amidst the unending darkness, your support could be the glimmer of hope I so desperately need. If you're willing to contribute and help me on this challenging journey, you can do so by following this link: https://venmo.com/u/njasi. The relentless isolation weighs heavy, and your donation could be the light in my world of shadows."""


async def venmo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    just send my venmo lol
    """
    await update.effective_message.reply_html(
        VENMO_STRING, disable_web_page_preview=True
    )
