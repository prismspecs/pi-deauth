# Testing Guide - WiFi Deauth Tool

## Quick Test (Automated)

Run the automated test script to verify your setup:

```bash
cd /home/grayson/workbench/wifi-deauth-rpi-wardrive
sudo bash test_setup.sh
```

This will check:
- Root privileges
- WiFi adapters (wlan0 and wlan1)
- Required software (aircrack-ng suite)
- Python dependencies
- Monitor mode capability
- I2C and LCD (if connected)
- Quick 5-second scan test

## Manual Testing Steps

### 1. Verify Hardware

**Check WiFi adapters:**
```bash
# List USB devices
lsusb | grep -i ralink

# Check wireless interfaces
iwconfig
```

Expected output:
- wlan0: Built-in adapter
- wlan1: External USB adapter (RT5572/Panda PAU09)

### 2. Install Firmware (if needed)

For RT5572 (Panda PAU09) and other Ralink adapters:
```bash
sudo apt update
sudo apt install firmware-ralink
sudo reboot
```

### 3. Test Monitor Mode

```bash
# Enable monitor mode
sudo airmon-ng start wlan1

# Verify
iwconfig wlan1
# Should show "Mode:Monitor"
```

### 4. Test Scanning

```bash
# Manual scan to see available networks
sudo airodump-ng wlan1

# Look for:
# - Networks appearing in the list
# - Signal strength (PWR column)
# - If testing eduroam, check if it appears in ESSID column

# Press Ctrl+C to stop
```

### 5. Test LCD (Optional)

```bash
# Check I2C
sudo i2cdetect -y 1
# Should show "27" or "3F"

# Run LCD test
python3 lcd_display.py
# Should display test patterns on LCD
```

### 6. Test Attack Script

**First run (dry run):**
```bash
cd /home/grayson/workbench/wifi-deauth-rpi-wardrive
sudo python3 attack.py
```

**What to watch for:**
```
WiFi Deauth Initializing...
LCD initialized successfully (if LCD connected)
Monitor mode enabled
Removing dump files

=== Attack Loop 1 ===
Starting airodump-ng scan...
airodump-ng process started
Getting latest dump file
Latest dump: dump-01.csv
```

**If eduroam is in range:**
```
Found target network: eduroam (AA:BB:CC:DD:EE:FF) on channel 36, power -45
Deauthing eduroam ( AA:BB:CC:DD:EE:FF ) on channel 36 num of packets: 100 ...
Hopped to channel 36
Delta time = 0:00:03.123456
Loop 1 complete
```

**If eduroam is NOT in range:**
```
WARNING: Target network 'eduroam' not found!
Loop 1 complete
```

### 7. Test Target Modes

**Test 1: Target specific network (eduroam)**
```bash
nano attack.py
# Verify: target_essid = "eduroam"
sudo python3 attack.py
# Should only attack eduroam
```

**Test 2: Target strongest signal (any network)**
```bash
nano attack.py
# Change to: target_essid = None
sudo python3 attack.py
# Should attack strongest signal
```

### 8. Verify Data Collection

```bash
# Check CSV files were created
ls -lh /home/pi/dump/

# View captured data
cat /home/pi/dump/dump-01.csv

# Should contain:
# - BSSID (MAC addresses)
# - Channel numbers
# - Power levels
# - ESSID (network names)
```

## Troubleshooting Tests

### Test: WiFi adapter not detected

```bash
# Check if adapter is recognized
lsusb

# Install firmware
sudo apt install firmware-ralink
sudo reboot

# Check again
iwconfig
```

### Test: Monitor mode fails

```bash
# Kill conflicting processes
sudo airmon-ng check kill

# Restart monitor mode
sudo airmon-ng start wlan1

# Verify
iwconfig wlan1 | grep Mode
```

### Test: Permission errors

```bash
# Check user
whoami
# Must be "root"

# Always run with sudo
sudo python3 attack.py
```

### Test: No networks detected

