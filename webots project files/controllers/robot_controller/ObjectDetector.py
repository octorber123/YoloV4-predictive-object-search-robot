import os
import re
import cv2
import numpy as np
import tensorflow as tf

from yolov3.configs import *
from yolov3.utils import detect_image, detect_realtime, detect_video, Load_Yolo_model, detect_video_realtime_mp



yolo = Load_Yolo_model()

unfiltered_detections = {}




def get_yolo_detections_from_camera(robot_camera):
 
    detections = [] 
    
    rgb_scene_image = np.frombuffer(robot_camera.getImage(), np.uint8).reshape((480,640,4))
    rbg_scene_image_with_detections, detections= detect_image(yolo, rgb_scene_image, "" , input_size=YOLO_INPUT_SIZE, show=False,    rectangle_colors=(255,0,0))
    cv2.imshow('Detections', rbg_scene_image_with_detections)
    

    return detections

def filter_detections(detections, acceptance_count):

    """
    this method filters detections based on the number of occurances, occrances higher than acceptance count returned

    :param detections          : is a list of detections from camera
    :param acceptance_count    : is an integer value
    
    :return: a list of filtered detections [name, bbox_x1, bbox_y1, bbox_x2, bbox_y2]
    """ 

    filtered_detections = []
    for detection in detections:
    
       
        detection_name  =  tokenize(detection[0])[0]
        if(detection_name == 'bench'):
            continue
            
        if(detection_name in unfiltered_detections.keys()):
        
            count = unfiltered_detections[detection_name][0] + 1
            unfiltered_detections[detection_name] = [count, detection]
        
        if(detection_name not in unfiltered_detections.keys()):
            count = 1
            unfiltered_detections[detection_name] = [count, detection]
            
    for detection in unfiltered_detections:
        
        if(unfiltered_detections[detection][0] >= acceptance_count):
            filtered_detections.append( unfiltered_detections[detection][1])
            count = 1
            unfiltered_detections[detection] = [count, detection]

    return filtered_detections
    
    
def tokenize(text):   
    DELIM = '\s|(?<!\d)[,.](?!\d)'  
    return re.split(DELIM, text.lower())
