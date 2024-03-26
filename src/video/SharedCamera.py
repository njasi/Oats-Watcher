import cv2
import time
import logging
import threading


class SharedCamera:
    """
    Basic interface for connecting to a udp stream & sharing the video frames

    (as we can only have one video capture bind to the udp resource)
    also simply consumes less resources, as reading is more intensive than just sharing
    """

    def __init__(self, url: str):
        self.url = url
        self._logger = logging.getLogger(f"{__name__}({self.url})")

        self._frame = None
        self._camera = None
        self._alive = True
        self._lock = threading.Lock()

        try:
            self._connect()
            self._thread = threading.Thread(target=self._read)
            self._thread.start()
        except:
            self._reconnect(cb=self._read)

    def _connect(self):
        """
        Connect to the resource
        """
        self._logger.info(f"Connecting...")
        camera = cv2.VideoCapture(self.url)

        if camera is None or not camera.isOpened():
            # for some reason cv2 Vid Capture doesnt raise error on error,
            # just prints it and waits till later to err...
            self._camera = None
            raise Exception("Error connecting")

        self._camera = camera
        self._logger.info(f"Connected")

    def _reconnect(self, cb=None):
        """
        Attempt to connect to the resource over and over in another thread
        """
        self._thread = threading.Thread(
            target=self._reconnect_worker, kwargs={"cb": cb}
        )
        self._thread.start()

    def _reconnect_worker(self, wait=10, cb=None):
        """
        Worker thread for reconnecting
        """

        self._logger.info(f"Starting reconnection worker...")
        while self._alive:
            try:
                self._connect()
                break
            except Exception:
                self._logger.warn(f"Error connecting, retrying in {wait} seconds...")
            time.sleep(wait)

        if cb is not None:
            cb()

    def _read(self):
        """
        Worker function, read the incoming frames and save them
        """
        self._logger.info("Started _read worker thread")
        while self._alive:
            success, frame = self._camera.read()
            with self._lock:
                if not success:
                    self._logger.debug("_camera read was unsuccessful.")
                    self._frame = None
                    self._camera = None
                    break
                else:
                    self._frame = frame

        # try to reconnect if still live, relaunch read on success
        if self._alive:
            self._reconnect(cb=self._read)

    def close(self):
        """
        Close the camera instance

            - worker thread
            - cv2 videocapture camera
        """
        self._logger.debug("Closing camera resources.")

        self._alive = False
        self._thread.join()

        if self._camera is not None:
            self._camera.release()

    @property
    def frame(self):
        """
        The most recent frame from the resource
        """
        with self._lock:
            if self._frame is None:
                return None
            return self._frame

    @property
    def connected(self):
        """
        Check if the shared camrea is connected
        """
        return self._camera is not None
