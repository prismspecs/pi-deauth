#!/bin/bash
# ============================================================================
# Raspberry Pi Startup Script
# ============================================================================
# This script runs automatically on boot via crontab (@reboot)
# 
# Purpose:
#   - Connect the Pi to a predetermined WiFi network (e.g., phone hotspot)
#   - This allows SSH access to the Pi from your phone while traveling
#   - Without a keyboard/mouse/display, SSH is essential for control
#
# Setup Instructions:
#   1. Edit crontab: crontab -e
#   2. Add this line: @reboot bash /home/pi/startup.sh
#   3. Configure wpa_supplicant_hotspot.conf with your hotspot credentials
#
# Usage While Wardriving:
#   1. Turn on your phone's hotspot
#   2. Power on the Raspberry Pi (it auto-connects via this script)
#   3. SSH from phone: ssh pi@raspberrypi (or use Pi's IP address)
#   4. Run the attack: sudo python3 attack.py
# ============================================================================

# Commented out: Alternative manual monitor mode setup (not needed with airmon-ng)
#sudo ifconfig wlan1 down
#sudo iwconfig wlan1 mode monitor
#sudo ifconfig wlan1 up

# Commented out: Packet capture setup (for debugging/analysis if needed)
#sudo touch /home/pi/capture.pcap
#sudo chown pi:pi /home/pi/capture.pcap
#sudo chmod a+rw /home/pi/capture.pcap
#sudo tshark -i wlan1 -w /home/pi/capture.pcap

# Commented out: Test file creation (for debugging startup execution)
#touch /home/pi/StartupFileCreationTest

# Commented out: Direct wpa_supplicant call (replaced by wifi-connect.sh wrapper)
#sudo wpa_supplicant -B -i wlan0 -c /home/pi/wpa_supplicant_hotspot.conf

# Connect to the predefined hotspot using the wifi-connect script
# wlan0 = built-in WiFi (used for SSH connection to hotspot)
# wlan1 = external WiFi adapter (used for monitor mode and attacks)
sudo bash /home/pi/wifi-connect.sh wlan0 /home/pi/wpa_supplicant_hotspot.conf
