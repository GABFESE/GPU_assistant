# Libraries
import RPi.GPIO as GPIO
import serial
import time

from os import system

print("Init Uart")

# Serial port configuration
system("sudo chmod 666 /dev/ttyTHS0")
serial_port = serial.Serial(
    port = "/dev/ttyTHS0",
    baudrate = 9600,
    bytesize = serial.EIGHTBITS,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
)
time.sleep(1)

# Configuration for output port to microcontroller
pin_enable_uc = 12
GPIO.setmode(GPIO.BOARD)  
GPIO.setup([pin_enable_uc], GPIO.OUT)
GPIO.output(pin_enable_uc, GPIO.LOW)

def closeuart():
    serial_port.close()

def enable_uc(times):
    # Microcontroller enable function
    GPIO.output(pin_enable_uc, GPIO.HIGH)
    time.sleep(times)
    GPIO.output(pin_enable_uc, GPIO.LOW)
    time.sleep(times)
    
def reception_uart():
    # Function for receiving data from the UART
    enable_uc(.007)

    if serial_port.inWaiting() > 0:
        message = []
        index = True

        while index:
            data = serial_port.read().decode("utf-8")

            if data == "\r" or data == "\n":       # Characters designated for death line
                if(index != 0):
                    index = False
                    message.pop(0)
                    strings = [str(integer) for integer in message]
                    a_string = "".join(strings)
                    an_integer = int(a_string)
                    return an_integer

            else:
                # Add information character by character
                message.append(data)
                index += 1
