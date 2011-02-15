function ret = qam16_berinv(ber)
    ret = qfuncinv(ber * 4/3).^2 * 5;
end