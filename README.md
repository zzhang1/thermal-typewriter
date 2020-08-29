# thermal-typewriter
Typewriter app for connecting to thermal printer from Raspberry Pi, printing text line by line. Supports using a 16x2 LCD display as a display.

## Setup
### Hardware Requirements
1. Raspberry Pi
2. Thermal Printer with USB mode supported
3. Optional but suggested: 16x2 LCD display
### Software Requirements
    sudo pip3 install pyusb

Find the ID of the USB device with lsusb. The ID is 8 digits in the form of VEND:PROD

    lsusb

Add permission to all users to use the USB printer. Make a new udev rule file with.

    sudo nano /etc/udev/rules.d/33-receipt-printer.rules

In this example, the ID from `lsusb` was 4b43:3538. Add the following to the file and save. 

    # Set permissions to let anyone use the thermal receipt printer
    SUBSYSTEM=="usb", ATTR{idVendor}=="4b43", ATTR{idProduct}=="3538", MODE="666"

Edit the source code to search for the same USB device ID

Optionally, connect LCD to the pins as specified in the source code, to use as a display.

## Use
* Ctrl-F: Toggle font size (Font A (normal) and Font B (small))
* Ctrl-B: Bold
* Ctrl-U: Underline
* Ctrl-L: Left Align
* Ctrl-E: Center Align
* Ctrl-R: Right Align
