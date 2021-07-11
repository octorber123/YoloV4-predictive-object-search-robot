import sys
import time
import math
from math import sin, cos, atan2, sqrt, pi
import cv2
import re
import numpy as np
import random
import matplotlib.pyplot as plt
from controller import Robot, RangeFinder

import os
# os.environ['CUDA_VISIBLE_DEVICES'] = '0'
import tensorflow as tf
from yolov3.utils import detect_image, detect_realtime, detect_video, Load_Yolo_model, detect_video_realtime_mp
from yolov3.configs import *

from pytransform3d import rotations as pr
from pytransform3d import transformations as pt
from pytransform3d.transform_manager import TransformManager

from gensim.models import Word2Vec, KeyedVectors
import pandas as dp
import nltk

from CV2MiniMap import *
#from RobotStateMachine import *

from CoordinateManager import *

from RobotNavigator import *


# create the Robot instance.
robot = Robot()
yolo = Load_Yolo_model()
model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary = True, limit = 100000)

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())
print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

#initialise components of robot
wheels = [robot.getDevice('wheel'+str(x+1)) for x in range(4)]
for w in wheels:
    w.setPosition(float('inf'))
    w.setVelocity(0.)

dss = [robot.getDevice('ds_right'), robot.getDevice('ds_left')]
for x in dss:
    x.enable(10)

left_path_ir = robot.getDevice('path-following-IR-sensor-left')
left_path_ir.enable(30)

right_path_ir = robot.getDevice('path-following-IR-sensor-right')
right_path_ir.enable(30)

cam = robot.getDevice('camera')
cam.enable(30)


rangeFinder = robot.getDevice('range-finder')
rangeFinder.enable(30)

robot_gps = robot.getDevice('gps')
robot_gps.enable(30)

compass = robot.getDevice('compass')
compass.enable(30)

step = 0.0


last = time.time()


unfiltered_objects = {}
filtered_objects = {}


tables = []
tables.append(("table1", 0, 3))
tables.append(("table2", -3, 0))
tables.append(("table3", 0, -3))
tables.append(("table4", 3, 0))


table1 = {}
table2 = {}
table3 = {}
table4 = {}

table_containers = [table1, table2, table3, table4]

def tokenize(text):
    #DELIM = '[ \r\n\t0123456789;:.,/\(\)\"\'-]+'   
    DELIM = '\s|(?<!\d)[,.](?!\d)'  
    return re.split(DELIM, text.lower())

def find_table_wtih_best_match(object_name, table_containers, model):
#iterate through all objects in the tables and compare the similarity 
#of the query object with object in the tables
##return the highest similarity and best table (table where most similar obj was found)
    
    bestSimilarity = None
    tablesEmpty = True
    table_index = 1
    for table in table_containers:
        if(len(table) != 0):
            tablesEmpty = False
            for k in table:
                try:
                    similarity = model.similarity(k, object_name)
                    if bestSimilarity is None:
                        bestSimilarity = similarity
                        #best_table = table
                        best_table_index = table_index
                    elif similarity > bestSimilarity:
                        bestSimilarity = similarity
                        #best_table = table
                        best_table_index = table_index
                          
                except Exception:
                    continue
        table_index = table_index + 1    
        
    if(tablesEmpty == True):
        bestSimilarity = 0
        best_table_index = None
    best_table = "table " + str(best_table_index)
    
    return [bestSimilarity, best_table]
     

     

    
    
def assign_objects_to_tables(objects):
    
    
    
    for object in objects:
           
        shortest = 1500
        for index in range(len(tables)):
            distance = math.sqrt((objects[object][0] - tables[index][1])**2 + (objects[object][1] - tables[index][2])**2)
    
            if distance < shortest:
                shortest = distance
                table = tables[index][0]
    
        if table == "table1":
            table1[object] = objects[object]
    
                      
        if table == "table2":
            table2[object] = objects[object]
    
                        
        if table == "table3":
            table3[object] = objects[object]
    
                       
        if table == "table4":
            table4[object] = objects[object]
     
    
    return None
    
 
#turns detections on the yolo image

# detection = [label, bbox_x1 ,bbox_y1, bbox_x2, bbox_y2]
def get_yolo_detections_from_camera():

    detections = [] 
    
    rgb_scene_image = np.frombuffer(cam.getImage(), np.uint8).reshape((480,640,4))
    rbg_scene_image_with_detections, detections= detect_image(yolo, rgb_scene_image, "" , input_size=YOLO_INPUT_SIZE, show=False, rectangle_colors=(255,0,0))
    cv2.imshow('Detections', rbg_scene_image_with_detections)
    

    return detections
    
def go_to_object_table(table):
    print("hello")

    
def robot_state_manager(self):
    
    if(robot_state.is_spinning):
    
        print(spinning)
        detections = [] 
        objects = []  

        detections = get_yolo_detections_from_camera()    
        objects = get_object_and_global_coordinate_from_detection(detections)
        assign_objects_to_tables(objects)
        
        draw_map()
        
        spin(5)
        
    if(robot_state.is_awaiting_command):
        print(is_awaiting_command) 
        best_table = find_table_wtih_best_match("horse", table_containers, model)
        
    if(robot_state.is_executing_command):
        print(is_executing_command)
        
        
def filter_objects(objects, acceptance_count):

    for object in objects:
    
        object_name  =  object[0]
            
        if(object_name in unfiltered_objects.keys()):
        
            count = unfiltered_objects[object_name][0] + 1
            unfiltered_objects[object_name] = [count, object]
        
        if(object_name not in unfiltered_objects.keys()):
            count = 1
            unfiltered_objects[object_name] = [count, object]
            
    for object in unfiltered_objects:
        
        if(unfiltered_objects[object][0] >= acceptance_count):
            filtered_objects[unfiltered_objects[object][1][0]] = unfiltered_objects[object][1][1]
            
    

    
        
while robot.step(timestep) != -1:
    ds = [x.getValue() for x in dss]
    if time.time()-last > 0.031:
        last = time.time()
        

        #robot_state = RobotStateMachine()
        #print(robot_state.is_spinning)
        detections = [] 
        objects_with_local_coordinates = []
        objects_with_global_coordinates = []  

        detections = get_yolo_detections_from_camera()
        #change name of range finder and compass
        objects_with_local_coordinates = get_object_and_local_coordinate_from_detections(detections,rangeFinder) 
        objects_with_global_coordinate = get_object_and_global_coordinate_from_local_coordinate(objects_with_local_coordinates, robot_gps, compass)
        
        #get normal results
        #assign_objects_to_tables(objects)
        
        #to get filtered results
        filter_objects(objects_with_global_coordinate, 5)
        assign_objects_to_tables(filtered_objects)
        
        
        draw_scene_map(table_containers, robot_gps)
        #draw_map()
        
        print("table1", table1)
        print("table2", table2)
        print("table3", table3)
        print("table4", table4)

        cv2.waitKey(10)

            
        follow_path(5,left_path_ir, right_path_ir, wheels)
            
       # best_table = find_table_wtih_best_match("horse", table_containers, model)
        #print("similarity, best_table", best_table)

        
        
        
        


# Enter here exit cleanup code.
