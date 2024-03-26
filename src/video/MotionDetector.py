import os
import cv2
import time
import logging
import asyncio
import imageio
import telegram
import datetime
import threading
from .SharedCamera import SharedCamera

logger = logging.getLogger(__name__)

OATS_CHAT_ID = os.environ["OATS_CHAT_ID"]


def grab_contours(cnts):
    """
    taken directly from imutils source,
    since its the only function I want to use

    no need to waste space
    """
    # if the length the contours tuple returned by cv2.findContours
    # is '2' then we are using either OpenCV v2.4, v4-beta, or
    # v4-official
    if len(cnts) == 2:
        cnts = cnts[0]

    # if the length of the contours tuple is '3' then we are using
    # either OpenCV v3, v4-pre, or v4-alpha
    elif len(cnts) == 3:
        cnts = cnts[1]

    # otherwise OpenCV has changed their cv2.findContours return
    # signature yet again and I have no idea WTH is going on
    else:
        raise Exception(
            (
                "Contours tuple must have length 2 or 3, "
                "otherwise OpenCV changed their cv2.findContours return "
                "signature yet again. Refer to OpenCV's documentation "
                "in that case"
            )
        )

    # return the actual contours array
    return cnts


class MotionDetector:
    def __init__(
        self,
        loop,
        camera: SharedCamera,
        limit_fps=10,
        min_area=100,
        blur_size=(21, 21),
        ignore=[],
    ) -> None:
        self._min_area = min_area
        self._blur_size = blur_size
        self._camera = camera

        self._last_motion = 0
        self._prev_gray = None
        self._prev_frame = None
        self._frames = []

        # array of areas to be ignored in the detection workers:
        #  ex [((0,0),(100,100)), ...]
        self.ignore = ignore

        # set an fps limit, is high rn cause we're trying out the gif mode
        self._fps = limit_fps
        self._rate = 1 / self._fps

        # worker thread stuff
        self._thread = None
        self._alive = True

        # gotta import here cause it aint inited when this module is created
        from bot import application, loop

        self._bot = application.bot
        self._loop = loop

    def add_frame():
        """
        add a frame to the queue of frames to be processed
        """
        # TODO, would be better than just iterating through endlessly

    def launch(self):
        self._alive = True
        self._thread = threading.Thread(target=self._motion_worker)
        self._thread.start()

    def close(self):
        self._alive = False
        self._thread.join()

    def _label_image(
        self, image, text="O A T S   M O T I O N   D E T E C T E D", date=True
    ):
        cv2.putText(
            image,
            text,
            (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 0, 0xFF, 255),
            2,
        )
        if date:
            cv2.putText(
                image,
                datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, image.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0xFF, 255),
                1,
            )
        return image

    def _motion_worker(self, empty_frame_wait=10, motion_buffer=1):
        logger.info("Launched motion detection worker")
        # loop over the frames of the video
        prev_time = time.time()
        while self._alive:

            # sleep to match the target fps
            delta_t = time.time() - prev_time
            if 0 < delta_t < self._rate:
                time.sleep(self._rate - delta_t)
            prev_time = time.time()

            # busy wait for new frame
            while self._prev_frame is self._camera.frame:
                pass

            # grab the current frame
            frame = self._camera.frame
            self._prev_frame = frame

            if frame is None:
                logger.info(
                    f"Camera has no frame, trying again in {empty_frame_wait} seconds."
                )
                time.sleep(empty_frame_wait)
                continue

            # prepare for diff processing
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, self._blur_size, 0)

            if self._prev_gray is None:
                self._prev_gray = gray

            # take diff, threshold it, & dilate
            threshold = cv2.dilate(
                cv2.threshold(
                    cv2.absdiff(self._prev_gray, gray), 25, 0xFF, cv2.THRESH_BINARY
                )[1],
                None,
                iterations=2,
            )

            # save frame for next round
            self._prev_gray = gray

            # patch over the ignore areas
            for dead_space in self.ignore:
                cv2.rectangle(
                    threshold, dead_space[0], dead_space[1], (0, 0xFF, 0), cv2.FILLED
                )

            # find the cotours & iterate over them
            cnts = cv2.findContours(
                threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            motion = False

            frame_copy = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2BGRA)

            for i, cnt in enumerate(grab_contours(cnts)):
                if cv2.contourArea(cnt) >= self._min_area:
                    # (x, y, w, h) = cv2.boundingRect(cnt)
                    cv2.drawContours(
                        frame_copy,
                        [cnt],
                        i * -1,
                        color=(0, 0xFF, 0, 50),
                        thickness=cv2.FILLED,
                    )
                    # cv2.rectangle(frame_copy, (x, y), (x + w, y + h), (0, 0xFF, 0), 2)
                    motion = True

            if motion:
                logger.info(f"Oats Motion Detected")
                labeled = self._label_image(frame_copy)

                # keeping this like this for if i wanna switch back to the gif thing
                self.on_motion(labeled)
                self._last_motion = time.time()

            else:
                if time.time() - self._last_motion < motion_buffer:
                    self.on_motion(self._label_image(frame_copy))
                    continue
                if len(self._frames) > 0:
                    self.on_motion_end()

    def _oat_recog_worker():
        """
        TODO object recognition specifically for oats lol
        """
        pass

    def _scale_frame(self, image, scale=2):

        # Get the original dimensions
        height, width = image.shape[:2]

        # Double the dimensions
        new_height = height * scale
        new_width = width * scale

        return cv2.resize(image, (new_width, new_height))

    def _timestamp_str(self):
        return f"<b>O A T S   M O T I O N   D E T E C T E D</b>\n\n{datetime.datetime.now().strftime('%A %d %B %Y %I:%M:%S%p')}"

    async def _make_gif(self, frames):
        """
        Let all the actual work be done in the telegram loop lol

        was like this so we could have the image not overwritten but...
        """

        file_path = f"data/temp/movement_{time.time()}.gif"
        try:
            # with imageio.get_writer(file_path, mode="I", disposal) as writer:
            for i in range(len(frames)):
                # TODO is there a way to make telegram not compress the gif into
                #      oblivion, thought scaling would possibly work ig not tho
                frames[i] = cv2.cvtColor(frames[i], cv2.COLOR_BGRA2RGBA)

            imageio.mimsave(
                file_path,
                frames,
                format="GIF",
                fps=10,
                loop=0,
            )

            with open(file_path, "rb") as gif:
                thumb = cv2.imencode(".png", frames[0])[1].tobytes()
                await self._bot.send_animation(
                    chat_id=OATS_CHAT_ID,
                    thumbnail=thumb,
                    animation=gif,
                    caption=self._timestamp_str(),
                    parse_mode="HTML",
                )

        finally:
            try:
                os.remove(file_path)
            except:
                pass

    def on_motion_end(self):
        logger.info(f"Sending Oats Motion To {OATS_CHAT_ID}")

        try:
            if len(self._frames) == 1:

                img_bytes = cv2.imencode(".jpg", self._frames[0])[1].tobytes()
                self._loop.call_soon_threadsafe(
                    asyncio.ensure_future,
                    self._bot.send_photo(
                        photo=img_bytes,
                        caption=self._timestamp_str(),
                        chat_id=OATS_CHAT_ID,
                        parse_mode="HTML",
                    ),
                )
            elif len(self._frames) > 1:
                self._loop.call_soon_threadsafe(
                    asyncio.ensure_future, self._make_gif([*self._frames])
                )
        except:
            pass
        finally:
            self._frames = []

    def on_motion(self, image):
        """
        Called when motion is detected
        """
        self._frames += [image]
