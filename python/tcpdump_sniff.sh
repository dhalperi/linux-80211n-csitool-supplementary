#!/usr/bin/sudo /bin/bash
iw wlan0 set monitor fcsfail
tcpdump -i wlan0 -s 50 --number -f 'wlan addr1 00:16:ea:12:34:56'
