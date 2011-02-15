function ret = qam64_ber(snr)
    ret = 7/12*qfunc(sqrt(snr/21));
end