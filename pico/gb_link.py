"""
Game Boy Link Cable Receiver for Raspberry Pi Pico (MicroPython)

Receives and sends data over the Game Boy link cable protocol.

Wiring (via 5V↔3.3V level shifter):
  GP2 - Clock input (Brown wire - SC from GB)
  GP3 - Data input (Yellow wire - SO from GB)  
  GP4 - Data output (Orange wire - SI to GB)
  GND - Ground (Black wire)

Protocol:
  - Clock idles HIGH
  - Data sampled on falling edge of clock
  - MSB first, 8 bits per transfer
  - ~8kHz clock rate

Usage:
  1. Copy this file to your Pico as main.py
  2. Connect to Pico via serial terminal (115200 baud)
  3. Run test ROM on Game Boy
  4. Press buttons to send data
"""

from machine import Pin
import time

# Pin definitions
PIN_CLOCK = 2    # GP2 - Clock input (Brown)
PIN_DATA_IN = 3  # GP3 - Data from GB (Yellow)
PIN_DATA_OUT = 4 # GP4 - Data to GB (Orange)

# Receive state
rx_byte = 0
rx_bit_count = 0
byte_ready = False
last_received_byte = 0

# Transmit state
tx_byte = 0x00
tx_bit_count = 0

# Statistics
byte_count = 0

# Initialize pins
clock_pin = Pin(PIN_CLOCK, Pin.IN, Pin.PULL_UP)
data_in_pin = Pin(PIN_DATA_IN, Pin.IN, Pin.PULL_UP)
data_out_pin = Pin(PIN_DATA_OUT, Pin.OUT, value=1)  # Idle high


def clock_falling_handler(pin):
    """
    IRQ handler called on each falling edge of the clock.
    Reads one bit from GB and shifts out one bit to GB.
    """
    global rx_byte, rx_bit_count, byte_ready, last_received_byte
    global tx_byte, tx_bit_count, byte_count
    
    # Read data bit from GB (MSB first)
    bit = data_in_pin.value()
    rx_byte = (rx_byte << 1) | bit
    rx_bit_count += 1
    
    # Shift out our data bit to GB (MSB first)
    out_bit = (tx_byte >> (7 - tx_bit_count)) & 0x01
    data_out_pin.value(out_bit)
    tx_bit_count += 1
    
    if rx_bit_count >= 8:
        # Complete byte received
        last_received_byte = rx_byte
        byte_ready = True
        byte_count += 1
        rx_byte = 0
        rx_bit_count = 0
        tx_bit_count = 0


def set_tx_byte(value):
    """Set the byte to send back to Game Boy on next transfer."""
    global tx_byte
    tx_byte = value & 0xFF


def format_binary(value):
    """Format a byte as binary string."""
    return ''.join('1' if value & (1 << (7-i)) else '0' for i in range(8))


def main():
    global byte_ready, last_received_byte
    
    print()
    print("=" * 40)
    print("Game Boy Link Cable Receiver (MicroPython)")
    print("=" * 40)
    print("Pins:")
    print(f"  GP{PIN_CLOCK} - Clock (Brown)")
    print(f"  GP{PIN_DATA_IN} - Data In (Yellow)")
    print(f"  GP{PIN_DATA_OUT} - Data Out (Orange)")
    print("  GND - Ground (Black)")
    print("=" * 40)
    print("Waiting for data from Game Boy...")
    print()
    
    # Enable interrupt on clock falling edge
    clock_pin.irq(trigger=Pin.IRQ_FALLING, handler=clock_falling_handler)
    
    # Set initial TX byte (echoed back to GB)
    set_tx_byte(0x00)
    
    while True:
        if byte_ready:
            byte_ready = False
            
            # Print received byte in multiple formats
            print(f"[{byte_count}] RX: 0x{last_received_byte:02X} "
                  f"(dec: {last_received_byte:3d}, "
                  f"bin: {format_binary(last_received_byte)})")
            
            # Echo received byte back (for testing)
            # Change this to send different responses
            set_tx_byte(last_received_byte)
        
        # Small delay to prevent busy-waiting
        time.sleep_us(100)


if __name__ == "__main__":
    main()
