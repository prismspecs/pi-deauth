"""
LCD Display Module for 16x2 I2C LCD Screen

This module provides functions to control a 16x2 character LCD display
connected via I2C (typically address 0x27). It's designed for use with
the Raspberry Pi and PCF8574 I2C backpack.

Hardware Setup:
- 16x2 LCD with I2C backpack (PCF8574)
- Default I2C address: 0x27 (some use 0x3F)
- Connect to Raspberry Pi I2C pins (SDA/SCL)

Installation:
    sudo apt-get install python3-smbus python3-dev i2c-tools
    sudo pip3 install RPLCD

Enable I2C:
    sudo raspi-config
    # Navigate to: Interface Options → I2C → Enable

Test I2C connection:
    sudo i2cdetect -y 1
    # Should show 27 or 3F in the output grid

Usage:
    from lcd_display import clearLCD, printLCD, startMarquee
    
    printLCD("Hello", "World")
    startMarquee("This is a long scrolling message")
"""

import threading
import time

try:
    from RPLCD.i2c import CharLCD
except ImportError:
    print("WARNING: RPLCD library not installed. LCD functions will not work.")
    print("Install with: sudo pip3 install RPLCD")
    CharLCD = None

# Global LCD object
lcd = None
marquee_thread = None
marquee_running = False

def init_lcd(i2c_bus=1, i2c_address=0x27, cols=16, rows=2):
    """
    Initialize the LCD display.
    
    Args:
        i2c_bus (int): I2C bus number (1 for newer Pi models, 0 for very old ones)
        i2c_address (int): I2C address of the LCD (0x27 or 0x3F typically)
        cols (int): Number of columns (typically 16)
        rows (int): Number of rows (typically 2)
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    global lcd
    
    if CharLCD is None:
        print("ERROR: RPLCD library not available")
        return False
    
    try:
        lcd = CharLCD(
            i2c_expander='PCF8574',
            address=i2c_address,
            port=i2c_bus,
            cols=cols,
            rows=rows,
            dotsize=8,
            charmap='A02',
            auto_linebreaks=True,
            backlight_enabled=True
        )
        lcd.clear()
        return True
    except Exception as e:
        print(f"ERROR: Failed to initialize LCD: {e}")
        print("Check I2C connection with: sudo i2cdetect -y 1")
        return False


def clearLCD():
    """
    Clear the LCD screen completely.
    
    This turns off all characters and moves cursor to home position.
    """
    global lcd
    if lcd is not None:
        try:
            lcd.clear()
        except Exception as e:
            print(f"ERROR clearing LCD: {e}")


def printLCD(line1, line2=''):
    """
    Print text on the LCD screen (up to 2 lines).
    
    This function clears the screen first, then prints the provided text.
    Text longer than 16 characters will be truncated.
    
    Args:
        line1 (str): Text for the first line (max 16 chars)
        line2 (str): Text for the second line (max 16 chars, optional)
    
    Example:
        printLCD("WiFi Deauth", "Starting...")
        printLCD("Target: eduroam")
    """
    global lcd
    if lcd is not None:
        try:
            lcd.clear()
            # Truncate to LCD width (16 chars)
            lcd.write_string(line1[:16])
            if line2:
                lcd.crlf()  # Move to second line
                lcd.write_string(line2[:16])
        except Exception as e:
            print(f"ERROR printing to LCD: {e}")


def startMarquee(text, interval_time=0.5):
    """
    Start a scrolling marquee effect on the first line of the LCD.
    
    This creates a scrolling text effect for messages longer than 16 characters.
    The text will continuously scroll from right to left. Call stopMarquee() to stop.
    
    Args:
        text (str): The text to scroll (can be any length)
        interval_time (float): Time between scroll steps in seconds (default: 0.5)
    
    Returns:
        bool: True if marquee started successfully, False otherwise
    
    Example:
        startMarquee("This is a very long message that will scroll across the screen")
        time.sleep(10)  # Let it scroll for 10 seconds
        stopMarquee()
    """
    global lcd, marquee_thread, marquee_running
    
    if lcd is None:
        return False
    
    # Stop any existing marquee
    stopMarquee()
    
    marquee_running = True
    
    def marquee_worker():
        """Worker thread that handles the scrolling animation."""
        global marquee_running
        
        # Pad text with spaces for smooth wraparound
        padded_text = text + "    "
        max_start = len(padded_text)
        current_position = 0
        
        while marquee_running:
            try:
                # Clear and display current window of text
                lcd.clear()
                display_text = padded_text[current_position:current_position + 16]
                
                # Handle wraparound
                if len(display_text) < 16:
                    display_text += padded_text[:16 - len(display_text)]
                
                lcd.write_string(display_text[:16])
                
                # Advance position
                current_position = (current_position + 1) % max_start
                
                time.sleep(interval_time)
                
            except Exception as e:
                print(f"ERROR in marquee: {e}")
                marquee_running = False
                break
    
    # Start marquee in background thread
    marquee_thread = threading.Thread(target=marquee_worker, daemon=True)
    marquee_thread.start()
    return True


def stopMarquee():
    """
    Stop any running marquee effect.
    
    This halts the scrolling animation and clears the screen.
    Safe to call even if no marquee is running.
    """
    global marquee_running, marquee_thread
    
    if marquee_running:
        marquee_running = False
        if marquee_thread is not None:
            marquee_thread.join(timeout=2)  # Wait up to 2 seconds for thread to finish
        clearLCD()


def display_status(status, detail=''):
    """
    Display a status message with optional detail line.
    
    Helper function for common status displays during operation.
    
    Args:
        status (str): Main status message (line 1)
        detail (str): Optional detail message (line 2)
    
    Example:
        display_status("Scanning...", "Ch: 6")
        display_status("Attacking", "eduroam")
        display_status("Idle", "Waiting...")
    """
    printLCD(status, detail)


# Test function for standalone testing
def test_lcd():
    """
    Test all LCD functions.
    
    Run this script directly to test your LCD connection:
        python3 lcd_display.py
    """
    print("Testing LCD display...")
    
    if not init_lcd():
        print("Failed to initialize LCD")
        return
    
    print("Test 1: Simple text")
    printLCD("LCD Test", "Hello World!")
    time.sleep(3)
    
    print("Test 2: Clearing display")
    clearLCD()
    time.sleep(1)
    
    print("Test 3: Status display")
    display_status("WiFi Deauth", "Ready")
    time.sleep(3)
    
    print("Test 4: Marquee effect")
    startMarquee("This is a long scrolling message that demonstrates the marquee effect!", 0.3)
    time.sleep(15)
    stopMarquee()
    
    print("Test 5: Final message")
    printLCD("Test Complete", "Success!")
    time.sleep(3)
    
    clearLCD()
    print("LCD test finished!")


if __name__ == "__main__":
    # Run test when script is executed directly
    test_lcd()



