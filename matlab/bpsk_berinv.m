function ret = bpsk_berinv(ber)
    ret = qfuncinv(ber).^2 / 2;
end