# Game Boy Link Cable Communication with Raspberry Pi Pico

Bidirectional communication between a Game Boy / Game Boy Color and a Raspberry Pi Pico using the link cable protocol.

## Project Structure

```
gb-link/
├── primary.c           # GB ROM - Original send-only test
├── secondary.c         # GB ROM - Bidirectional with RX display
├── Makefile            # Build GB ROMs with GBDK
├── pico/
│   ├── gb_link.c       # Pico firmware (bit-banging)
│   ├── CMakeLists.txt  # Pico SDK build config
│   ├── pico_sdk_import.cmake
│   └── README.md       # Pico-specific instructions
└── plans/
    └── gb-link-pico-plan.md  # Detailed design document
```

## Hardware Requirements

- Game Boy or Game Boy Color
- Link cable (with one end cut off)
- Raspberry Pi Pico
- Bidirectional 5V ↔ 3.3V level shifter
- Flash cart (e.g., EverDrive, GB USB 64M Smart Card) to run test ROMs

## Wiring

### Link Cable Pinout (from your measurements)

| Wire Color | Function | Description |
|------------|----------|-------------|
| Black | GND | Ground (connected to sheath) |
| Red | VCC | 5V power from Game Boy |
| Brown | SC | Serial Clock |
| Yellow | SO | Serial Out (data FROM Game Boy) |
| Orange | SI | Serial In (data TO Game Boy) |

### Pico Connections (via level shifter)

```
Game Boy          Level Shifter         Pico
─────────────────────────────────────────────
Black  (GND)  ────── GND ────────────── GND
Brown  (SC)   ────── HV ──── LV ─────── GP2
Yellow (SO)   ────── HV ──── LV ─────── GP3
Orange (SI)   ────── HV ──── LV ─────── GP4
Red    (VCC)  ────── (do not connect to Pico)
```

## Protocol Overview

The Game Boy uses a synchronous serial protocol similar to SPI:

- **Clock**: Idle HIGH, ~8 kHz (normal speed)
- **Data**: MSB first, sampled on falling clock edge
- **Transfer**: Full duplex - both devices send AND receive simultaneously
- **Size**: 8 bits per transaction

### Timing Diagram

```
Clock (SC):  ─────┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌─────
                  └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘   └───┘
                  
Data (SO/SI): ──< D7 >─< D6 >─< D5 >─< D4 >─< D3 >─< D2 >─< D1 >─< D0 >──────
```

## Building the Game Boy ROMs

### Prerequisites

Install GBDK: https://github.com/gbdk-2020/gbdk-2020/releases

### Build

```bash
# Adjust GBDK path if needed
export GBDK=/opt/gbdk

# Build both ROMs
make

# Or build individually
make primary.gb
make secondary.gb
```

### ROMs

- **primary.gb**: Simple send-only test (TX 0x00, 0xFF, 0xAA, 0x55)
- **secondary.gb**: Bidirectional test showing both TX and RX values

## Building the Pico Firmware

See [pico/README.md](pico/README.md) for detailed build instructions.

```bash
cd pico
mkdir build && cd build
cmake ..
make
```

Copy `gb_link.uf2` to your Pico.

## Testing

### Step 1: Verify Receive (GB → Pico)

1. Flash `gb_link.uf2` to Pico
2. Connect link cable wires to Pico (via level shifter)
3. Open serial terminal: `screen /dev/tty.usbmodem* 115200`
4. Run `primary.gb` on Game Boy
5. Press A - should see `RX: 0x00` on terminal
6. Press B - should see `RX: 0xFF`

### Step 2: Test Bidirectional

1. Run `secondary.gb` on Game Boy instead
2. Press A - GB displays TX:00 RX:xx where xx is what Pico sent back
3. The Pico firmware echoes received bytes by default

### Step 3: Custom Communication

Modify `set_tx_byte()` calls in `pico/gb_link.c` to send your own data.

## Test Patterns

| Button | Value | Binary | Purpose |
|--------|-------|--------|---------|
| A | 0x00 | 00000000 | All zeros |
| B | 0xFF | 11111111 | All ones |
| SELECT | 0xAA | 10101010 | Alternating A |
| START | 0x55 | 01010101 | Alternating B |
| UP | Counter | Varies | Sequential test |

## Troubleshooting

### No data received on Pico

1. **Check wiring**: Verify level shifter connections
2. **Swap wires**: Your Brown/Yellow might be swapped - try exchanging GP2 and GP3
3. **Check GB ROM**: Make sure the ROM is running and you're pressing buttons

### Wrong data / bit errors

1. **Clock polarity**: Try changing `gpio_pull_up` to `gpio_pull_down` on clock pin
2. **Data polarity**: Try inverting: `uint8_t bit = gpio_get(PIN_DATA_IN) ? 0 : 1;`
3. **Timing**: The bit-bang implementation should work at 8kHz, but if issues persist, consider PIO

### GB shows 0xFF for all RX

1. **Check SI connection**: Orange wire might not be connected properly
2. **Level shifter direction**: Verify it's bidirectional or output direction is correct
3. **Pico GPIO**: Ensure GP4 is actually outputting (check with multimeter)

## Future Improvements

- [ ] PIO-based implementation for more reliable timing
- [ ] GBC high-speed mode support (~256 kHz)
- [ ] Example protocols (save transfer, multiplayer simulation)
- [ ] USB HID device for GB→PC communication

## Resources

- [Pan Docs - Serial Data Transfer](https://gbdev.io/pandocs/Serial_Data_Transfer_(Link_Cable).html)
- [GBDK 2020](https://github.com/gbdk-2020/gbdk-2020)
- [Raspberry Pi Pico SDK](https://github.com/raspberrypi/pico-sdk)

## License

MIT License - feel free to use and modify for your own projects.
