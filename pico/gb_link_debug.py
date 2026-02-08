"""
Game Boy Link Cable DEBUG Version

This version monitors raw pin states to help diagnose wiring issues.
Run this first to verify your connections before using the main gb_link.py.

Expected behavior when GB sends data:
- Clock should toggle (idle HIGH, pulses LOW)
- Data should change based on bits being sent
"""

from machine import Pin
import time

# Pin definitions - TRY SWAPPING THESE IF NOT WORKING
PIN_CLOCK = 2    # GP2 - Try swapping with PIN_DATA_IN
PIN_DATA_IN = 3  # GP3 - Data from GB
PIN_DATA_OUT = 4 # GP4 - Data to GB

# Initialize pins
clock_pin = Pin(PIN_CLOCK, Pin.IN, Pin.PULL_UP)
data_in_pin = Pin(PIN_DATA_IN, Pin.IN, Pin.PULL_UP)
data_out_pin = Pin(PIN_DATA_OUT, Pin.OUT, value=1)

# Edge counters
falling_edges = 0
rising_edges = 0

def count_falling(pin):
    global falling_edges
    falling_edges += 1

def count_rising(pin):
    global rising_edges
    rising_edges += 1

print()
print("=" * 50)
print("Game Boy Link Cable - DEBUG MODE")
print("=" * 50)
print(f"Clock pin:    GP{PIN_CLOCK}")
print(f"Data In pin:  GP{PIN_DATA_IN}")
print(f"Data Out pin: GP{PIN_DATA_OUT}")
print("=" * 50)
print()
print("Monitoring pin states every second...")
print("Press buttons on GB to send data.")
print("Look for clock changes when you press buttons.")
print()

# Enable edge counting on clock pin
clock_pin.irq(trigger=Pin.IRQ_FALLING, handler=count_falling)

last_clock = clock_pin.value()
last_data = data_in_pin.value()

while True:
    clock = clock_pin.value()
    data = data_in_pin.value()
    
    # Show current state
    print(f"Clock(GP{PIN_CLOCK})={clock}  Data(GP{PIN_DATA_IN})={data}  "
          f"Falling edges={falling_edges}")
    
    # Detect any changes
    if clock != last_clock:
        print(f"  >>> CLOCK CHANGED: {last_clock} -> {clock}")
        last_clock = clock
    
    if data != last_data:
        print(f"  >>> DATA CHANGED: {last_data} -> {data}")
        last_data = data
    
    if falling_edges > 0:
        print(f"  >>> Got {falling_edges} falling edges!")
        
        # Try to read a byte
        if falling_edges >= 8:
            print("  >>> 8+ edges = at least one byte transferred!")
            falling_edges = 0
    
    time.sleep(1)
