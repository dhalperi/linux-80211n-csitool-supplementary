#!/usr/bin/env python3

import argparse
from scapy.all import *
from utils import configure_tx_chains

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2019 Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Select wireless interface')
    parser.add_argument('--txchains',
                        type=str,
                        default="ABC",
                        help='Which RX chains should be activated, e.g. ABC')
    parser.add_argument('--streamNum',
                        type=int,
                        default=1,
                        help='Number of TX streams')
    parser.add_argument('--mcs',
                        type=int,
                        default=0,
                        help='MCS index')
    parser.add_argument('--size',
                        type=int,
                        default=100,
                        help='Frame size')
    parser.add_argument('--count',
                        type=int,
                        default=1,
                        help='Number of frames to send')
    parser.add_argument('--interval',
                        type=float,
                        default=1,
                        help='Frame sending interval [s]')

    args = parser.parse_args()
    txchains = args.txchains
    streamNum = args.streamNum
    mcs = args.mcs
    size = args.size
    count = args.count
    interval = args.interval

    configure_tx_chains(txchains, streamNum, mcs)

    rt = RadioTap()
    dot11 = Dot11(addr1="00:16:ea:12:34:56",
                  addr2="00:16:ea:12:34:56",
                  addr3="ff:ff:ff:ff:ff:ff")

    DOT11_SUBTYPE_QOS_DATA = 0x28
    recv_mac = "00:16:ea:12:34:56"
    src_mac = "00:16:ea:12:34:56"
    dst_mac = "ff:ff:ff:ff:ff:ff"
    ds=0x01
    dot11 =  Dot11(type="Data", subtype=DOT11_SUBTYPE_QOS_DATA, addr1=recv_mac, addr2=src_mac, addr3=dst_mac, SC=0x3060, FCfield=ds)
    payload = Raw(RandString(size=size))
    frame = rt / dot11 / payload

    sendp(frame, iface="mon0", inter=interval, count=count)
