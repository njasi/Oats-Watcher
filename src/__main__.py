import time
import dotenv
import logging
import threading

dotenv.load_dotenv()
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)


# init database & camera
import video
import database
import webapp
import bot


def main():
    # init the bot app so we can import it elsewhere
    bot.init()

    # start the webapp in its own thread
    threading.Thread(target=webapp.main).start()

    # when the camera first opens it is quite volitile,
    # so wait a bit before we do the motion detector
    time.sleep(5)
    video.main()

    # then start the bot
    bot.start()


if __name__ == "__main__":
    main()
