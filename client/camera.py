from io import BytesIO
import time
import logging
from picamera import PiCamera
from PIL import Image
import os
import argparse

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.DEBUG,
)
logger = logging.getLogger(__name__)


class Camera:
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--loop', type=int, default=5000, help='Capture photo every --loop ms')
        parser.add_argument('--img_size', type=str, default='100,100') 
        parser.add_argument('--img_format', type=str, default='jpeg')
        parser.add_argument('--tmp_dir', type=str, default='tmp')

    def __init__(self, args):
        logger.info("Init camera")
        self.args = args
        self.camera = PiCamera()
        self.image_size = [int(s) for s in args.img_size.split(',')]
        self.camera.resolution = tuple(self.image_size)
        self.camera.rotation = 180

        # self.camera.start_preview()

    def capture(self, debug=True):
        logger.info("Capture image")
        stream = BytesIO()
        self.camera.capture(stream, format='jpeg')
        stream.seek(0)
        img = Image.open(stream)
        if debug:
            os.makedirs(self.args.tmp_dir, exist_ok=True)
            t = str(time.time())
            name = os.path.join(self.args.tmp_dir, t + ".jpeg")
            logger.info("Saving  image to {}".format(name))
            img.save(name)
        return img

    def loop(self, debug=True):
        while True:
            img = self.capture(debug=debug)
            yield img
            time.sleep(self.args.loop/1000)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    Camera.add_args(parser)

    args = parser.parse_args()

    camera = Camera(args)

    for img in camera.loop():
        pass

