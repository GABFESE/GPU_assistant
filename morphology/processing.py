# Libraries
import numpy as np
import os
import pycuda.autoinit as inition
import pycuda.driver as cuda
import math

from pycuda import compiler
from utils import copy_host_to_device, kernel_creation

inition

def morphological_filter(binarized_image, filter, name):
    # Algorithm for the application of the morphological filter
    # Definition of necessary variables 
    height_image, width_image = binarized_image.shape
    height_filter, width_filter = filter.shape
    rows_device = math.ceil(width_image / 100)
    columns_device = math.ceil(height_image / 100)

    # Creating vectors for processing
    binarized_image_host = np.array(binarized_image).astype(np.uint32)
    filtered_image_host = np.zeros((height_image, width_image)).astype(np.uint32)
    filter_host = np.array(filter).astype(np.uint32)

    binarized_image_device  = copy_host_to_device(binarized_image_host)
    filtered_image_device = copy_host_to_device(filtered_image_host)
    filter_device = copy_host_to_device(filter_host)

    path = os.path.dirname(os.path.abspath(__file__))
    parameters = {
        'height_image': str(height_image), 
        'width_image': str(width_image),
        'height_filter': str(height_filter),
        'width_filter': str(width_filter)
    }
    kernel = kernel_creation(path, kernel_parameters = parameters)

    # Kernel excecution 
    module = compiler.SourceModule(kernel)
    if(name == "dilatation"):
        dilatation_function = module.get_function("dilatation")
        dilatation_function(
        binarized_image_device,
        filter_device,
        filtered_image_device, 
        block = (rows_device, columns_device, 1),
        grid = (100, 100, 1)
        ) 
    else:
        erosion_function = module.get_function("erosion")
        erosion_function(
        binarized_image_device,
        filter_device,
        filtered_image_device, 
        block = (rows_device, columns_device, 1),
        grid = (100,100,1),
        ) 

    # Copy device variable to host device
    cuda.memcpy_dtoh(filtered_image_host, filtered_image_device)
    return filtered_image_host

def morfologic(depth):
    # Application of morphological filters to eliminate salt and pepper noise
    filter = np.array( [[1,1,1,1,1,1,1],
                        [1,1,1,1,1,1,1],
                        [1,1,1,1,1,1,1],
                        [1,1,1,1,1,1,1],
                        [1,1,1,1,1,1,1],
                        [1,1,1,1,1,1,1],
                        [1,1,1,1,1,1,1]])                  

    output_erosion = morphological_filter(depth, filter, "erosion")
    output_dilatation = morphological_filter(output_erosion, filter, "dilatation")
    output_dilatation = morphological_filter(output_dilatation, filter, "erosion")
    filter_result = morphological_filter(output_dilatation, filter, "dilatation")
    filter_result = output_erosion.astype(np.uint8)

    return filter_result