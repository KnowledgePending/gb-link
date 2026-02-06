/**
 * Game Boy Link Cable Test ROM - Bidirectional
 * 
 * This ROM can both send AND receive data over the link cable.
 * Acts as master (generates the clock).
 * 
 * Controls:
 *   A      - Send 0x00
 *   B      - Send 0xFF
 *   SELECT - Send 0xAA
 *   START  - Send 0x55
 *   UP     - Send counter (increments each send)
 *   DOWN   - Clear screen
 * 
 * Display shows both TX (sent) and RX (received) values.
 */

#include <gb/gb.h>
#include <stdio.h>

// Counter for UP button sends
UINT8 counter = 0;

// Line counter for display
UINT8 line = 4;

/**
 * Send a byte and receive a byte simultaneously (full duplex)
 * 
 * @param tx_value The byte to send
 * @return The byte received from the other device
 */
UINT8 link_transfer(UINT8 tx_value) {
    UINT8 rx_value;
    
    // Load value to send into Serial Buffer register
    SB_REG = tx_value;
    
    // Start transfer with internal clock (master mode)
    // Bit 7: Transfer Start Flag (1 = start)
    // Bit 0: Shift Clock (1 = internal/master)
    SC_REG = 0x81;
    
    // Wait for transfer to complete
    // Bit 7 is cleared by hardware when transfer finishes
    while (SC_REG & 0x80);
    
    // Read received value from Serial Buffer
    rx_value = SB_REG;
    
    return rx_value;
}

/**
 * Print a transfer result to the screen
 */
void print_transfer(UINT8 tx, UINT8 rx) {
    // Scroll if we're near the bottom
    if (line >= 17) {
        // Simple clear and reset
        printf("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n");
        gotoxy(0, 0);
        printf("LINK TEST\n");
        printf("A=00 B=FF SEL=AA\n");
        printf("STA=55 UP=CNT\n");
        line = 4;
    }
    
    gotoxy(0, line);
    printf("TX:%02X RX:%02X\n", tx, rx);
    line++;
}

void main(void) {
    UINT8 keys;
    UINT8 prev_keys = 0;
    UINT8 tx_byte;
    UINT8 rx_byte;

    DISPLAY_ON;
    SHOW_BKG;

    // Title and instructions
    printf("LINK TEST\n");
    printf("A=00 B=FF SEL=AA\n");
    printf("STA=55 UP=CNT\n");
    printf("----------------\n");

    while (1) {
        keys = joypad();
        
        // Only trigger on key press (not hold)
        UINT8 pressed = keys & ~prev_keys;

        if (pressed & J_A) {
            tx_byte = 0x00;
            rx_byte = link_transfer(tx_byte);
            print_transfer(tx_byte, rx_byte);
            delay(100);
        }
        
        if (pressed & J_B) {
            tx_byte = 0xFF;
            rx_byte = link_transfer(tx_byte);
            print_transfer(tx_byte, rx_byte);
            delay(100);
        }
        
        if (pressed & J_SELECT) {
            tx_byte = 0xAA;
            rx_byte = link_transfer(tx_byte);
            print_transfer(tx_byte, rx_byte);
            delay(100);
        }
        
        if (pressed & J_START) {
            tx_byte = 0x55;
            rx_byte = link_transfer(tx_byte);
            print_transfer(tx_byte, rx_byte);
            delay(100);
        }
        
        if (pressed & J_UP) {
            tx_byte = counter++;
            rx_byte = link_transfer(tx_byte);
            print_transfer(tx_byte, rx_byte);
            delay(100);
        }
        
        if (pressed & J_DOWN) {
            // Clear screen
            printf("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n");
            gotoxy(0, 0);
            printf("LINK TEST\n");
            printf("A=00 B=FF SEL=AA\n");
            printf("STA=55 UP=CNT\n");
            printf("----------------\n");
            line = 4;
            counter = 0;
        }

        prev_keys = keys;
        wait_vbl_done();
    }
}
