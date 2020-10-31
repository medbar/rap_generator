import socket
import argparse
import logging
import os
from PIL import Image
import time

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.INFO,
)
logger = logging.getLogger(__name__)


class RapGeneratorServer:
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument("--port", default=9090, type=int)
        parser.add_argument('--host', default='0.0.0.0', type=str)
        parser.add_argument('--clients_number', default=1, type=int)
        parser.add_argument('recv_bsize', type=int, default=1024)
        parser.add_argument('--img_size', type=str, default='100,100')
        parser.add_argument('--img_mode', type=str, default='RGB')
        parser.add_argument('--img_decoder_name', type=str, default='raw')
        parser.add_argument('--tmp_dir', type=str, default='tmp')
        parser.add_argument('--no_debug', action='store_true', default=False)

    def __init__(self, args):
        self.args = args
        self.debug = not self.args.no_debug
        os.makedirs(self.args.tmp_dir, exist_ok=True)
        self.sock = socket.socket()
        self.sock.bind((self.args.host, self.args.port))
        self.sock.listen(self.args.clients_number)
        self.connections = []
        self.addrs = []
        self.image_size = [int(s) for s in args.img_size.split(',')]

    def accept(self):
        conn, addr = self.sock.accept()
        logger.info(f"Connection from {addr}")
        self.connections.append(conn)
        self.addrs.append(addr)

    def listen(self, con_id=0):
        conn = self.connections[con_id]
        datas = []
        while True:
            data = conn.recv(1024)
            datas.extend(data)
            if not data:
                logger.info("End data recvs")
                break
        img = self.data2image(data)

    def data2image(self, data):
        img = Image.frombytes(mode=self.args.img_mode,
                              size=self.image_size,
                              data=data,
                              decoder_name=self.args.img_decoder_name)
        if self.debug:
            t = str(time.time())
            name = os.path.join(self.args.tmp_dir, t + ".jpeg")
            logger.info(f"Saving  image to {name}")
            img.save(name)
        return img

