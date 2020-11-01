import struct
import logging

logger = logging.getLogger(__name__)
HEADER_LEN = 4


def send_bytes(sock, bytes):
    data_len = len(bytes)
    logger.debug("Send to server {} bytes".format(data_len))
    header = struct.pack('!i', data_len)

    logger.debug("Send header {}".format(header))
    sock.sendall(header)
    answ = str(sock.recv(1024))
    logger.debug("Answer is {}".format(answ))
    logger.debug("Send data")
    sock.sendall(bytes)
    logger.debug("Done")


def recv_bytes(sock):
    header = sock.recv(HEADER_LEN)
    if not header:
        logger.info("Got zero header")
        return
    logger.debug("Got header {}".format(header))
    answ = 'Ready'
    logger.debug("Send answ '{}'".format(answ))
    sock.sendall(answ.encode())
    data_len = struct.unpack('!i', header)[0]
    logger.debug("Data len is {}".format(data_len))
    datas = []
    while True:
        data = sock.recv(data_len)
        logger.debug("Got {} bytes. ({}/{})".format(len(data), len(data)+len(datas), data_len))
        datas.extend(data)
        if len(datas) == data_len:
            break
        if not data:
            logger.info("Got zero data")
            return datas
    return datas

