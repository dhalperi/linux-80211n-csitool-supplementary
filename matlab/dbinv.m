%DBINV Convert from decibels.
function ret = dbinv(x)
    ret = 10.^(x/10);
end