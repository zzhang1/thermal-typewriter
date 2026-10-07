# Thermal Typewriter

A small Raspberry Pi app that sends typed text to a USB thermal printer. An optional 16×2 LCD shows the current line and status messages.

## Requirements

- Raspberry Pi with Python 3
- USB thermal printer
- Optional 16×2 LCD wired to the BCM GPIO pins listed in `typewriter.py`
- Python packages: `pyusb`, `RPLCD`, and `RPi.GPIO`

Create a virtual environment and install the Python packages:

```sh
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install pyusb RPLCD RPi.GPIO
```

## Printer setup

Find the printer's vendor and product IDs:

```sh
lsusb
```

Create a udev rule for that device (replace the example IDs with the values from `lsusb`):

```sh
sudo nano /etc/udev/rules.d/33-receipt-printer.rules
```

Add:

```text
SUBSYSTEM=="usb", ATTR{idVendor}=="4b43", ATTR{idProduct}=="3538", GROUP="lp", MODE="0660"
```

Reload udev rules or reconnect the printer. The same IDs are currently set in `typewriter.py`.

## Run

```sh
python3 typewriter.py
```

Type in the terminal; press Enter to print the current line. Press Ctrl-C to exit.

## Keyboard shortcuts

| Shortcut | Action |
| --- | --- |
| Ctrl-F | Toggle regular and small font |
| Ctrl-B | Toggle bold |
| Ctrl-U | Toggle underline |
| Ctrl-L | Left align |
| Ctrl-E | Center align |
| Ctrl-R | Right align |
