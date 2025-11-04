# WiFi Deauthentication Wardrive Tool for Raspberry Pi

> **WARNING: DISCLAIMER**: This tool is for educational and authorized testing purposes only. Unauthorized access to computer networks is illegal. Always obtain proper authorization before testing.

## Overview

This project turns a Raspberry Pi into an automated WiFi deauthentication device for wardriving. It continuously scans for nearby WiFi networks and performs deauthentication attacks on the strongest signal, making it ideal for security research and penetration testing.

### Key Features

- **Automated scanning**: Uses `airodump-ng` to detect nearby access points
- **Smart targeting**: Target specific networks (e.g., "eduroam") or automatically select strongest signal
- **LCD display support**: Real-time status updates on 16x2 I2C LCD screen
- **Portable operation**: Designed to run from a backpack with SSH control via phone
- **Data logging**: Saves all detected AP information (BSSID, ESSID, channel, power) to CSV files for later analysis
- **Continuous operation**: Automatically refreshes targets as you move around
- **Raspberry Pi 5 compatible**: Works on Pi Zero W, 3, 4, and 5

## How It Works

The system uses a dual-WiFi setup:
- **wlan0** (built-in): Connects to your phone's hotspot for SSH access
- **wlan1** (external adapter): Monitor mode for scanning and deauth attacks

### Attack Workflow

1. **Scan Phase**: `airodump-ng` scans all channels for 10 seconds
2. **Parse Phase**: Script reads CSV and identifies the strongest AP
3. **Attack Phase**: Sends 100 deauth packets to the target
4. **Repeat**: Loop continues indefinitely

## What You Need

### Hardware

**Required:**
- 1x Raspberry Pi (Zero W, 3, 4, or 5)
- **1x External WiFi adapter with monitor mode capability** (REQUIRED - built-in WiFi does NOT work reliably for this)
  - Recommended: Alfa AWUS036NH, Alfa AWUS036NHA, Alfa AWUS036ACH
  - Must support monitor mode and packet injection
  - Chipsets: RTL8187, RT3070, RT5370, Atheros AR9271
- 1x MicroSD card (8GB+ recommended)

**Optional:**
- 16x2 I2C LCD display (PCF8574 backpack) for real-time status
- Portable battery pack for mobile operation
- USB hub if using Pi Zero W (for both WiFi adapter and LCD)

### Why You Need a Separate WiFi Adapter

The Raspberry Pi's built-in WiFi adapter:
- Does NOT support monitor mode reliably
- Cannot perform packet injection
- Uses proprietary firmware with limited capabilities

You need **TWO WiFi interfaces**:
1. **Built-in WiFi (wlan0)**: Connect to phone hotspot for SSH access
2. **External USB adapter (wlan1)**: Monitor mode for scanning and attacks

### Tested Hardware

This project has been tested with:
- **RT5572 chipset** (Panda PAU09 adapter)
- Alfa AWUS036NH (RTL8187)
- Other Ralink chipsets (RT3070, RT5370)

### Software Requirements
- Raspberry Pi OS (Bookworm or Bullseye)
- aircrack-ng suite (airodump-ng, aireplay-ng, airmon-ng)
- Python 3.7+
- wpa_supplicant
- I2C tools and libraries (for LCD)
- RPLCD Python library (for LCD)

## Installation & Setup

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install aircrack-ng python3 python3-pip python3-smbus i2c-tools git
```

### 2. Install WiFi Adapter Firmware (if needed)

For Ralink chipsets (RT5572, RT3070, RT5370) like the Panda PAU09:

```bash
sudo apt update
sudo apt install firmware-ralink
```

After installation, reboot:
```bash
sudo reboot
```

Verify your adapter is detected:
```bash
lsusb
# Should show your WiFi adapter (e.g., "Ralink Technology, Corp.")

