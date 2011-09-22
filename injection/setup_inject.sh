#!/usr/bin/sudo /bin/bash
rmmod iwlagn mac80211 cfg80211
modprobe iwlagn
ifconfig wlan0 2>/dev/null 1>/dev/null
while [ $? -ne 0 ]
do
	        ifconfig wlan0 2>/dev/null 1>/dev/null
done
iw dev wlan0 interface add mon0 type monitor
iw mon0 set channel $1 $2
ifconfig mon0 up
