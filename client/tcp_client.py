import socket
import argparse
from PIL import Image
import io
import logging

from client.camera import Camera
from client.audio_player import AudioPlayer
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.DEBUG,
)
logger = logging.getLogger(__name__)


class TCPClient:
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument("--port", default=9090, type=int)
        parser.add_argument('--host', default='0.0.0.0', type=str)
        parser.add_argument('--recv_bsize', type=int, default=1024)

    def __init__(self, args):
        self.args = args
        self.socket = socket.socket()
        logger.info("Connection to {}:{}".format(self.args.host, self.args.port))
        self.socket.connect((self.args.host, self.args.port))
        logger.info("Connected")

    def send_img(self, img: Image):
        byte_stream = io.BytesIO()
        img.save(byte_stream, format=self.args.img_format)
        bytes = byte_stream.getvalue()
        self.send_bytes(bytes)

    def send_bytes(self, bytes):
        logger.debug("Send to server {} bytes".format(len(bytes)))
        self.socket.send(bytes)
        logger.debug("Send zero")
        self.send_zero()
        logger.debug("Send done")

    def send_zero(self):
        self.socket.send(''.encode())

    def get_response(self):
        datas = []
        while True:
            data = self.socket.recv(self.args.recv_bsize)
            if not data:
                break
            datas.extend(data)
        return datas


def main():
    parser = argparse.ArgumentParser()
    TCPClient.add_args(parser)
    Camera.add_args(parser)
    AudioPlayer.add_args(parser)

    args = parser.parse_args()

    client = TCPClient(args)
    camera = Camera(args)
    player = AudioPlayer(args)
    logger.info(vars(args))
    player.load_all_bg_sounds()

    for img in camera.loop():
        client.send_img(img)
        logger.debug("Waiting response from server")
        music_bytes = client.get_response()
        logger.debug("Response contains {} bytes".format(len(music_bytes)))
        player.play_sound_from_bytes(music_bytes)


if __name__=="__main__":
    main()
