#!/bin/sh
sudo bluetoothctl discoverable on
sudo bluetoothctl pairable on
sudo python3 $(sudo find /home/pi/ -name "pi.py")
