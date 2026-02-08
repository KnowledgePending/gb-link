"""
Game Boy Link Cable - WIRE IDENTIFICATION

This script helps identify which wire is which by testing each one.

PROCEDURE:
1. Connect Pico VBUS (pin 40, 5V) to level shifter HV reference
2. Connect Pico 3V3 (pin 36) to level shifter LV reference  
3. Connect Pico GND to level shifter GND
4. Connect ONE unknown wire at a time to HV1
5. Watch which GPIO shows activity when pressing GB buttons

Run this, then connect wires one at a time to HV1 while pressing
buttons on the GB. The wire that shows 8+ changes is CLOCK.
"""

from machine import Pin
import time

# We're only monitoring LV1 output (connected to GP2)
# Connect each unknown wire to HV1 one at a time

TEST_PIN = 2  # GP2 connected to LV1

pin = Pin(TEST_PIN, Pin.IN, Pin.PULL_UP)
changes = 0
last_val = pin.value()

print()
print("=" * 50)
print("WIRE IDENTIFICATION TEST")
print("=" * 50)
print()
print("Setup:")
print("  1. Level shifter HV ← Pico VBUS (pin 40, 5V)")
print("  2. Level shifter LV ← Pico 3V3 (pin 36)")
print("  3. Level shifter GND ← Pico GND")
print("  4. Level shifter LV1 → GP2")
print()
print("Test each colored wire ONE AT A TIME:")
print("  - Connect wire to HV1")
print("  - Press A button on Game Boy several times")
print("  - Check if changes are detected below")
print()
print("CLOCK wire = 8 changes per button press")
print("DATA wire = changes, but pattern varies")
print("POWER wire = no changes, constant high or low")
print("GROUND wire = stays 0")
print()
print("=" * 50)
print(f"Monitoring GP{TEST_PIN}...")
print("=" * 50)
print()

while True:
    val = pin.value()
    if val != last_val:
        changes += 1
        print(f"Change #{changes}: {last_val} -> {val}")
        last_val = val
        
        # Every 8 changes, note it (one byte = 8 clock pulses)
        if changes % 8 == 0:
            print(f"  ^^^ {changes} changes = {changes // 8} byte(s) worth of clock pulses")
    
    time.sleep_us(100)
