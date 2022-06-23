# Libraries
import math
import numpy as np
import os
import pycuda.autoinit
import pycuda.driver as cuda
import time

from alerts.alertas import openaudio, audio, PWM
from pycuda import compiler
from utils import copy_host_to_device, kernel_creation
from uart import reception_uart


def thresholding_depth(val_lower, val_upper, img_depth):              
    # thresholding by layers, according to distance sections
    thres_depth = 255 * np.logical_and(img_depth > val_lower, img_depth < val_upper)
    return thres_depth

def detection(binarized_image, index, dist):
    # Algorithm for object detection
    # Definition of necessary variables 
    height_image, width_image = binarized_image.shape
    rows_device = math.ceil(width_image / 100)
    columns_device = math.ceil(height_image / 100)

    # Creating vectors for processing
    binarized_image_host = np.array(binarized_image).astype(np.uint32)
    matrix_detection_host = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]).astype(np.uint32)

    binarized_image_device, matrix_detection_device = copy_host_to_device(binarized_image_host, matrix_detection_host)

    path = os.path.dirname(os.path.abspath(__file__))
    parameters = {
        'height_image': str(height_image), 
        'width_image': str(width_image),
        'channels': str(index),
        'lower': str(1),
        'upper': str(1)
    }
    kernel = kernel_creation(path, kernel_parameters = parameters)

    # Kernel excecution
    module = compiler.SourceModule(kernel)
    rgb2gray_function = module.get_function("detection")
    rgb2gray_function(
        binarized_image_device, 
        matrix_detection_device,
        block = (rows_device, columns_device, 1),
        grid = (100, 100, 1),
    )

    # Copy device variable to host device
    cuda.memcpy_dtoh(matrix_detection_host, matrix_detection_device)
    return matrix_detection_host

def obstacle_detector(bin_image, input_vector, actual_distance, iterations, maximum_distance):
    # Function to apply detection algorithm
    height, width = input_vector.shape
    displacement_increase = int((64 / iterations) * height)
    matrix_detection = detection(bin_image, displacement_increase, actual_distance)
    detection_matrix = np.append(matrix_detection, actual_distance, axis=None)

    # Layer-by-layer detection matrix
    input_vector = np.append(input_vector, [detection_matrix], axis=0)

    # Function to remove soil at a certain distance
    if(input_vector[height, 15] >= maximum_distance): 
        if(input_vector[height,6] == 0):
            input_vector[height,11] = 0
        elif(input_vector[height,7] == 0):
            input_vector[height,12] = 0
        elif(input_vector[height,8] == 0):
            input_vector[height,13] = 0
    return input_vector

def avg_detection(detection_matrix, iterations):
    # Algorithm for object detection averaging       
    output = np.array([[0,1,2,3,4,5]])
    temp = np.array([0,1,2,3,4,5]) 

    for i in range(1, iterations + 1):
        for j in range(5):
            if((detection_matrix[i,j+5] == 1) or (detection_matrix[i,j+10] == 1) or (detection_matrix[i,j] == 1)):
                temp[j] = 1
            else:
                temp[j] = 0
        temp[5] = detection_matrix[i, 15]
        output = np.append(output, [temp], axis=0)
    return output

def counter(avg_detection_matrix, index, iterations, posicion):
    # Algorithm for counting free positions of detected objects
    for height in range (index, iterations):
        if(avg_detection_matrix[height, posicion] != 0):
            break
    return height 

def path_planning(avg_detection_matrix, iterations, min_dist):
    # Path planning algorithm
    alert_vector = np.array([0,1,2,3,4]) 
    center_count = counter(avg_detection_matrix, 1, iterations, 2)
    right_count = counter(avg_detection_matrix, 1, iterations, 3)
    left_count = counter(avg_detection_matrix, 1, iterations, 1)

    # Alert creation
    if(center_count > right_count and center_count > left_count):
        if(avg_detection_matrix[center_count,5] > min_dist):
            alert_vector = ([0,avg_detection_matrix[center_count,5],0,avg_detection_matrix[center_count,5],"centros"])
        else:
            alert_vector = ([0,avg_detection_matrix[center_count,5],0,avg_detection_matrix[center_count,5],"centro"])
    elif(right_count > left_count):
        left_count = counter(avg_detection_matrix, 0, iterations, 1)
        alert_vector = ([0,avg_detection_matrix[left_count,5],1,avg_detection_matrix[right_count,5],"derecha"])
    elif(left_count > right_count):
        right_count = counter(avg_detection_matrix, 0, iterations, 3)
        alert_vector = ([1,avg_detection_matrix[left_count,5],0,avg_detection_matrix[right_count,5],"izquierda"])
    elif(center_count == right_count == left_count):
        if(avg_detection_matrix[center_count,5] > min_dist):
            alert_vector = ([0,avg_detection_matrix[center_count,5],0,avg_detection_matrix[center_count,5],"centros"])
        else:
            alert_vector = ([1,avg_detection_matrix[left_count,5],1,avg_detection_matrix[right_count,5],"igual"])        
    else:
        alert_vector = ([1,avg_detection_matrix[left_count,5],1,avg_detection_matrix[right_count,5],"igual"])
    return alert_vector

def ultrasound_measurement(mindist_ultra, counter):
    # Addition of the value detected by the ultrasound sensor
    ultrasound = reception_uart()
    danger = False

    if(ultrasound <= mindist_ultra):
        counter += 1
        danger = True

        # If the warning is repeated for more than 3 times, it is "deactivated"
        if(counter <= 3):
            alert = ([1,ultrasound,1,ultrasound,"alerta"]) 
            print(alert)
            PWM(alert)
            audio(alert) 
    else:
        counter = 0
    return counter, danger

def detection_alert(init_flag, alert_input_vector, iterations, mindist_system, mindist_ultra, counter):
    # Function for the generation and emission of alerts
        counter, danger = ultrasound_measurement(mindist_ultra, counter)
        alert = np.array([0,1,2,3,4])

        # message only at program start
        if(init_flag):
            openaudio('INICIANDO','signals')
            init_flag = False
            
        if(not danger):
            output_vector = avg_detection(alert_input_vector, iterations)
            alert = path_planning(output_vector, iterations, mindist_system)
            PWM(alert)
        
        print(alert)
        return init_flag, counter, alert
        