iwconfig
# Should show wlan0 (built-in) and wlan1 (external adapter)
```

### 3. Enable I2C (for LCD display)

```bash
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
# Reboot when prompted
```

Test I2C connection (with LCD connected):
```bash
sudo i2cdetect -y 1
# Should show 27 or 3F in the grid
```

### 4. Install Python Dependencies

```bash
pip3 install -r requirements.txt
# Or manually: pip3 install RPLCD
```

### 5. Create Dump Directory

```bash
mkdir -p /home/pi/dump
```

### 6. Configure Hotspot Connection

Edit `wpa_supplicant_hotspot.conf` with your phone's hotspot credentials:

```bash
nano wpa_supplicant_hotspot.conf
```

Change these values:
- `ssid="myhotspotname"` → Your hotspot name
- `psk="myhotspotpassword"` → Your hotspot password
- `country=il` → Your country code (us, gb, de, etc.)

### 7. Configure Target Network

Edit `attack.py` to set your target network:

```bash
nano attack.py
```

Find and modify this line:

```python
target_essid = "eduroam"  # Target specific network
# OR
target_essid = None       # Auto-target strongest signal
```

Examples:
- `target_essid = "eduroam"` - Only attack eduroam networks
- `target_essid = "Starbucks WiFi"` - Only attack Starbucks
- `target_essid = None` - Attack strongest signal (any network)

### 8. Setup Automatic Startup

Configure the Pi to connect to your hotspot on boot:

```bash
crontab -e
```

Add this line:

```
@reboot bash /home/pi/startup.sh
```

### 9. (Optional) Test LCD Display

If you have an LCD connected, test it:

```bash
python3 lcd_display.py
```

This will run through LCD test patterns.

### 10. (Optional) Change Hostname

For easier SSH access without knowing the IP:

```bash
sudo raspi-config
# Navigate to: Network Options → Hostname
# Set a memorable name (e.g., "wardrive-pi")
```

## Usage

### Starting the Attack

1. **Power on the Pi** (it will auto-connect to your hotspot via `startup.sh`)
2. **Enable your phone's hotspot**
3. **SSH into the Pi** from your phone:
   ```bash
   ssh pi@raspberrypi
   # or use your custom hostname
   ssh pi@wardrive-pi
   ```
4. **Run the attack**:
   ```bash
   sudo python3 attack.py
   ```

### Stopping the Attack

Press `Ctrl+C` to gracefully stop the script.

### Analyzing Collected Data

All detected access points are logged to CSV files in `/home/pi/dump/`:
- View with: `cat /home/pi/dump/dump-01.csv`
- Analyze BSSID (MAC addresses), ESSIDs (network names), channels, and signal strengths

## Configuration

Edit these variables in `attack.py` to customize behavior:

```python
# Target Configuration
target_essid = "eduroam"          # Specific network name to target
                                   # Set to None for strongest signal mode

# Attack Configuration
dump_dir = "/home/pi/dump"        # Where to save CSV files
deauth_num_pkts = 100             # Packets per attack (increase for more disruption)
iface = "wlan1"                   # Monitor mode interface (external adapter)

# Inside deauth_from_csv function:
deauth_all = False                # False = one AP, True = all detected APs
```

### LCD Display Status Messages

When the LCD is connected, you'll see real-time status updates:
- **"WiFi Deauth" / "Initializing..."** - Starting up
- **"Scanning" / "WiFi Networks..."** - Scanning for APs
- **"Searching" / "eduroam"** - Looking for target network
- **"Attacking" / "eduroam"** - Sending deauth packets
- **"Not Found" / "eduroam"** - Target not detected
- **"Loop Complete" / "#5"** - Finished cycle #5

## File Descriptions

| File | Purpose |
|------|---------|
| `attack.py` | Main attack script - scans, parses, and deauths with LCD support |
| `lcd_display.py` | LCD control module for 16x2 I2C displays |
| `startup.sh` | Auto-run on boot - connects to hotspot |
| `wifi-connect.sh` | Helper script for wpa_supplicant |
| `wpa_supplicant_hotspot.conf` | WiFi credentials for SSH access |
| `requirements.txt` | Python dependencies (RPLCD) |
| `README.md` | This documentation file |

## Troubleshooting

### Monitor mode not working
```bash
sudo airmon-ng check kill
sudo airmon-ng start wlan1
```

### Can't SSH to Pi
- Verify hotspot is active
- Check Pi is powered on and booted (LED activity)
- Try IP address instead of hostname: `ssh pi@192.168.x.x`
- Use `nmap` to find Pi's IP: `nmap -sn 192.168.x.0/24`

### No APs detected
- Verify monitor mode: `iwconfig wlan1`
- Check adapter supports monitor mode: `iw list`
- Ensure external WiFi adapter is plugged in

### LCD not working
Check I2C connection:
```bash
sudo i2cdetect -y 1
# Should show 27 or 3F if LCD is connected
```

If nothing appears:
- Check wiring (SDA to GPIO2, SCL to GPIO3, VCC to 5V, GND to GND)
- Verify I2C is enabled: `sudo raspi-config` → Interface Options → I2C
- Try different I2C address in `lcd_display.py` (change `0x27` to `0x3F`)
- Test standalone: `python3 lcd_display.py`

The script will work without LCD - it's optional

### Target network not found
If you're targeting a specific network (e.g., "eduroam") and it shows "Not Found":
- Verify the network is actually in range
- Check spelling in `target_essid` (case-insensitive but spelling matters)
- The network must have a valid signal (power > -1 dBm)
- Try scanning manually: `sudo airodump-ng wlan1` to see available networks
- Set `target_essid = None` to test with any network

## Testing Instructions

### Step-by-Step Testing Process

**1. Verify WiFi Adapter Detection**
```bash
# Check USB devices
lsusb | grep -i ralink
# Should show: "Ralink Technology, Corp." or similar

