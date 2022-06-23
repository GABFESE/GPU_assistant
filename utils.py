# Libraries
import numpy as np
import pycuda.driver as cuda
import os
import RPi.GPIO as GPIO
import time
import math

from alerts.alertas import openaudio
from string import Template
from timeit import default_timer as timer

print("Init Utils")

def copy_host_to_device(*hots_variables):
    device_mem_allocations = []
    for index in range(len(hots_variables)):
        # Memory allocation
        device_mem_allocation = memory_allocation(hots_variables[index].astype(np.float32))
        # Copy host information to device
        cuda.memcpy_htod(device_mem_allocation, hots_variables[index])
        device_mem_allocations.append(device_mem_allocation)
    return device_mem_allocations if len(device_mem_allocations) > 1 else device_mem_allocation

def memory_allocation(hots_variable):
    return cuda.mem_alloc(hots_variable.nbytes)

def kernel_creation(path, **kernel_parameters):
    parameters = kernel_parameters["kernel_parameters"]
    path = os.path.join(path, "templates.cpp")
    template = Template(_get_template(path))
    return template.safe_substitute(**parameters)

def _get_template(path):
    with open(path, "r") as file:
        template = file.readlines()
    return "".join(template)

def distances(value):
    # characteristic equation of the kinect sensor
    functiona = 0.0000000153604707187203 * pow(value, 5)
    functionb = 0.0000102550961463067 * pow(value, 4)
    functionc = 0.002562964189799 * pow(value, 3)
    functiond = 0.281730142677474 * pow(value, 2)
    functione = 11.860783228931 * value
    dist = round(functiona - functionb + functionc - functiond + functione)
    return dist

def variables(size_layers_distance):
    lower_thresh = 115
    upper_thresh = lower_thresh + size_layers_distance #135}
    mindist_system = 220
    counter = 1
    flag_button = True
    flag_init = True
    return lower_thresh, upper_thresh, mindist_system, counter, flag_button, flag_init

def datta(camera_height, increment, lower_thresh, upper_thresh, max_upper=255, degrees=69):  
    iterations = int(((max_upper - upper_thresh) / increment) + 1)
    input_vector = np.array([[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]])
    output_vector = np.zeros([])
    distance = (camera_height / math.cos(math.radians(degrees)))
    maximum_distance = int(math.sqrt((distance)**2 - (camera_height)**2))
    mid = (lower_thresh + (int(iterations / 2) * (increment)))
    return max_upper, iterations, input_vector, output_vector, maximum_distance, mid

def button(flag):
    # Eliminate the bounce effect of the button
    if(GPIO.input(22)):
        time.sleep(1)
        if(GPIO.input(22)):
            time.sleep(1)
            if(GPIO.input(22)):
                if(flag):
                    openaudio('PAUSADO','signals')
                else:
                    openaudio('REANUDADO','signals')
                flag = not flag
                time.sleep(1)
    return flag
