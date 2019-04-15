#!/usr/bin/env python3

import logging
import argparse
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2019 Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


BUF_SIZE = 4096
triangle = np.array([1, 3, 6])  # What perm should sum to for 1,2,3 antennas

DTYPE_LENGTH_TLV = np.dtype([
    ("length", np.uint16),
]).newbyteorder('>')

DTYPE_CSI_HEADER_TLV = np.dtype([
    ("code", np.uint8),
    ("timestamp_low", np.uint32),
    ("bfee_count", np.uint16),
    ("reserved1", np.uint16),
    ("Nrx", np.uint8),
    ("Ntx", np.uint8),
    ("rssiA", np.uint8),
    ("rssiB", np.uint8),
    ("rssiC", np.uint8),
    ("noise", np.int8),
    ("agc", np.uint8),
    ("antenna_sel", np.uint8),
    ("len", np.uint16),
    ("fake_rate_n_flags", np.uint16),
]).newbyteorder('<')

DTYPE_CSI_DATA_TLV = np.dtype(np.ubyte).newbyteorder('>')


def get_total_rss(rssi_a, rssi_b, rssi_c, agc):
    # Calculates the Received Signal Strength (RSS) in dBm from
    # Careful here: rssis could be zero
    rssi_mag = 0
    if rssi_a != 0:
        rssi_mag = rssi_mag + np.power(10.0, rssi_a/10)

    if rssi_b != 0:
        rssi_mag = rssi_mag + np.power(10.0, rssi_b/10)

    if rssi_c != 0:
        rssi_mag = rssi_mag + np.power(10.0, rssi_c/10)

    ret = 10*np.log10(rssi_mag) - 44 - agc;
    return ret


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Select wireless interface')
    parser.add_argument('--file',
                        type=str,
                        default=None,
                        help='Port on which LtFi receiver publishes recv msg.')

    args = parser.parse_args()
    fileName = args.file

    fn = '../matlab/sample_data/log.all_csi.6.7.6'

    with open(fn, 'rb') as inFile:
        while True:
            # Read the next entry size
            rawLength = inFile.read(DTYPE_LENGTH_TLV.itemsize)
            if not rawLength:
                break

            length = np.frombuffer(rawLength, dtype=DTYPE_LENGTH_TLV)
            length = length["length"][0]
            print("length: ", length)

            if (length == 0):
                print("Error: got entry size=0")
                exit(-1)
                break

            elif (length > BUF_SIZE):
                print("Error: got entry size {} > BUF_SIZE={}".format(length, BUF_SIZE))
                exit(-2);
                break

            # Read in the entry
            rawData = inFile.read(length)

            header = np.frombuffer(rawData[0:DTYPE_CSI_HEADER_TLV.itemsize], dtype=DTYPE_CSI_HEADER_TLV)
            csiData = np.frombuffer(rawData[DTYPE_CSI_HEADER_TLV.itemsize:], dtype=DTYPE_CSI_DATA_TLV)

            print(header)
            print(csiData.shape)
            code = header["code"][0]
            bfee_count = header["bfee_count"][0]
            Nrx = header["Nrx"][0]
            Ntx = header["Ntx"][0]
            rssiA = header["rssiA"][0]
            rssiB = header["rssiB"][0]
            rssiC = header["rssiC"][0]
            noise = header["noise"][0]
            agc = header["agc"][0]
            antenna_sel = header["antenna_sel"][0]
            length = header["len"][0]
            rate = header["fake_rate_n_flags"][0]

            rssiAdb = rssiA - 44 - agc;
            rssiBdb = rssiB - 44 - agc;
            rssiCdb = rssiC - 44 - agc;

            print("code: ", code)
            print("bfee_count: ", bfee_count)
            print("Nrx: ", Nrx)
            print("Ntx: ", Ntx)
            print("rssiA: ", rssiAdb)
            print("rssiB: ", rssiBdb)
            print("rssiC: ", rssiCdb)
            print("noise: ", noise)
            print("agc  : ", agc)
            print("antenna_sel  : ", antenna_sel)
            print("length  : ", length)
            print("rate: ", rate)

            calc_len = (30 * (Nrx * Ntx * 8 * 2 + 3) + 7) / 8
            calc_len = np.int(calc_len)
            # Check that length matches what it should */
            if (length != calc_len):
                print("Wrong CSI matrix size.")

            csiMatrixShape = (Ntx, Nrx, 30)
            tmpMatrix = np.zeros(shape=(Ntx * Nrx * 30), dtype=np.complex64)
            csiMatrix = np.zeros(shape=csiMatrixShape, dtype=np.complex64)
            print("csiMatrix ", csiMatrix.shape)

            permShape = (3)
            permMatrix = np.zeros(shape=permShape, dtype=np.int)

            # Compute CSI from all this crap
            counter = 0
            index = 0
            remainder = 0
            for i in range(30):
                index += 3
                remainder = index % 8;
                rxAntId = -1
                for j in range(Ntx * Nrx):
                    idx = np.int(index / 8)
                    tmpReal = (csiData[idx] >> remainder) | (csiData[idx+1] << (8-remainder))
                    tmpReal = np.int8(tmpReal)
                    tmpImag = (csiData[idx+1] >> remainder) | (csiData[idx+2] << (8-remainder))
                    tmpImag = np.int8(tmpImag)
                    complexCsi = tmpReal + tmpImag * 1j

                    txAntId = j % Ntx
                    if txAntId == 0:
                        rxAntId += 1
                    #print(j, txAntId, rxAntId)
                    csiMatrix[txAntId, rxAntId, i] = complexCsi
                    #print(complexCsi)
                    #input("Press enter...")
                    index += 16
                    counter += 1

            # Compute the permutation array
            permMatrix[0] = ((antenna_sel) & 0x3) + 1
            permMatrix[1] = ((antenna_sel >> 2) & 0x3) + 1;
            permMatrix[2] = ((antenna_sel >> 4) & 0x3) + 1;
            print("perm", permMatrix)

            if Nrx == 1:
                continue # No permuting needed for only 1 antenna

            if np.sum(permMatrix) != triangle[Nrx-1]:
                print('WARN ONCE: Found CSI with Nrx={} and invalid perm'.format(Nrx))

            else:
                permIdxs = permMatrix - 1
                tmpMatrix = np.copy(csiMatrix)
                csiMatrix[:,permIdxs[:Nrx],:] = tmpMatrix[:,:,:];

            #print(csiMatrix.shape)
            #print(csiMatrix)
            #input("Press enter...")

            # scale CSI
            # Calculate the scale factor between normalized CSI and RSSI (mW)
            csi_sq = np.multiply(csiMatrix, np.conj(csiMatrix))
            csi_pwr = np.sum(csi_sq)
            csi_pwr = np.real(csi_pwr)
            print("csi_pwr: ", csi_pwr)

            print("ant_power: ", rssiA, rssiB, rssiC, agc)
            rssi_pwr = get_total_rss(rssiA, rssiB, rssiC, agc)
            print("rssi_pwr: ",rssi_pwr)
            rssi_pwr = np.power(10, rssi_pwr/10)
            print("rssi_pwr: ",rssi_pwr)


            # Scale CSI -> Signal power : rssi_pwr / (mean of csi_pwr)
            scale = rssi_pwr / (csi_pwr / 30);
            print("scale: ", scale)

            # Thermal noise might be undefined if the trace was
            # captured in monitor mode.
            # ... If so, set it to -92
            noise_db = noise
            if (noise == -127):
                noise_db = -92

            noise_db = np.float(noise_db)
            print("noise_db: ", noise_db)

            thermal_noise_pwr  = np.power(10.0, noise_db/10);
            print("thermal_noise_pwr: ", thermal_noise_pwr)

            '''
            Quantization error: the coefficients in the matrices are
            8-bit signed numbers, max 127/-128 to min 0/1. Given that Intel
            only uses a 6-bit ADC, I expect every entry to be off by about
            +/- 1 (total across real & complex parts) per entry.

            The total power is then 1^2 = 1 per entry, and there are
            Nrx*Ntx entries per carrier. We only want one carrier's worth of
            error, since we only computed one carrier's worth of signal above.
            '''
            quant_error_pwr = scale * (Nrx * Ntx)
            # Total noise and error power
            total_noise_pwr = thermal_noise_pwr + quant_error_pwr;
            print("total_noise_pwr: ", total_noise_pwr)

            # Ret now has units of sqrt(SNR) just like H in textbooks
            ret = csiMatrix * np.sqrt(scale / total_noise_pwr);
            if Ntx == 2:
                ret = ret * np.sqrt(2);
            elif Ntx == 3:
                # Note: this should be sqrt(3)~ 4.77 dB. But, 4.5 dB is how
                # Intel (and some other chip makers) approximate a factor of 3
                # You may need to change this if your card does the right thing.
                ret = ret * np.sqrt(np.power(10, 4.5/10));

            csiMatrix = ret

            if 1:
                fig, ax = plt.subplots(figsize=(10,5))
                plt.grid(True, linestyle='--')
                plt.title('CSI')
                #plt.plot(range(len(ret)), 10*np.log10(np.abs(ret)))
                for i in range(Ntx):
                    for j in range(Nrx):
                        linestyle = '-'
                        if i == 1:
                            linestyle = ':'
                        if i == 2:
                            linestyle = '--'
                        plt.plot(range(30), 20*np.log10(np.abs(csiMatrix[i][j])), label="Antenna {}->{}".format(i,j), linestyle=linestyle)
                plt.xlabel('Subcarrier index')
                plt.ylabel('SNR [dB]')
                plt.legend(prop={'size': 12})
                plt.savefig('csi_tmp.png', bbox_inches='tight')
                plt.show()
