#Include libraries
import RPi.GPIO as GPIO 
import time
from RPLCD.gpio import CharLCD

# Configure the LCD
lcd = CharLCD(pin_rs = 7, pin_rw = None, pin_e = 8, pins_data = [25,24,23,18], 
        numbering_mode = GPIO.BCM, cols=16, rows=2, dotsize=8)

# Create a variable ‘number’ 
number = 0

# Main loop
while(True):
    # Increment the number and then print it to the LCD number = number + 1
    lcd.clear()
    lcd.write_string('Count: '+ str(number))
    time.sleep(1)
    number += 1

lcd.close() 
GPIO.cleanup()
