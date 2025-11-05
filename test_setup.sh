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
if [ "$EUID" -eq 0 ]; then
    test_pass "Running as root"
else
    test_fail "Not running as root. Run with: sudo bash test_setup.sh"
    exit 1
fi

echo ""
echo "Test 2: Checking WiFi adapters..."
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
if lsusb | grep -qi "ralink\|realtek\|atheros"; then
    test_pass "WiFi adapter chipset detected"
    lsusb | grep -i "ralink\|realtek\|atheros"
else
    test_warn "Could not identify WiFi adapter chipset"
    echo "       Your adapter might still work"
fi

echo ""
echo "Test 4: Checking required software..."
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
if python3 -c "import RPLCD" 2>/dev/null; then
    test_pass "RPLCD library installed (for LCD)"
else
    test_warn "RPLCD library not installed (LCD will not work)"
    echo "       Install with: pip3 install RPLCD"
fi

echo ""
echo "Test 6: Checking directories..."
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
echo "Test 9: Quick scan test (5 seconds)..."
SCAN_OUTPUT="/tmp/airodump_test"
timeout 5 airodump-ng wlan1 -w "$SCAN_OUTPUT" --output-format csv > /dev/null 2>&1
killall airodump-ng > /dev/null 2>&1

if [ -f "${SCAN_OUTPUT}-01.csv" ]; then
    AP_COUNT=$(grep -c "^[0-9A-Fa-f][0-9A-Fa-f]:" "${SCAN_OUTPUT}-01.csv" 2>/dev/null || echo 0)
    if [ "$AP_COUNT" -gt 0 ]; then
        test_pass "Scan test successful - detected $AP_COUNT access points"
    else
        test_warn "Scan ran but no access points detected"
    fi
    rm -f "${SCAN_OUTPUT}"*.csv > /dev/null 2>&1
else
    test_fail "Scan test failed"
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
else
    echo "Some tests failed. Please address the issues above."
    echo "Check the README.md for troubleshooting steps."
fi

echo ""



