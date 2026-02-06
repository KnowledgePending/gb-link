# Game Boy Link Cable Test ROMs Makefile
# Requires GBDK to be installed

# GBDK path - adjust if needed
GBDK ?= /opt/gbdk
LCC = $(GBDK)/bin/lcc

# Compiler flags
LCCFLAGS = -Wa-l -Wl-m -Wl-j

# ROM targets
all: primary.gb secondary.gb

# Primary ROM - original send-only test
primary.gb: primary.c
	$(LCC) $(LCCFLAGS) -o $@ $<

# Secondary ROM - bidirectional test with RX display
secondary.gb: secondary.c
	$(LCC) $(LCCFLAGS) -o $@ $<

clean:
	rm -f *.gb *.o *.lst *.map *.sym *.asm

.PHONY: all clean
