import cv2
import numpy as np

from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

from database.Users import Users
from video import CAMERA


from helpers import load_config

CAPTION = load_config("caption", "./data/messages.json")
CAPTION_HAPPY = load_config("caption-happy", "./data/messages.json")


async def view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends a live view of the oats (or black screen if not connected)
    """

    image = CAMERA.frame
    text = ""
    if image is None:
        image = depression()
        text = CAPTION
    else:
        image = live_view(image)
        text = CAPTION_HAPPY

    # update the user's view count
    Users.view(update.effective_user)

    image_bytes = cv2.imencode(".jpg", image)[1].tobytes()

    # TODO if there has been alot of spam from someone dont send to save resources
    await update.effective_message.reply_photo(caption=text, photo=image_bytes)


def live_view(image, text="H I G H   D E F I N I T I O N   O A T S"):
    # add text to black image
    cv2.putText(
        image,
        text,
        (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (0, 0, 0xFF),
        2,
    )

    cv2.putText(
        image,
        datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, image.shape[0] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 0xFF),
        1,
    )

    return image


def depression():
    image = np.zeros((1080, 1920, 3), np.uint8)
    text = "H I G H   D E F I N I T I O N   O A T S   S A D N E S S   D E T E C T E D"
    return live_view(image, text=text)
