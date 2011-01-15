%GET_SCALED_CSI Converts a CSI struct to a scaled CSI matrix.
function ret = get_scaled_csi(csi_st)
    % Pull out CSI
    csi = csi_st.csi;

    % Calculate the scale factor between RSSI and CSI
    csi_sq = csi .* conj(csi);
    csi_mag = sum(csi_sq(:));
    % Careful here: rssis could be zero
    rssi_mag = 0;
    if csi_st.rssi_a ~= 0
        rssi_mag = rssi_mag + dbinv(csi_st.rssi_a);
    end
    if csi_st.rssi_b ~= 0
        rssi_mag = rssi_mag + dbinv(csi_st.rssi_b);
    end
    if csi_st.rssi_c ~= 0
        rssi_mag = rssi_mag + dbinv(csi_st.rssi_c);
    end

    % Noise might be undefined
    % ... If so, set it to -95
    if (csi_st.noise == -127)
        noise = -92;
    else
        noise = csi_st.noise;
    end
    
    % Scale factor to convert to SNR. Two steps:
    %
    %   Scale CSI -> S : rssi_mag / (mean of csi_mag)
    %   Calculate N: noise + 44 + AGC
    scale = rssi_mag / (csi_mag / 30) / dbinv(noise + 44 + csi_st.agc);
    ret = csi * sqrt(scale);
    if csi_st.Ntx == 2
        ret = ret * sqrt(csi_st.Ntx);
    elseif csi_st.Ntx == 3
        ret = ret * sqrt(dbinv(4.5));
    end
end