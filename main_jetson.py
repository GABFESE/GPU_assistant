# Libraries
import freenect
import pycuda.autoinit as inition
import pycuda.driver
import RPi.GPIO as GPIO

from alerts.alertas import interrupt, initpwm, offpwm, openaudio, stoppwm
from detection.processing import detection_alert, obstacle_detector, thresholding_depth,  ultrasound_measurement
from kinect import closekinect, depth_map
from morphology.processing import morfologic
from utils import button, datta, distances, variables
from uart import closeuart

print("Init Main Jetson")

inition
initpwm()
closekinect()

button_pin = 22
interruption_pin = 18
GPIO.setmode(GPIO.BOARD)
GPIO.setup(button_pin, GPIO.IN)  
GPIO.setup(interruption_pin, GPIO.IN) 
# Edge interrupt description
GPIO.add_event_detect(18, GPIO.RISING, callback=lambda reprocudir:interrupt(alert), bouncetime=100)

#variables necesarias
mindist_ultra = 80
camera_height = 150
increment = 10
size_layers_distance = 20

lower_threshi, upper_threshi, mindist_system, counter, flag_button, flag_init = variables(size_layers_distance)
max_upper, iterations, input_vectori, output_vectori, maximum_distance, mid = datta(camera_height, increment, lower_threshi, upper_threshi)

lower = lower_threshi
upper = upper_threshi
input_vector = input_vectori
output_vector = output_vectori
alert = ([1,1,1,1,"igual"]) 
image_depth = depth_map()

try:
    while(True):
        # Check button pressure
        flag_button = button(flag_button)

        if(flag_button):
            # Limit when the maximum number of iterations is reached
            if(upper > max_upper):
                # Create and send alert
                flag_init, counter, alert = detection_alert(flag_init, input_vector, iterations, mindist_system, mindist_ultra, counter)

                # Variable reset
                image_depth = depth_map()
                lower = lower_threshi
                upper = upper_threshi
                input_vector = input_vectori
                output_vector = output_vectori

            actual_distance = distances(upper)
            image = thresholding_depth(lower, upper, image_depth)   # Layered thresholding
            image = morfologic(image)   # Morphological filter application
            input_vector = obstacle_detector(image, input_vector, actual_distance, iterations, maximum_distance)

            # Increase threshold limits
            lower += increment
            upper += increment

            # Periodic review of the value of the ultrasound sensor
            if(not flag_init and mid == lower):
                counter, trash = ultrasound_measurement(mindist_ultra, counter)
        
        else:
            # Program stop function
            alert = ([1,1,1,1,"igual"]) 
            stoppwm()


except KeyboardInterrupt:
    print("Exiting Program")

except Exception as exception_error:
    openaudio('ERROR','signals')
    print("Error occurred. Exiting Program")
    print("Error: " + str(exception_error))

finally:

    offpwm()
    closeuart()
    openaudio('FIN1','signals')
    closekinect()
    pass
