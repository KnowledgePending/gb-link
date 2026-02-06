#include <gb/gb.h>
#include <stdio.h>

void link_send_byte(UINT8 v) {
    SB_REG = v;
    SC_REG = 0x81;          // start, internal clock
    while (SC_REG & 0x80);  // wait complete
}

void main(void) {
    UINT8 keys;

    DISPLAY_ON;
    SHOW_BKG;

    printf("LINK MASTER\n");
    printf("A=00 B=FF\n");
    printf("SEL=AA STA=55\n");

    while (1) {
        keys = joypad();

        if (keys & J_A) {
            printf("\nTX 00");
            link_send_byte(0x00);
            delay(250);
        }
        if (keys & J_B) {
            printf("\nTX FF");
            link_send_byte(0xFF);
            delay(250);
        }
        if (keys & J_SELECT) {
            printf("\nTX AA");
            link_send_byte(0xAA);
            delay(250);
        }
        if (keys & J_START) {
            printf("\nTX 55");
            link_send_byte(0x55);
            delay(250);
        }

        wait_vbl_done();
    }
}