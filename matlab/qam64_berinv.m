function ret = qam64_berinv(ber)
    ret = qfuncinv(12/7*ber).^2*21;
end