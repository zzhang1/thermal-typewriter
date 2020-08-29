# thermal-typewriter
Typewriter app for connecting to thermal printer

## Setup
### Requirements
    sudo pip3 install pyusb

Find the ID of the USB device with lsusb. The ID is 8 digits in the form of VEND:PROD

    lsusb

Add permission to all users to use the USB printer. Make a new udev rule file with.

    sudo nano /etc/udev/rules.d/33-receipt-printer.rules

In this example, the ID from `lsusb` was 4b43:3538. Add the following to the file and save. 

    # Set permissions to let anyone use the thermal receipt printer
    SUBSYSTEM=="usb", ATTR{idVendor}=="4b43", ATTR{idProduct}=="3538", MODE="666"