# Check wireless interfaces
iwconfig
# Should show wlan0 (built-in) and wlan1 (external)
```

**2. Test Monitor Mode**
```bash
# Enable monitor mode
sudo airmon-ng start wlan1

# Verify monitor mode is active
iwconfig wlan1
# Should show "Mode:Monitor"

# Check for monitor interface (might create wlan1mon)
iwconfig
```

**3. Test Scanning (Manual)**
```bash
# Start airodump-ng to see available networks
sudo airodump-ng wlan1

# You should see:
# - BSSID column (MAC addresses)
# - PWR column (signal strength)
# - CH column (channels)
# - ESSID column (network names including "eduroam" if in range)

# Press Ctrl+C to stop
```

**4. Test LCD (Optional)**
```bash
# Check I2C connection
sudo i2cdetect -y 1
# Should show "27" or "3F" in the grid

# Run LCD test
python3 lcd_display.py
# Should display test messages on LCD
```

**5. Dry Run Test (without LCD)**
```bash
# Run the attack script
sudo python3 attack.py

# Watch for output:
# - "airodump-ng process started"
# - "Getting latest dump file"
# - "Found target network: eduroam..." (if eduroam in range)
# - "Deauthing eduroam..."

# Press Ctrl+C to stop after one loop
```

**6. Check CSV Output**
```bash
# View collected AP data
ls -lh /home/pi/dump/
cat /home/pi/dump/dump-01.csv

# Should contain columns:
# BSSID, First time seen, Last time seen, channel, Speed, Privacy, Cipher, Authentication, Power, # beacons, # IV, LAN IP, ID-length, ESSID, Key
```

**7. Test Target Filtering**
```bash
# Edit attack.py to test different modes
nano attack.py

# Test 1: Target eduroam
target_essid = "eduroam"
# Run: sudo python3 attack.py
# Should only attack eduroam if found

# Test 2: Target any network
target_essid = None
# Run: sudo python3 attack.py
# Should attack strongest signal
```

### Expected Behavior

**When eduroam is found:**
```
=== Attack Loop 1 ===
Starting airodump-ng scan...
airodump-ng process started
Getting latest dump file
Latest dump: dump-01.csv
Found target network: eduroam (AA:BB:CC:DD:EE:FF) on channel 36, power -45
Deauthing eduroam ( AA:BB:CC:DD:EE:FF ) on channel 36 num of packets: 100 ...
Hopped to channel 36
Delta time = 0:00:03.123456
Loop 1 complete
```

**When eduroam is NOT found:**
```
=== Attack Loop 1 ===
Starting airodump-ng scan...
airodump-ng process started
Getting latest dump file
Latest dump: dump-01.csv
WARNING: Target network 'eduroam' not found!
Loop 1 complete
```

**With LCD connected:**
- Line 1 shows status: "Scanning", "Searching", "Attacking", "Not Found"
- Line 2 shows detail: network name, "10 seconds...", etc.

### Troubleshooting Tests

**Test 1: WiFi adapter not recognized**
```bash
sudo apt update
sudo apt install firmware-ralink
sudo reboot
lsusb | grep -i ralink
```

**Test 2: Monitor mode fails**
```bash
sudo airmon-ng check kill
sudo airmon-ng start wlan1
iwconfig wlan1
```

**Test 3: No networks detected**
```bash
# Test with any network (not just eduroam)
nano attack.py
# Change: target_essid = None
sudo python3 attack.py
```

**Test 4: Permission denied errors**
```bash
# Always run as root
sudo python3 attack.py

# Check if you're root
whoami
# Should output: root
```

### Verification Checklist

Before deploying:
- [ ] lsusb shows WiFi adapter
- [ ] iwconfig shows wlan0 and wlan1
- [ ] sudo airodump-ng wlan1 shows networks
- [ ] sudo i2cdetect -y 1 shows LCD (if using LCD)
- [ ] python3 lcd_display.py works (if using LCD)
- [ ] /home/pi/dump directory exists
- [ ] sudo python3 attack.py runs without errors
- [ ] CSV files created in /home/pi/dump/
- [ ] Deauth packets sent successfully

## Legal & Ethical Considerations

**This tool demonstrates WiFi deauthentication attacks, which:**
- Are **illegal** without explicit authorization
- Violate computer fraud and abuse laws in most countries
- Can disrupt critical services and communications

**Authorized use cases:**
- Penetration testing with signed contracts
- Personal network security testing
- Educational research in controlled lab environments
- Security awareness demonstrations with permission

**Always obtain written permission before testing any network you don't own.**

## License

This project is for educational purposes only. The authors assume no liability for misuse.

## Contributing

Contributions are welcome! Please ensure all code is well-commented and follows the project's coding standards.
