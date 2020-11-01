import struct
import logging

logger = logging.getLogger(__name__)
HEADER_LEN = 4


def send_bytes(sock, bytes):
    data_len = len(bytes)
    logger.debug("Send to server {} bytes".format(data_len))
    header = struct.pack('!i', data_len)

    logger.debug("Send header {}".format(header))
    sock.send(header)

    logger.debug("Send data")
    sock.send(bytes)
    logger.debug("Done")


def recv_bytes(sock):
    header = sock.recv(HEADER_LEN)
    if not header:
        logger.info("Got zero header")
        return
    logger.debug("Got header {}".format(header))
    data_len = struct.unpack('!i', header)
    logger.debug("Data len is {}".format(data_len))

    data = sock.recv(data_len)
    if not data:
        logger.info("Got zero data")
        return
    return data

