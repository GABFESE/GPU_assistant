# Libraries
import freenect
import numpy as np
import pandas as pd
import RPi.GPIO as GPIO
import time

print("Init Kinect")

def closekinect():
    freenect.Kill
    freenect.sync_stop()

def depth_map():
    depth_map, timestamp = freenect.sync_get_depth(0, freenect.DEPTH_11BIT)
    np.clip(depth_map, 0, 2**10 - 1, depth_map)
    depth_map >>= 2
    depth_map = depth_map.astype(np.uint8)
    return depth_map
