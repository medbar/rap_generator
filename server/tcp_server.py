import socket
import argparse
import logging
import os
import io
from PIL import Image
import time

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.DEBUG,
)
logger = logging.getLogger(__name__)


class RapGeneratorServer:
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument("--port", default=9090, type=int)
        parser.add_argument('--host', default='0.0.0.0', type=str)
        parser.add_argument('--clients_number', default=1, type=int)
        parser.add_argument('--recv_bsize', type=int, default=1024)
        parser.add_argument('--img_size', type=str, default='100,100')
        # parser.add_argument('--img_mode', type=str, default='RGB')
        parser.add_argument('--img_format', type=str, default='jpeg')
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
        while True:
            img = self.get_image(con_id)
            if not img:
                logger.info(f"Break connection from {self.addrs[con_id]}")
                break
            yield img
        return

    def get_image(self, con_id=0):
        conn = self.connections[con_id]
        datas = []
        logger.debug("Waiting image...")
        while True:
            data = conn.recv(1024)
            logger.debug(f"recived {len(data)} bytes. Continue..")
            datas.extend(data)
            if not data:
                logger.debug("End data recvs")
                break
        logger.debug(f"Client sent {len(datas)} bytes")
        if len(datas) == 0:
            return
        img = self.data2image(data)
        return img

    def data2image(self, data):
        logger.debug(f"Convert bytes to image")
        img = Image.open(io.BytesIO(data))
        # img = Image.frombytes(mode=self.args.img_mode,
        #                       size=self.image_size,
        #                       data=data,
        #                       decoder_name=self.args.img_decoder_name)

        if self.debug:
            t = str(time.time())
            name = os.path.join(self.args.tmp_dir, t + "." + self.args.img_format)
            logger.info(f"Saving  image to {name}")
            img.save(name)
        return img

    def response_to_client(self, bytes, con_id=0):
        logger.debug(f"Send to client {len(bytes)} bytes.")
        sock = self.connections[con_id]
        sock.send(bytes)
        logger.debug(f"Send zero.")
        sock.send(''.encode())
        logger.debug("Done")


def main():
    parser = argparse.ArgumentParser()
    RapGeneratorServer.add_args(parser)
    args = parser.parse_args()
    server = RapGeneratorServer(args)
    logger.info(vars(args))
    with open('audio/stc-cloud_tts.wav', 'rb') as f:
        answ = f.read()
    try:
        while True:
            logger.info("Wait to new connection...")
            server.accept()
            for img in server.listen():
                logger.debug("Process image")
                #TODO real answ
                server.response_to_client(answ)
    finally:
        server.sock.close()


if __name__ == "__main__":
    main()
