import usb.core
import usb.util
import time 
#Include libraries
import RPi.GPIO as GPIO
import time
from RPLCD.gpio import CharLCD

lcd = CharLCD(pin_rs = 7, pin_rw = None, pin_e = 8, pins_data = [25,24,23,18], 
        numbering_mode = GPIO.BCM, cols=16, rows=2, dotsize=8)


# ESCPOS Codes
__ESC = '\x1b'
__GS = '\x1d'
__DLE = '\x10'
__FS = '\x1c'


__BOLD_ON = __ESC + 'E\x01'
__BOLD_OFF = __ESC + 'E\x00'
__UNDERLINE_ON = __ESC + '-\x01'
__UNDERLINE_OFF = __ESC + '-\x00'
__FONT_A = __ESC + 'M' + '\x00'
__FONT_B = __ESC + 'M' + '\x01'
__ALIGN_LEFT = __ESC + 'a' + '\x00'
__ALIGN_CENTER = __ESC + 'a' + '\x01'
__ALIGN_RIGHT = __ESC + 'a' + '\x02'
__ALIGN_JUSTIFY = __ESC + 'a' + '\x03'


"""Demo program to print to the POS58 USB thermal receipt printer. This is
labeled under different companies, but is made by Zijiang. See 
http:zijiang.com"""

# In Linux, you must:
#
# 1) Add your user to the Linux group "lp" (line printer), otherwise you will
#    get a user permissions error when trying to print.
#
# 2) Add a udev rule to allow all users to use this USB device, otherwise you
#    will get a permissions error also. Example:
#
#    In /etc/udev/rules.d create a file ending in .rules, such as
#    33-receipt-printer.rules with the contents:
#
#   # Set permissions to let anyone use the thermal receipt printer
#   SUBSYSTEM=="usb", ATTR{idVendor}=="0416", ATTR{idProduct}=="5011", MODE="666"

# Find our device
# 0416:5011 is POS58 USB thermal receipt printer

