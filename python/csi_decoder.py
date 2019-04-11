import numpy as np

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2019 Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


BUF_SIZE = 4096
triangle = np.array([1, 3, 6])  # What perm should sum to for 1,2,3 antennas

DTYPE_LENGTH_TLV = np.dtype([
    ("length", np.uint16),
]).newbyteorder('<')

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
    ("fake_rate_n_flags", np.uint8),
]).newbyteorder('<')

DTYPE_CSI_DATA_TLV = np.dtype(np.ubyte).newbyteorder('<')


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


class CsiEntry(object):
    """docstring for CsiEntry"""
    def __init__(self):
        super(CsiEntry, self).__init__()
        self.correct = True
        self.code = None
        self.bfee_count = None
        self.Nrx = None
        self.Ntx = None
        self.rssiA = None
        self.rssiB = None
        self.rssiC = None
        self.noise = None
        self.agc = None
        self.antenna_sel = None
        self.length = None
        self.rate = None
        self.rssiA_db = None
        self.rssiB_db = None
        self.rssiC_db = None
        self.csi = None
        self.perm = None
        self.csi_pwr = None
        self.rssi_pwr_db = None
        self.rssi_pwr = None
        self.scale = None
        self.noise_db = None
        self.quant_error_pwr = None
        self.total_noise_pwr = None

    def __str__(self):
        myString = "CSI Entry:\n"
        myString += "\t Correct: " + str(self.correct) + "\n"
        if not self.correct:
            return myString

        myString += "\t Code: " + str(self.code) + "\n"
        myString += "\t bfee_count: " + str(self.bfee_count) + "\n"
        myString += "\t Ntx: " + str(self.Ntx) + "\n"
        myString += "\t Nrx: " + str(self.Nrx) + "\n"
        myString += "\t MCS Rate: " + str(self.rate) + "\n"
        myString += "\t Rssi A [dB]: " + str(self.rssiA_db) + "\n"
        myString += "\t Rssi B [dB]: " + str(self.rssiB_db) + "\n"
        myString += "\t Rssi C [dB]: " + str(self.rssiC_db) + "\n"
        myString += "\t Total Rssi [dB]: " + str(np.round(self.rssi_pwr_db,2)) + "\n"
        myString += "\t Agc: " + str(self.agc) + "\n"
        myString += "\t Antenna Sel: " + str(self.antenna_sel) + "\n"
        myString += "\t Thermal Noise [dB]: " + str(self.noise_db) + "\n"
        myString += "\t Quantization Noise [dB]: " + str(np.round(self.quant_error_pwr,2)) + "\n"
        myString += "\t Total Noise [dB]: " + str(np.round(self.total_noise_pwr,2)) + "\n"
        myString += "\t Permutation vector: " + str(self.perm) + "\n"
        myString += "\t CSI matrix shape: " + str(self.csi.shape) + "\n"
        return myString


