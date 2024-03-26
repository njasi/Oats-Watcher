from .SharedCamera import SharedCamera
from .MotionDetector import MotionDetector

# single shared camera for all of the code to use

CAMERA = SharedCamera("udp://@:1234")


def main():
    md = MotionDetector(None, CAMERA)
    md.launch()
