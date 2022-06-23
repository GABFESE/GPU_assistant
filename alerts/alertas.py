# Libraries
import RPi.GPIO as GPIO
import time

from playsound import playsound

# Motor pin definition
print("Init Alert")
motor_1 = 32
motor_2 = 33
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(motor_1,GPIO.OUT)
GPIO.setup(motor_2,GPIO.OUT)

# Motor initialization
my_pwm1 = GPIO.PWM(motor_1,100)
my_pwm2 = GPIO.PWM(motor_2,100)
my_pwm1.start(0)
my_pwm1.ChangeDutyCycle(100)
my_pwm2.start(0)
my_pwm2.ChangeDutyCycle(100)

def ChangeDutyCycles(DutyCycle_1, DutyCycle_2):
    my_pwm1.ChangeDutyCycle(DutyCycle_1)
    my_pwm2.ChangeDutyCycle(DutyCycle_2)

def stoppwm():
    ChangeDutyCycles(100,100)

def initpwm():
    ChangeDutyCycles(50,100)
    time.sleep(1)
    ChangeDutyCycles(100,50)
    time.sleep(1)
    stoppwm()

def offpwm():
    initpwm()
    my_pwm1.stop()
    my_pwm2.stop()

def freq(distance):
    # Frec and dutty selection according to measured distance
    if distance >= 200 and distance <= 300:
        frec = 100
        dutty = 70
    elif distance >= 101 and distance <= 199 :
        frec = 1000
        dutty = 40
    elif distance >= 0 and distance <= 100:
        frec = 2000
        dutty =0
    elif distance > 300:
        frec = 25
        dutty = 100
    return frec, dutty
    
def PWM(list):
    # PWM selection according to resultant vector of path planning
    left_motor = list[0]
    left_distance = list[1]
    right_motor = list[2]
    right_distance = list[3]
    
    left_dutty = 0
    right_dutty = 0
    frec = 0

    if left_motor == 1 and right_motor == 0: 
        frec,left_dutty = freq(left_distance)
        right_dutty = 100
    elif left_motor == 0 and right_motor == 1:
        frec,right_dutty = freq(right_distance)
        left_dutty = 100
    elif left_motor == 1 and right_motor == 1:
        if(right_distance < 50):
            right_distance = 50
        frec,right_dutty = freq(right_distance)
        left_dutty = right_dutty
    elif left_motor == 0 and right_motor == 0:
        frec = 25
        right_dutty = 100
        left_dutty = right_dutty

    ChangeDutyCycles(0, 0)
    my_pwm1.ChangeFrequency(frec)
    my_pwm2.ChangeFrequency(frec)
    ChangeDutyCycles(right_dutty, left_dutty)

def openaudio(name, types):
    filename = "alerts/" + types + "/" + name + '.mp3'
    playsound(filename)

def audio(list):
    # Selection of audio to play
    ruta = list[4]

    if(list[0] == 1 and list[1] == 1 and list[2] == 1 and list[3] == 1):
        openaudio('detenido','rute')
    elif(ruta == "centros"):
        openaudio("centro",'rute')
    else:
        openaudio(ruta,'rute')

def interrupt(list):
    # Function performed by the button
    time.sleep(.5)
    if(GPIO.input(22)):
        print("interrupcion")
        PWM(list)
        audio(list)
