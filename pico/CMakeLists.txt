cmake_minimum_required(VERSION 3.13)

# Initialize pico_sdk from installed location
# (note this can come from environment, CMake cache etc)
# set(PICO_SDK_PATH "/path/to/pico-sdk")

# Pull in Raspberry Pi Pico SDK (must be before project)
include(pico_sdk_import.cmake)

project(gb_link C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialize the Raspberry Pi Pico SDK
pico_sdk_init()

# Add executable
add_executable(gb_link
    gb_link.c
)

# Pull in common dependencies
target_link_libraries(gb_link
    pico_stdlib
    hardware_gpio
)

# Enable USB output, disable UART output
pico_enable_stdio_usb(gb_link 1)
pico_enable_stdio_uart(gb_link 0)

# Create map/bin/hex/uf2 file etc.
pico_add_extra_outputs(gb_link)
