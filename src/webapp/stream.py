import os
import cv2
import logging
from flask import Flask, request, Response, render_template

HOSTNAME = os.environ["FLASK_HOSTNAME"]
PORT = os.environ["FLASK_PORT"]

from video import CAMERA

app = Flask(__name__)
logger = logging.getLogger(__name__)


def check_auth(username, password):
    """Check if a username/password combination is valid."""
    return username == os.environ["FLASK_USERNAME"] and password == os.environ["FLASK_PASSWORD"]

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    """Decorator to prompt for username and password."""
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


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
@requires_auth
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


def main():
    app.run(host=HOSTNAME, port=PORT, threaded=True)
