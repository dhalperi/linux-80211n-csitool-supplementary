%GET_QUANT_ERR Calculates the Quantization Error in dBm from
% a CSI struct.
%
% (c) 2012 Daniel Halperin <dhalperi@cs.washington.edu>
%
function ret = get_quant_err(csi_st, ADC_BITS)
    error(nargchk(1,2,nargin));
    if nargin == 1
        ADC_BITS = 6;
    end
    
    % Find the strongest RSS value. On most chips (and iwl5300 for sure),
    % there is only 1 AGC that is locked to the strongest antenna. So
    % the quantization error should be normalized to the strongest signal.
    large_rss = max([csi_st.rssi_a, csi_st.rssi_b, csi_st.rssi_c]);
    
    % Compute the quantization error relative to SNR, 6.02 dB per ADC bit.
    % See Wikipedia: % http://en.wikipedia.org/wiki/Quantization_error
    % Assumption: MIMO-OFDM symbols look more uniform than a pure sine wave.
    quant_rel_dB = 6.02 * ADC_BITS;

    % Same SNR calculation as normal for RSSI -> SNR, then subtract the
    % relative quantization power in dB
    ret = (large_rss - 44 - csi_st.agc) - quant_rel_dB;
end
