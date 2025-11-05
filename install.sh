#!/bin/bash
# WiFi Deauth Tool - Complete Installation Script
# Run with: sudo bash install.sh

set -e  # Exit on error

echo "=========================================="
echo "WiFi Deauth Tool Installation"
echo "=========================================="
echo ""

# Check for root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: This script must be run as root"
    echo "Run with: sudo bash install.sh"
    exit 1
fi

echo "Step 1: Updating system packages..."
apt update

echo ""
echo "Step 2: Installing system dependencies..."
apt install -y \
    aircrack-ng \
    python3 \
    python3-pip \
    python3-smbus \
    i2c-tools \
    git \
    wireless-tools \
    net-tools

echo ""
echo "Step 3: Installing WiFi adapter firmware..."
echo "Installing firmware for common chipsets..."
apt install -y \
    firmware-ralink \
    firmware-realtek \
    firmware-atheros

echo ""
echo "Step 4: Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt || pip3 install RPLCD

echo ""
echo "Step 5: Creating dump directory..."
mkdir -p /home/pi/dump
chown pi:pi /home/pi/dump
chmod 755 /home/pi/dump

echo ""
echo "Step 6: Enabling I2C for LCD..."
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt 2>/dev/null && \
   ! grep -q "^dtparam=i2c_arm=on" /boot/firmware/config.txt 2>/dev/null; then
    echo "I2C needs to be enabled manually"
    echo "Run: sudo raspi-config"
    echo "Navigate to: Interface Options -> I2C -> Enable"
else
    echo "I2C already enabled"
fi

# Load I2C modules
modprobe i2c-dev 2>/dev/null || true

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "IMPORTANT: You need a WiFi adapter that supports monitor mode!"
echo ""
echo "Detected USB devices:"
lsusb | grep -i "ralink\|realtek\|atheros\|wireless\|wlan\|802.11" || echo "  No WiFi adapters detected"
echo ""
echo "The RTL2838 DVB-T device is a TV tuner, not a WiFi adapter."
echo "You need to purchase a compatible WiFi adapter such as:"
echo "  - Panda PAU09 (RT5572 chipset)"
echo "  - Alfa AWUS036NH (RTL8187 chipset)"
echo "  - Any adapter with RT3070, RT5370, or Atheros AR9271 chipset"
echo ""
echo "Next steps:"
echo "  1. Plug in a compatible WiFi adapter"
echo "  2. Reboot: sudo reboot"
echo "  3. Run test: sudo bash test_setup.sh"
echo "  4. If tests pass, run: sudo python3 attack.py"
echo ""



