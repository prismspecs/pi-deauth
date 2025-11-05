# Quick Start Guide

## Current Status - What You Need

Based on your test results, here's what you need to do:

### 1. You Need a WiFi Adapter

**CRITICAL: The RTL2838 DVB-T device is a TV tuner, not a WiFi adapter!**

You need to purchase a USB WiFi adapter that supports monitor mode:

**Recommended (Tested):**
- Panda PAU09 (RT5572 chipset) - About $15-20
- Alfa AWUS036NH (RTL8187 chipset) - About $30-40

**Budget Options:**
- Any adapter with RT3070, RT5370, or Atheros AR9271 chipset

**Where to Buy:**
- Amazon: Search "Panda PAU09" or "Alfa AWUS036NH"
- eBay: Search "RT5572 WiFi adapter"
- Make sure it explicitly says "monitor mode" or "packet injection" support

### 2. Install All Software

Once you have a WiFi adapter, run the installation script:

```bash
cd ~/pi-deauth
sudo bash install.sh
```

This single command will install:
- aircrack-ng (airodump-ng, aireplay-ng, airmon-ng)
- Python packages (RPLCD for LCD)
- WiFi firmware (Ralink, Realtek, Atheros)
- Create dump directory
- Configure I2C

### 3. Reboot

```bash
sudo reboot
```

### 4. Test Again

```bash
cd ~/pi-deauth
sudo bash test_setup.sh
```

You should see:
- [PASS] External WiFi adapter (wlan1) detected
- [PASS] Monitor mode enabled successfully
- [PASS] Scan test successful

### 5. Run the Attack

```bash
sudo python3 attack.py
```

## What Your Test Results Mean

```
[PASS] Built-in WiFi (wlan0) detected          ✓ Good
[FAIL] External WiFi adapter (wlan1) not found  ✗ Need WiFi adapter
[PASS] WiFi adapter chipset detected            ✗ This is a TV tuner, not WiFi
[FAIL] airmon-ng not installed                  ✗ Run install.sh
[FAIL] airodump-ng not installed                ✗ Run install.sh
[FAIL] aireplay-ng not installed                ✗ Run install.sh
[PASS] Python 3 installed                       ✓ Good
[WARN] RPLCD library not installed              ✗ Run install.sh
[FAIL] Dump directory missing                   ✗ Run install.sh
[PASS] attack.py found                          ✓ Good
[PASS] I2C interface enabled                    ✓ Good
[PASS] LCD detected on I2C bus                  ✓ Good (LCD working!)
[FAIL] Monitor mode could not be enabled        ✗ Need WiFi adapter
[FAIL] Scan test failed                         ✗ Need WiFi adapter
```

## Installation Command (One-Liner)

After you get a WiFi adapter:

```bash
cd ~/pi-deauth && sudo bash install.sh && sudo reboot
```

Then after reboot:

```bash
cd ~/pi-deauth && sudo bash test_setup.sh
```

If all tests pass:

```bash
sudo python3 attack.py
```

## Expected Timeline

1. **Order WiFi adapter** - 2-5 days shipping
2. **Plug it in and run install.sh** - 5 minutes
3. **Reboot** - 1 minute
4. **Run test_setup.sh** - 30 seconds
5. **Run attack.py** - Ready to go!

## Common Questions

**Q: Can I use the built-in WiFi?**
A: No. The Raspberry Pi's built-in WiFi does not support monitor mode.

**Q: What about the RTL2838 DVB-T device I have?**
A: That's a TV tuner dongle for watching digital TV. It cannot be used for WiFi.

**Q: Do I need the LCD?**
A: No, it's optional. The script works fine without it. (But yours is detected and working!)

**Q: Which WiFi adapter should I buy?**
A: Panda PAU09 (RT5572) is the cheapest reliable option. Alfa AWUS036NH is more powerful but more expensive.

**Q: Will any USB WiFi adapter work?**
A: No. Most consumer adapters don't support monitor mode. Stick to the recommended models.

## After You Get the WiFi Adapter

Run these commands in order:

```bash
# 1. Install everything
cd ~/pi-deauth
sudo bash install.sh

# 2. Reboot
sudo reboot

# 3. After reboot, test
cd ~/pi-deauth
sudo bash test_setup.sh

# 4. If tests pass, configure target
nano attack.py
# Set: target_essid = "eduroam"  (or None for any network)

# 5. Run attack
sudo python3 attack.py

# 6. Stop with Ctrl+C when done
```

## Current Working Features

Good news! These are already working:
- Python 3 installed
- LCD detected and ready to use
- I2C enabled
- Script files in place

You just need:
1. WiFi adapter (hardware purchase)
2. Software installation (run install.sh)

## Budget Breakdown

- **Panda PAU09**: ~$15-20 on Amazon
- **Alfa AWUS036NH**: ~$30-40 on Amazon
- **Generic RT5370**: ~$10-15 on eBay (less reliable)

Your LCD is already working, so no additional cost there!

## Next Steps

1. Order a compatible WiFi adapter
2. Wait for delivery
3. Plug it in
4. Run: `sudo bash install.sh`
5. Run: `sudo reboot`
6. Run: `sudo bash test_setup.sh`
7. Run: `sudo python3 attack.py`

That's it!



