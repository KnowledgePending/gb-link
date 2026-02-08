# Game Boy Link Cable - Pico Firmware

This firmware allows a Raspberry Pi Pico to communicate with a Game Boy/Game Boy Color via the link cable.

Two versions are provided:
- **`gb_link.py`** - MicroPython (easiest to get started)
- **`gb_link.c`** - C SDK (more robust timing)

## Wiring

Connect the cut link cable wires to the Pico via a 5V↔3.3V level shifter:

| Wire Color | Function | Pico Pin |
|------------|----------|----------|
| Black | Ground (GND) | GND |
| Brown | Clock (SC) | GP2 |
| Yellow | Data In (SO from GB) | GP3 |
| Orange | Data Out (SI to GB) | GP4 |
| Red | VCC (5V) | Do not connect |

**Important**: Use bidirectional level shifters between the GB (5V) and Pico (3.3V)!

## Option A: MicroPython (Easiest)

### Setup

1. Download MicroPython for Pico: https://micropython.org/download/rp2-pico/
2. Hold BOOTSEL, connect Pico via USB, copy the `.uf2` file
3. Copy `gb_link.py` to the Pico as `main.py`:

```bash
# Using mpremote (pip install mpremote)
mpremote cp gb_link.py :main.py

# Or use Thonny IDE to copy the file
```

### Running

The script runs automatically on boot. Connect via serial terminal to see output.

## Option B: C SDK (More Robust)

### Prerequisites

1. Raspberry Pi Pico SDK installed
2. CMake 3.13+
3. ARM GCC toolchain

### Build Steps

```bash
# Set PICO_SDK_PATH if not already set
export PICO_SDK_PATH=/path/to/pico-sdk

# Create build directory
cd pico
mkdir build
cd build

# Configure and build
cmake ..
make
```

### Flashing

1. Hold the BOOTSEL button on the Pico
2. Connect Pico to computer via USB
3. Release BOOTSEL - Pico will appear as a USB drive
4. Copy `gb_link.uf2` to the Pico drive
5. Pico will reboot and start running

## Usage

1. Flash the firmware to your Pico
2. Connect the link cable wires to the Pico (via level shifters)
3. Open a serial terminal at 115200 baud:
   ```bash
   # macOS
   screen /dev/tty.usbmodem* 115200
   
   # Linux
   screen /dev/ttyACM0 115200
   
   # Or use minicom, picocom, etc.
   ```
4. Run the test ROM on your Game Boy
5. Press buttons on the GB to send data
6. Watch received bytes appear on the serial terminal

## Expected Output

When the Game Boy sends bytes using the test ROM:

```
================================
Game Boy Link Cable Receiver
================================
Pins:
  GP2 - Clock (Brown)
  GP3 - Data In (Yellow)
  GP4 - Data Out (Orange)
  GND - Ground (Black)
================================
Waiting for data from Game Boy...

[1] RX: 0x00 (dec:   0, bin: 00000000)
[2] RX: 0xFF (dec: 255, bin: 11111111)
[3] RX: 0xAA (dec: 170, bin: 10101010)
[4] RX: 0x55 (dec:  85, bin: 01010101)
```

## Troubleshooting

### No data received
- Check level shifter connections
- Verify wire colors match the pinout (your cable may differ)
- Try swapping Brown/Yellow wires (clock vs data)
- Make sure GB is in master mode (using internal clock)

### Garbled data
- Check clock polarity - try adding `gpio_pull_down()` instead of pull-up
- Verify baud rate in serial terminal is 115200

### Inverted bit patterns
- The data line polarity may be inverted
- Try inverting the data bit in the ISR: `uint8_t bit = gpio_get(PIN_DATA_IN) ? 0 : 1;`
