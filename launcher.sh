#!/bin/sh
sudo bluetoothctl discoverable on
sudo python $(sudo find /home/pi/ -name "pi.py")
