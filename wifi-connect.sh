#!/bin/bash
# ============================================================================
# WiFi Connection Helper Script
# ============================================================================
# This script connects a wireless interface to a WiFi network using
# wpa_supplicant. It's a wrapper that handles cleanup and initialization.
#
# Arguments:
#   $1 - Interface name (e.g., wlan0, wlan1)
#   $2 - Path to wpa_supplicant configuration file
#
# Usage:
#   sudo bash wifi-connect.sh wlan0 /path/to/wpa_supplicant.conf
#
# What it does:
#   1. Removes old wpa_supplicant socket file (cleanup)
#   2. Starts wpa_supplicant in background (-B flag)
#   3. Connects to the network specified in the config file
# ============================================================================

IFACE=$1    # Wireless interface (e.g., wlan0 for built-in, wlan1 for external adapter)
FILENAME=$2 # Path to wpa_supplicant configuration file

# Validate that both arguments were provided
if [ $# -ne 2 ]
then
	echo "Error: Missing required arguments"
	echo "Argument 1 is interface (e.g., wlan0)"
	echo "Argument 2 is filename (e.g., /home/pi/wpa_supplicant.conf)"
	exit 1
fi

# Remove old wpa_supplicant socket file to prevent conflicts
# This ensures a clean start if wpa_supplicant crashed or was stopped improperly
sudo rm /var/run/wpa_supplicant/$IFACE

# Start wpa_supplicant in background mode
# -B = run in background (daemon mode)
# -i = specify interface
# -c = specify configuration file
sudo wpa_supplicant -B -i $IFACE -c $FILENAME
