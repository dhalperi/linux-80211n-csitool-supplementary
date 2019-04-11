import os
import socket
import struct

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2019 Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"

# iwl_nl.h
IWL_NL_BUFFER_SIZE = 4096

# connector_users.h
CN_NETLINK_USERS = 11   # Highest index + 1

# iwl_connector.h
CN_IDX_IWLAGN = (CN_NETLINK_USERS + 0xf)
CN_VAL_IWLAGN = 0x1

# define type
if getattr(socket, "NETLINK_CONNECTOR", None) is None:
    socket.NETLINK_CONNECTOR = 11

def open_netlink_socket():
    # Setup the socket
    sock = socket.socket(socket.AF_NETLINK, socket.SOCK_DGRAM, socket.NETLINK_CONNECTOR)

    # Now bind the socket
    sock.bind((os.getpid(), CN_IDX_IWLAGN))

    # 270 is SOL_NETLINK and 1 is NETLINK_ADD_MEMBERSHIP
    sock.setsockopt(270, 1, CN_IDX_IWLAGN)
    return sock


def close_netlink_socket(sock):
    sock.close()


def recv_from_netlink_socket(sock):
    data = sock.recv(IWL_NL_BUFFER_SIZE)

    # decode netlink header
    msg_len, msg_type, flags, seq, pid = struct.unpack("=LHHLL", data[:16])
    #print(msg_len, msg_type, flags, seq, pid)

    # get payload
    payload = data[32:]
    return payload
