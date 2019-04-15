1.  Receiver:
1.1 Setup receiver:
	sudo ./setup_rx.sh 5 HT20

1.2 Sniff packets using tcpdump:
	sudo ./tcpdump_sniff.sh

1.3 Receive CSI:
	sudo ./rx_csi.py --rxchains "abc"

2.  Transmitter
2.1 Setup transmitter:
	sudo ./setup_tx.sh 5 HT20

2.1 Send frames:
	sudo ./send_frames.py --txchains "abc" --streamNum 1 --mcs 0 --count 10 --size 1000 --interval 0.1