def connect_device():
    lcd.clear()
    lcd.write_string('Connecting...')
    try:
    #dev = usb.core.find(idVendor=0x0416, idProduct=0x5011)
        global dev
        dev = usb.core.find(idVendor=0x4B43, idProduct=0x3538)

        # Was it found?
        if dev is None:
            raise ValueError('Device not found')
        else:
            print('Printer found and attached')

        # Disconnect it from kernel
        global needs_reattach
        needs_reattach = False
        if dev.is_kernel_driver_active(0):
            needs_reattach = True
            dev.detach_kernel_driver(0)

        # Set the active configuration. With no arguments, the first
        # configuration will be the active one
        dev.set_configuration()

        # get an endpoint instance
        cfg = dev.get_active_configuration()
        intf = cfg[(0,0)]

        global ep
        ep = usb.util.find_descriptor(
            intf,
            # match the first OUT endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_OUT)

        assert ep is not None
        lcd.clear()
        lcd.write_string('Happy Typing!')
        time.sleep(2)
    except:
        time.sleep(5)
        connect_device()


## Get keyboard character input
class _Getch:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

mode = 'typing'
line_break_mode = 'whole word'
bold = False
underline = False
fontA = True
injection_buffer = []
chars_per_line = 32

def handle_hyphen_break(c, char_buffer):
    if len(char_buffer) <= chars_per_line - 1:
        char_buffer.append(c)
    else:
        if c == ' ' or char_buffer[-2] == ' ':
            char_buffer[-1] = ''
            c = ''
        else:
            char_buffer[-1] = '-'
        print_buffer(''.join(char_buffer))
        char_buffer = [c]
    return char_buffer


def handle_whole_word_break(c, char_buffer):
    if len(char_buffer) <= chars_per_line - 1:
        char_buffer.append(c)
        return char_buffer
    elif c == ' ':
        new_buffer = []
        print_buffer(''.join(char_buffer))
    else:
        try:
            last_space = ''.join(char_buffer).rindex(' ')
            new_buffer = char_buffer[last_space+1:]
        except:
            new_buffer = []
            last_space = len(char_buffer)-1
        print_buffer(''.join(char_buffer[:last_space+1]))
        new_buffer.append(c)
    lcd.write_string(''.join(new_buffer))
    return new_buffer


def setup():
    lcd.clear()
    lcd.cursor_mode = 'blink'


def flash(string, current_string, seconds=1):
    lcd.clear()
    lcd.write_string(string)
    time.sleep(seconds)
    lcd.clear()
    lcd.write_string(current_string)


def loop():
    global mode
    global underline
    global bold
    global fontA
    global injection_buffer
    global chars_per_line

    print('Ready for typing.')
    getch = _Getch()
    char_buffer = []
    escape_buffer = []
    tag_along_string = ''
    while True:
        c = getch()
        print(ord(c))
        #Force new line if limit is reached, but hyphenate for now
        if mode == 'typing':
            if c == '\r':
                print_buffer(''.join(char_buffer))
                char_buffer=[]
            elif c == '\x03':
                break
            elif c == '\x02':  # Bold
                if bold:
                    tag_along_string = tag_along_string + __BOLD_OFF
                    flash('Bold OFF',''.join(char_buffer))
                else:
                    tag_along_string = tag_along_string + __BOLD_ON
                    flash('Bold ON',''.join(char_buffer))
                bold = not bold
            elif c == '\x15':  # Underline
                if underline:
                    tag_along_string = tag_along_string + __UNDERLINE_OFF
                    flash('Underline OFF',''.join(char_buffer))
                else:
                    tag_along_string = tag_along_string + __UNDERLINE_ON
                    flash('Underline ON',''.join(char_buffer))
                underline = not underline
            elif c == '\x0c':  # CTRL L Left Align
                tag_along_string = tag_along_string + __ALIGN_LEFT
                flash('Left align',''.join(char_buffer))
            elif c == '\x05':  # CTRL E Center Align
                tag_along_string = tag_along_string + __ALIGN_CENTER
                flash('Center align',''.join(char_buffer))
            elif c == '\x12':  # CTRL R Right Align
                tag_along_string = tag_along_string + __ALIGN_RIGHT
                flash('Right align',''.join(char_buffer))
            elif c == '\x06':  # CTRL F Toggle font
                if fontA:
                    tag_along_string = tag_along_string + __FONT_B
                    chars_per_line = 42
                    flash('Small font',''.join(char_buffer))
                else:
                    tag_along_string = tag_along_string + __FONT_A
                    chars_per_line = 32
                    flash('Regular font',''.join(char_buffer))
                fontA = not fontA
            elif ord(c) == 27:
                print('ESC detected')
                mode = 'escape'
            elif ord(c) == 127 or ord(c) == 8:  #Backspace
                print('Backspace detected')
                if len(char_buffer) > 0:
                    char_buffer.pop()
                    lcd.clear()
                    lcd.write_string(''.join(char_buffer))
            elif ord(c) >= 32 and ord(c) <= 126:  #Regular typewriter mode if the character is printable
                lcd.write_string(c)
                injection_buffer.append((len(char_buffer),tag_along_string))
                tag_along_string = ''
                if line_break_mode == 'force hyphen':
                    char_buffer = handle_hyphen_break(c, char_buffer)
                elif line_break_mode == 'whole word':
                    char_buffer = handle_whole_word_break(c, char_buffer)
        elif mode == 'escape':
            escape_buffer.append(c)
            mode = 'typing'


# Print the string to printer and clear the screen
def print_buffer(string_buffer):
    global injection_buffer
    try:
        # Inject any ESC commands
        while len(injection_buffer) > 0:
            location, inject_string = injection_buffer.pop()
            string_buffer = string_buffer[:location] + inject_string + string_buffer[location:]
        ep.write(string_buffer + '\n')
        print(string_buffer)
    except:
        print('Reconnecting to printer')
        connect_device()
        print_buffer(string_buffer)
    lcd.clear()


connect_device()
setup()
loop()


dev.reset()
if needs_reattach:
    dev.attach_kernel_driver(0)
    print("Reattached USB device to kernel driver")

lcd.close()
GPIO.cleanup()
