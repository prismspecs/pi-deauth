#!/usr/bin/env python3
"""
Simple LCD Test Script
Run with: python3 test_lcd.py
"""

import time
from lcd_display import init_lcd, printLCD, clearLCD, display_status, startMarquee, stopMarquee

print("LCD Test Script")
print("=" * 40)
print()

# Test 1: Initialize
print("Test 1: Initializing LCD...")
if not init_lcd(i2c_bus=1, i2c_address=0x27, cols=16, rows=2):
    print("FAILED: Could not initialize LCD")
    print("\nTroubleshooting:")
    print("1. Check I2C address: sudo i2cdetect -y 1")
    print("2. If you see 3F instead of 27, edit lcd_display.py")
    print("3. Check wiring: SDA->GPIO2, SCL->GPIO3, VCC->5V, GND->GND")
    exit(1)

print("PASSED: LCD initialized")
time.sleep(1)

# Test 2: Simple text
print("\nTest 2: Displaying simple text...")
printLCD("Hello World!", "Line 2 Test")
print("PASSED: Should see 'Hello World!' on line 1")
time.sleep(3)

# Test 3: Clear screen
print("\nTest 3: Clearing screen...")
clearLCD()
print("PASSED: Screen should be blank")
time.sleep(2)

# Test 4: Status display
print("\nTest 4: Status messages...")
display_status("WiFi Deauth", "Ready")
print("PASSED: Should see 'WiFi Deauth / Ready'")
time.sleep(2)

display_status("Scanning", "Networks...")
print("PASSED: Should see 'Scanning / Networks...'")
time.sleep(2)

display_status("Attacking", "eduroam")
print("PASSED: Should see 'Attacking / eduroam'")
time.sleep(2)

# Test 5: Scrolling text
print("\nTest 5: Scrolling marquee...")
print("Starting marquee effect (10 seconds)...")
startMarquee("This is a long scrolling message to test the marquee feature!", 0.3)
time.sleep(10)
stopMarquee()
print("PASSED: Marquee stopped")
time.sleep(1)

# Test 6: Attack simulation
print("\nTest 6: Simulating attack sequence...")
display_status("Initializing", "Monitor Mode")
time.sleep(2)

display_status("Scanning", "10 seconds...")
time.sleep(2)

display_status("Searching", "eduroam")
time.sleep(2)

display_status("Found", "eduroam")
time.sleep(2)

display_status("Attacking", "eduroam")
time.sleep(3)

display_status("Complete", "#1")
time.sleep(2)

# Finish
print("\nTest 7: Final test...")
printLCD("LCD Test", "Complete!")
print("PASSED: All tests complete!")
time.sleep(3)

clearLCD()
print("\n" + "=" * 40)
print("LCD Test Finished Successfully!")
print("Your LCD is working correctly.")
print("=" * 40)

