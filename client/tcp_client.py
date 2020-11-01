import socket
import argparse
from PIL import Image
import io
import logging

from client.camera import Camera
from client.audio_player import AudioPlayer
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.INFO,
)
logger = logging.getLogger(__name__)


class TCPClient:
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument("--port", default=9090, type=int)
        parser.add_argument('--host', default='0.0.0.0', type=str)
        parser.add_argument('--recv_bsize', type=int, default=1024)
        parser.add_argument('--img_size', type=str, default='100,100')
        parser.add_argument('--img_mode', type=str, default='RGB')
        parser.add_argument('--img_format', type=str, default='jpeg')
        parser.add_argument('--tmp_dir', type=str, default='tmp')
        parser.add_argument('--no_debug', action='store_true', default=False)

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
        self.socket.send(bytes)
        self.send_zero()

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
    player.all_minuses()

    for img in camera.loop():
        client.send_img(img)
        music_bytes = client.get_response()
        logger.info('Bytes len is {}'.format(len(music_bytes)))
        player.play_sound_from_bytes(music_bytes)


if __name__=="__main__":
    main()
