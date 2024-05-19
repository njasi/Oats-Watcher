import os
from .SharedCamera import SharedCamera
from .MotionDetector import MotionDetector

CAMERA_MRL = os.environ["CAMERA_MRL"]

# try to make it an int for local 
try:
    CAMERA_MRL = int(CAMERA_MRL)
except:
    pass

# single shared camera for all of the code to use
CAMERA = SharedCamera(CAMERA_MRL)


def main():
    md = MotionDetector(None, CAMERA)
    md.launch()
