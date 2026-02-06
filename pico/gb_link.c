/**
 * Game Boy Link Cable Receiver for Raspberry Pi Pico
 * 
 * This firmware acts as a secondary device, receiving data from a Game Boy
 * that is operating as the master (generating the clock signal).
 * 
 * Wiring:
 *   GP2 - Clock input (Brown wire - SC from GB)
 *   GP3 - Data input (Yellow wire - SO from GB, data FROM Game Boy)
 *   GP4 - Data output (Orange wire - SI to GB, data TO Game Boy)
 *   GND - Ground (Black wire)
 * 
 * Protocol:
 *   - SPI-like synchronous serial
 *   - Clock idles HIGH
 *   - Data sampled on falling edge of clock
 *   - MSB first, 8 bits per transfer
 *   - ~8kHz clock rate (normal speed)
 */

#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"

// Pin definitions
#define PIN_CLOCK   2   // GP2 - Clock input (Brown)
#define PIN_DATA_IN 3   // GP3 - Data from GB (Yellow)
#define PIN_DATA_OUT 4  // GP4 - Data to GB (Orange)

// Receive state
volatile uint8_t rx_byte = 0;
volatile uint8_t rx_bit_count = 0;
volatile bool byte_ready = false;
volatile uint8_t last_received_byte = 0;

// Transmit state
volatile uint8_t tx_byte = 0x00;  // Byte to send back to GB
volatile uint8_t tx_bit_count = 0;

/**
 * GPIO interrupt handler - called on clock falling edge
 * 
 * On each falling edge:
 * 1. Read the data input bit
 * 2. Shift it into the receive register
 * 3. After 8 bits, mark byte as ready
 */
void gpio_callback(uint gpio, uint32_t events) {
    if (gpio == PIN_CLOCK && (events & GPIO_IRQ_EDGE_FALL)) {
        // Read data bit from GB
        uint8_t bit = gpio_get(PIN_DATA_IN) ? 1 : 0;
        
        // Shift into receive register (MSB first)
        rx_byte = (rx_byte << 1) | bit;
        rx_bit_count++;
        
        // Also shift out our data bit to GB (MSB first)
        // Set output for NEXT clock cycle
        uint8_t out_bit = (tx_byte >> (7 - tx_bit_count)) & 0x01;
        gpio_put(PIN_DATA_OUT, out_bit);
        tx_bit_count++;
        
        if (rx_bit_count >= 8) {
            // Complete byte received
            last_received_byte = rx_byte;
            byte_ready = true;
            rx_byte = 0;
            rx_bit_count = 0;
            tx_bit_count = 0;
        }
    }
}

/**
 * Initialize GPIO pins for link cable communication
 */
void init_link_pins(void) {
    // Clock pin - input with pull-up (clock idles high)
    gpio_init(PIN_CLOCK);
    gpio_set_dir(PIN_CLOCK, GPIO_IN);
    gpio_pull_up(PIN_CLOCK);
    
    // Data input pin - input with pull-up
    gpio_init(PIN_DATA_IN);
    gpio_set_dir(PIN_DATA_IN, GPIO_IN);
    gpio_pull_up(PIN_DATA_IN);
    
    // Data output pin - output, start high (idle state)
    gpio_init(PIN_DATA_OUT);
    gpio_set_dir(PIN_DATA_OUT, GPIO_OUT);
    gpio_put(PIN_DATA_OUT, 1);
    
    // Enable interrupt on clock falling edge
    gpio_set_irq_enabled_with_callback(PIN_CLOCK, GPIO_IRQ_EDGE_FALL, true, &gpio_callback);
}

/**
 * Set the byte that will be sent to the Game Boy on the next transfer
 */
void set_tx_byte(uint8_t value) {
    tx_byte = value;
}

int main() {
    // Initialize stdio for USB serial output
    stdio_init_all();
    
    // Wait for USB connection (optional, helpful for debugging)
    sleep_ms(2000);
    
    printf("\n");
    printf("================================\n");
    printf("Game Boy Link Cable Receiver\n");
    printf("================================\n");
    printf("Pins:\n");
    printf("  GP2 - Clock (Brown)\n");
    printf("  GP3 - Data In (Yellow)\n");
    printf("  GP4 - Data Out (Orange)\n");
    printf("  GND - Ground (Black)\n");
    printf("================================\n");
    printf("Waiting for data from Game Boy...\n");
    printf("\n");
    
    // Initialize link cable pins
    init_link_pins();
    
    // Set initial TX byte (will be sent back to GB)
    set_tx_byte(0x00);
    
    uint32_t byte_count = 0;
    
    while (true) {
        if (byte_ready) {
            byte_ready = false;
            byte_count++;
            
            // Print received byte in multiple formats
            printf("[%lu] RX: 0x%02X (dec: %3d, bin: ", 
                   byte_count, last_received_byte, last_received_byte);
            
            // Print binary representation
            for (int i = 7; i >= 0; i--) {
                printf("%c", (last_received_byte & (1 << i)) ? '1' : '0');
            }
            printf(")\n");
            
            // Echo received byte back (for testing)
            // You can change this to send different responses
            set_tx_byte(last_received_byte);
        }
        
        // Small delay to prevent busy-waiting
        sleep_us(100);
    }
    
    return 0;
}
