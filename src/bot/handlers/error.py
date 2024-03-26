import os
import html
import json
import logging
import tempfile
import datetime
import traceback
from telegram import Update
from telegram.constants import ParseMode, MessageLimit
from telegram.ext import ContextTypes


DEVELOPER_CHAT_ID = os.environ["ADMIN_CHAT_ID"]
logger = logging.getLogger(__name__)


async def error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Log the error and send a telegram message to notify the developers.
    """
    logger.error("Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    # Build error message with
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # send if its below the limit
    if len(message) < MessageLimit.MAX_TEXT_LENGTH:
        await context.bot.send_message(
            chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
        )
        return

    with tempfile.TemporaryFile("r+") as file:
        file.write(message)
        file.flush()
        file.seek(0)

        time_str = str(datetime.now()).replace(" ", "_")

        await context.bot.send_document(
            caption="An exception was raised while handling an update.\n\nHowever it was too long to send as a message, check the logs or the attached file.",
            parse_mode=ParseMode.HTML,
            chat_id=DEVELOPER_CHAT_ID,
            document=file,
            filename=f"ERROR_{time_str}.html",
        ),