```bash
# Ensure wlan1 is in monitor mode
sudo airmon-ng start wlan1

# Try manual scan first
sudo airodump-ng wlan1
# If nothing appears, your adapter may have issues

# Test with any network (not just eduroam)
nano attack.py
# Change: target_essid = None
sudo python3 attack.py
```

### Test: LCD not working

```bash
# Check I2C
sudo i2cdetect -y 1
# Should show address (27 or 3F)

# If blank, check wiring:
# SDA -> GPIO2 (Pin 3)
# SCL -> GPIO3 (Pin 5)
# VCC -> 5V (Pin 2)
# GND -> GND (Pin 6)

# Enable I2C if needed
sudo raspi-config
# Interface Options -> I2C -> Enable

# Test LCD module
python3 lcd_display.py
```

## Pre-Deployment Checklist

Before using in the field:

- [ ] lsusb shows WiFi adapter
- [ ] iwconfig shows wlan0 and wlan1
- [ ] sudo airmon-ng start wlan1 works
- [ ] sudo airodump-ng wlan1 shows networks
- [ ] firmware-ralink installed (for RT5572)
- [ ] /home/pi/dump directory exists
- [ ] sudo python3 attack.py runs without errors
- [ ] CSV files created in /home/pi/dump/
- [ ] Target network (eduroam) appears when in range
- [ ] Deauth packets sent successfully
- [ ] LCD displays status (if using LCD)
- [ ] i2cdetect shows LCD (if using LCD)
- [ ] Hotspot connection configured in wpa_supplicant_hotspot.conf
- [ ] Crontab configured for auto-start (@reboot)

## Expected Performance

**Timing:**
- Scan phase: 10 seconds
- Parse phase: < 1 second
- Attack phase: 3-5 seconds (100 packets)
- Total loop time: ~15 seconds

**Success indicators:**
- "Found target network: eduroam..." message appears
- "Deauthing eduroam..." message appears
- Delta time shows 3-5 seconds
- Loop completes and repeats
- CSV files continuously created in dump directory
- LCD shows status updates (if connected)

**Failure indicators:**
- "Target network 'eduroam' not found" - Network not in range
- "Latest dump file invalid" - Scan failed
- "Monitor mode not enabled" - Adapter issue
- Permission errors - Not running as root
- No output at all - Software not installed correctly

## Testing Eduroam Specifically

**Prerequisites:**
- Must be physically near an eduroam access point
- Eduroam must be broadcasting (visible in airodump-ng)

**Test procedure:**
1. Run manual scan: `sudo airodump-ng wlan1`
2. Verify eduroam appears in ESSID column
3. Note the channel and signal strength (PWR)
4. Press Ctrl+C to stop scan
5. Run attack script: `sudo python3 attack.py`
6. Watch for "Found target network: eduroam..." message
7. Verify deauth packets are sent
8. Check LCD shows "Attacking / eduroam"

**If eduroam doesn't appear:**
- You may be out of range
- Eduroam may not be deployed in your location
- Test with another network first: `target_essid = None`

## Quick Commands Reference

```bash
# Automated test
sudo bash test_setup.sh

# Manual scan
sudo airodump-ng wlan1

# Check adapters
iwconfig

# Check USB devices
lsusb

# Check I2C
sudo i2cdetect -y 1

# Test LCD
python3 lcd_display.py

# Run attack
sudo python3 attack.py

# View logs
cat /home/pi/dump/dump-01.csv

# Stop attack
# Press Ctrl+C
```

## RT5572 (Panda PAU09) Specific Notes

This adapter has been tested and confirmed working with:
- Raspberry Pi 5
- firmware-ralink package installed
- aircrack-ng suite
- Monitor mode and packet injection both functional

If you're using the Panda PAU09:
1. Install firmware: `sudo apt install firmware-ralink`
2. Reboot: `sudo reboot`
3. Verify: `lsusb | grep Ralink`
4. Should show: "Ralink Technology, Corp."
5. Monitor mode works without issues

## Need Help?

1. Run automated test: `sudo bash test_setup.sh`
2. Check README.md for detailed documentation
3. Review error messages carefully
4. Verify all prerequisites are met
5. Test each component individually before running full attack