class CsiDecoder(object):
    """docstring for CsiDecoder"""
    def __init__(self):
        super(CsiDecoder).__init__()

    @classmethod
    def decode(cls, rawData, debug=False):
        csiEntry = CsiEntry()

        lengthRawData = np.copy(rawData[:DTYPE_LENGTH_TLV.itemsize])
        length = np.frombuffer(lengthRawData, dtype=DTYPE_LENGTH_TLV)
        length = length["length"][0]

        if debug:
            print("")
            print("***New CSI message***")
            print("NETLINK msg length: ", length)

        if (length == 0):
            print("Error: got entry size=0")
            csiEntry.correct = False
            return csiEntry

        elif (length > BUF_SIZE):
            print("Error: got entry size {} > BUF_SIZE={}".format(length, BUF_SIZE))
            csiEntry.correct = False
            return csiEntry

        # Read in the entry
        startIdx = 4  # length is only uint16 but there is 4 byte aligment
        csiRawData = rawData[startIdx:]
        header = np.frombuffer(csiRawData[0:DTYPE_CSI_HEADER_TLV.itemsize], dtype=DTYPE_CSI_HEADER_TLV)
        csiData = np.frombuffer(csiRawData[DTYPE_CSI_HEADER_TLV.itemsize:], dtype=DTYPE_CSI_DATA_TLV)

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

        rssiA_db = rssiA - 44 - agc
        rssiB_db = rssiB - 44 - agc
        rssiC_db = rssiC - 44 - agc

        if debug:
            print("Msg header: ", header)
            print("code: ", code)
            print("bfee_count: ", bfee_count)
            print("Ntx: ", Ntx)
            print("Nrx: ", Nrx)
            print("rssiA: ", rssiA_db)
            print("rssiB: ", rssiB_db)
            print("rssiC: ", rssiC_db)
            print("noise: ", noise)
            print("agc  : ", agc)
            print("antenna_sel  : ", antenna_sel)
            print("length  : ", length)
            print("rate: ", rate)

        csiEntry.code = code
        csiEntry.bfee_count = bfee_count
        csiEntry.Nrx = Nrx
        csiEntry.Ntx = Ntx
        csiEntry.rssiA = rssiA
        csiEntry.rssiB = rssiB
        csiEntry.rssiC = rssiC
        csiEntry.noise = noise
        csiEntry.agc = agc
        csiEntry.antenna_sel = antenna_sel
        csiEntry.length = length
        csiEntry.rate = rate
        csiEntry.rssiA_db = rssiA_db
        csiEntry.rssiB_db = rssiB_db
        csiEntry.rssiC_db = rssiC_db

        calc_len = (30 * (Nrx * Ntx * 8 * 2 + 3) + 7) / 8
        calc_len = np.int(calc_len)
        # Check that length matches what it should */
        if (length != calc_len):
            print("Wrong CSI matrix size.")
            csiEntry.correct = False
            return csiEntry

        csiMatrixShape = (Ntx, Nrx, 30)
        csiMatrix = np.zeros(shape=csiMatrixShape, dtype=np.complex64)
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

                csiMatrix[txAntId, rxAntId, i] = complexCsi
                index += 16
                counter += 1

        # Compute the permutation array
        permMatrix[0] = ((antenna_sel) & 0x3) + 1
        permMatrix[1] = ((antenna_sel >> 2) & 0x3) + 1;
        permMatrix[2] = ((antenna_sel >> 4) & 0x3) + 1;

        if debug:
            print("csiMatrix ", csiMatrix.shape)
            print("perm", permMatrix)

        if Nrx == 1:
            pass # No permuting needed for only 1 antenna

        elif np.sum(permMatrix[:Nrx]) != triangle[Nrx-1]: # matrix does not contain default values
            print('WARN ONCE: Found CSI with Nrx={} and invalid perm'.format(Nrx))
            print("rx perm", permMatrix)
            print("triangle", triangle)

        else:
            permIdxs = permMatrix - 1
            tmpMatrix = np.copy(csiMatrix)
            csiMatrix[:,permIdxs[:Nrx],:] = tmpMatrix[:,:,:];

        # scale CSI
        # Calculate the scale factor between normalized CSI and RSSI (mW)
        csi_sq = np.multiply(csiMatrix, np.conj(csiMatrix))
        csi_pwr = np.sum(csi_sq)
        csi_pwr = np.real(csi_pwr)

        rssi_pwr_db = get_total_rss(rssiA, rssiB, rssiC, agc)
        rssi_pwr = np.power(10, rssi_pwr_db/10)

        if debug:
            print("csi_pwr: ", csi_pwr)
            print("ant_power: ", rssiA, rssiB, rssiC, agc)
            print("rssi_pwr [db]: ",rssi_pwr_db)
            print("rssi_pwr [linear]: ",rssi_pwr)

        # Scale CSI -> Signal power : rssi_pwr / (mean of csi_pwr)
        scale = rssi_pwr / (csi_pwr / 30);

        if debug:
            print("scale: ", scale)

        # Thermal noise might be undefined if the trace was
        # captured in monitor mode.
        # ... If so, set it to -92
        noise_db = noise
        if (noise == -127):
            noise_db = -92

        noise_db = np.float(noise_db)
        thermal_noise_pwr  = np.power(10.0, noise_db/10);

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

        if debug:
            print("noise_db: ", noise_db)
            print("thermal_noise_pwr: ", thermal_noise_pwr)
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

        csiEntry.csi = csiMatrix
        csiEntry.perm = permMatrix
        csiEntry.csi_pwr = csi_pwr
        csiEntry.rssi_pwr = rssi_pwr
        csiEntry.rssi_pwr_db = rssi_pwr_db
        csiEntry.scale = scale
        csiEntry.noise_db = noise_db
        csiEntry.quant_error_pwr = 10*np.log10(quant_error_pwr)
        csiEntry.total_noise_pwr = 10*np.log10(total_noise_pwr)

        return csiEntry
