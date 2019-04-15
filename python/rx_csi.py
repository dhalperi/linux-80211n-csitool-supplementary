#!/usr/bin/env python3

import argparse
import numpy as np
from netlink import open_netlink_socket
from netlink import close_netlink_socket
from netlink import recv_from_netlink_socket
from csi_decoder import CsiEntry, CsiDecoder
from utils import configure_rx_chains

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2019 Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Select wireless interface')
    parser.add_argument('--rxchains',
                        type=str,
                        default="ABC",
                        help='Which RX chains should be activated, e.g. ABC')
    parser.add_argument('--plot',
                        type=bool,
                        default=False,
                        help='Plot CSI to PNG file')

    args = parser.parse_args()
    rxChains = args.rxchains
    plot = args.plot

    configure_rx_chains(rxChains)

    sock = open_netlink_socket()
    while True:
        try:
            payload = recv_from_netlink_socket(sock)
            csiEntry = CsiDecoder.decode(payload)
            print(csiEntry)

            if plot and csiEntry.correct:
                import matplotlib as mpl
                import matplotlib.pyplot as plt

                plot = False # plot only once
                fig, ax = plt.subplots(figsize=(10,5))
                plt.grid(True, linestyle='--')
                plt.title('CSI')
                for i in range(csiEntry.Ntx):
                    for j in range(csiEntry.Nrx):
                        linestyle = '-'
                        if i == 1:
                            linestyle = ':'
                        if i == 2:
                            linestyle = '--'
                        # add +0.001 to prevent negative
                        plt.plot(range(30), 20*np.log10(np.abs(csiEntry.csi[i][j] + 0.001)), label="Antenna {}->{}".format(i,j), linestyle=linestyle)
                plt.xlabel('Subcarrier index')
                plt.ylabel('SNR [dB]')
                plt.legend(prop={'size': 12})
                plt.savefig('csi_example.png', bbox_inches='tight')
                plt.show()

        except KeyboardInterrupt:
            print("Ctrl+C -> Exit")
            break

    close_netlink_socket(sock)
