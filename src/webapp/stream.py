import os
import cv2
import logging
from flask import Flask, Response, render_template

HOSTNAME = os.environ["FLASK_HOSTNAME"]
PORT = os.environ["FLASK_PORT"]

from video import CAMERA

app = Flask(__name__)
logger = logging.getLogger(__name__)


def generate_frames():
    while True:
        frame = CAMERA.frame
        if frame is None:
            logger.debug("Camera frame was None")
            break
        else:
            _, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


def main():
    app.run(host=HOSTNAME, port=PORT, threaded=True)
