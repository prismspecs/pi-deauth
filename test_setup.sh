#!/bin/bash
# WiFi Deauth Setup Test Script
# Run this to verify your hardware and software is configured correctly

echo "=========================================="
echo "WiFi Deauth Setup Test Script"
echo "=========================================="
echo ""

# Color codes for output (optional, works in most terminals)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# LCD helper function
LCD_INITIALIZED=0
update_lcd() {
    python3 - "$1" "$2" "$LCD_INITIALIZED" <<'EOF' 2>/dev/null
import sys
try:
    from lcd_display import init_lcd, display_status
    line1 = sys.argv[1] if len(sys.argv) > 1 else ""
    line2 = sys.argv[2] if len(sys.argv) > 2 else ""
    initialized = sys.argv[3] if len(sys.argv) > 3 else "0"
    
    if initialized == "0":
        init_lcd()
    
    if line1:
        display_status(line1, line2)
except:
    pass
EOF
    LCD_INITIALIZED=1
}

# Initialize LCD
update_lcd "System Test" "Starting..."
sleep 1

# Function to print test results
test_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED++))
}

test_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED++))
}

test_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo "Test 1: Checking for root privileges..."
update_lcd "Test 1/9" "Root check..."
if [ "$EUID" -eq 0 ]; then
    test_pass "Running as root"
else
    test_fail "Not running as root. Run with: sudo bash test_setup.sh"
    update_lcd "FAILED" "Need root"
    exit 1
fi

echo ""
echo "Test 2: Checking WiFi adapters..."
update_lcd "Test 2/9" "WiFi adapters..."
if iwconfig 2>/dev/null | grep -q "wlan0"; then
    test_pass "Built-in WiFi (wlan0) detected"
else
    test_fail "Built-in WiFi (wlan0) not found"
fi

if iwconfig 2>/dev/null | grep -q "wlan1"; then
    test_pass "External WiFi adapter (wlan1) detected"
else
    test_fail "External WiFi adapter (wlan1) not found"
    echo "       Make sure USB WiFi adapter is plugged in"
fi

echo ""
echo "Test 3: Checking USB WiFi adapter..."
update_lcd "Test 3/9" "USB adapter..."
if lsusb | grep -qi "ralink\|realtek\|atheros"; then
    test_pass "WiFi adapter chipset detected"
    lsusb | grep -i "ralink\|realtek\|atheros"
else
    test_warn "Could not identify WiFi adapter chipset"
    echo "       Your adapter might still work"
fi

echo ""
echo "Test 4: Checking required software..."
update_lcd "Test 4/9" "Software..."
if command -v airmon-ng &> /dev/null; then
    test_pass "airmon-ng installed"
else
    test_fail "airmon-ng not installed. Run: sudo apt install aircrack-ng"
fi

if command -v airodump-ng &> /dev/null; then
    test_pass "airodump-ng installed"
else
    test_fail "airodump-ng not installed. Run: sudo apt install aircrack-ng"
fi

if command -v aireplay-ng &> /dev/null; then
    test_pass "aireplay-ng installed"
else
    test_fail "aireplay-ng not installed. Run: sudo apt install aircrack-ng"
fi

if command -v python3 &> /dev/null; then
    test_pass "Python 3 installed"
else
    test_fail "Python 3 not installed. Run: sudo apt install python3"
fi

echo ""
echo "Test 5: Checking Python dependencies..."
update_lcd "Test 5/9" "Python..."
if python3 -c "import RPLCD" 2>/dev/null; then
    test_pass "RPLCD library installed (for LCD)"
else
    test_warn "RPLCD library not installed (LCD will not work)"
    echo "       Install with: pip3 install RPLCD"
fi

echo ""
echo "Test 6: Checking directories..."
update_lcd "Test 6/9" "Directories..."
if [ -d "/home/pi/dump" ]; then
    test_pass "Dump directory exists"
else
    test_fail "Dump directory missing. Create with: mkdir -p /home/pi/dump"
fi

if [ -f "attack.py" ]; then
    test_pass "attack.py found"
else
    test_fail "attack.py not found. Are you in the correct directory?"
fi

echo ""
echo "Test 7: Checking I2C (for LCD)..."
update_lcd "Test 7/9" "I2C / LCD..."
if [ -e "/dev/i2c-1" ]; then
    test_pass "I2C interface enabled"
    
    if command -v i2cdetect &> /dev/null; then
        echo "       Running i2cdetect..."
        if i2cdetect -y 1 2>/dev/null | grep -q "27\|3F"; then
            test_pass "LCD detected on I2C bus"
        else
            test_warn "No LCD detected on I2C bus (optional)"
            echo "       This is OK if you're not using an LCD"
        fi
    else
        test_warn "i2c-tools not installed"
        echo "       Install with: sudo apt install i2c-tools"
    fi
else
    test_warn "I2C not enabled (required for LCD)"
    echo "       Enable with: sudo raspi-config -> Interface Options -> I2C"
fi

echo ""
echo "Test 8: Testing monitor mode..."
update_lcd "Test 8/9" "Monitor mode..."
echo "       Enabling monitor mode on wlan1..."
airmon-ng start wlan1 > /dev/null 2>&1
sleep 2

if iwconfig 2>/dev/null | grep -q "Mode:Monitor"; then
    test_pass "Monitor mode enabled successfully"
else
    test_fail "Monitor mode could not be enabled"
    echo "       Your adapter may not support monitor mode"
fi

echo ""
echo "Test 9: Quick scan test (10 seconds)..."
update_lcd "Test 9/9" "Scanning 10s..."
SCAN_OUTPUT="/tmp/airodump_test"

# Clean up any old scan files
rm -f "${SCAN_OUTPUT}"*.csv > /dev/null 2>&1

# Run scan for 10 seconds
timeout 10 airodump-ng wlan1 -w "$SCAN_OUTPUT" --output-format csv > /dev/null 2>&1
sleep 1
killall airodump-ng > /dev/null 2>&1
sleep 1

# Check if CSV was created and contains data
if [ -f "${SCAN_OUTPUT}-01.csv" ]; then
    # Count lines that look like MAC addresses (AP entries)
    AP_COUNT=$(grep -c "^[0-9A-Fa-f][0-9A-Fa-f]:[0-9A-Fa-f][0-9A-Fa-f]:" "${SCAN_OUTPUT}-01.csv" 2>/dev/null || echo 0)
    
    if [ "$AP_COUNT" -gt 0 ]; then
        test_pass "Scan test successful - detected $AP_COUNT access points"
    else
        # CSV exists but no APs found - this is still okay, just means no networks nearby
        test_warn "Scan ran but no access points detected (you may be in a low-signal area)"
        echo "       This is okay - the script will work when networks are present"
    fi
    rm -f "${SCAN_OUTPUT}"*.csv > /dev/null 2>&1
else
    test_fail "Scan test failed - CSV file not created"
    echo "       This might indicate an issue with monitor mode or airodump-ng"
fi

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "All critical tests passed!"
    echo "You can now run: sudo python3 attack.py"
    update_lcd "All Tests" "PASSED"
    sleep 2
    update_lcd "Ready to" "Attack!"
else
    echo "Some tests failed. Please address the issues above."
    echo "Check the README.md for troubleshooting steps."
    update_lcd "$PASSED Pass" "$FAILED Fail"
    sleep 2
    update_lcd "Check" "Terminal"
fi

sleep 2
python3 - <<'EOF' 2>/dev/null
try:
    from lcd_display import clearLCD
    clearLCD()
except:
    pass
EOF

echo ""



