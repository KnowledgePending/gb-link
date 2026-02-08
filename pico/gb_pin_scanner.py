"""
Game Boy Link Cable - PIN SCANNER

This script monitors MULTIPLE GPIO pins simultaneously to find
which pins are actually receiving the signal.

Run this to discover the correct pin mapping.
"""

from machine import Pin
import time

# Scan these pins for any activity
PINS_TO_SCAN = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

# Store pin objects and their last values
pins = {}
last_values = {}
change_counts = {}

print()
print("=" * 50)
print("Game Boy Link Cable - PIN SCANNER")
print("=" * 50)
print(f"Scanning GPIO pins: {PINS_TO_SCAN}")
print()
print("Press buttons on GB. Any pin that changes will be reported.")
print("Look for pins with 8+ changes (one byte = 8 clock pulses)")
print("=" * 50)
print()

# Initialize all pins as inputs with pull-up
for pin_num in PINS_TO_SCAN:
    try:
        pins[pin_num] = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        last_values[pin_num] = pins[pin_num].value()
        change_counts[pin_num] = 0
    except Exception as e:
        print(f"Could not init GP{pin_num}: {e}")

print("Initial pin states:")
for pin_num in sorted(pins.keys()):
    print(f"  GP{pin_num:2d} = {last_values[pin_num]}")
print()
print("Monitoring for changes...")
print()

scan_count = 0
while True:
    # Check each pin for changes
    changes_this_scan = []
    
    for pin_num in pins:
        current = pins[pin_num].value()
        if current != last_values[pin_num]:
            change_counts[pin_num] += 1
            changes_this_scan.append((pin_num, last_values[pin_num], current))
            last_values[pin_num] = current
    
    # Report any changes immediately
    for pin_num, old_val, new_val in changes_this_scan:
        print(f"GP{pin_num:2d}: {old_val} -> {new_val}  (total changes: {change_counts[pin_num]})")
    
    # Every 5 seconds, show summary of any pins that have changed
    scan_count += 1
    if scan_count >= 5000:  # roughly 5 seconds at 1ms per scan
        scan_count = 0
        active_pins = [(p, c) for p, c in change_counts.items() if c > 0]
        if active_pins:
            print()
            print("--- ACTIVE PINS (have changed) ---")
            for pin_num, count in sorted(active_pins, key=lambda x: -x[1]):
                print(f"  GP{pin_num:2d}: {count} changes")
            print("-----------------------------------")
            print()
        else:
            print("... no pin changes detected in last 5 seconds ...")
    
    time.sleep_ms(1)
