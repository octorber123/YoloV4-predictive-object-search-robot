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


# create the Robot instance.
robot = Robot()
yolo = Load_Yolo_model()
model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary = True, limit = 100000)

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())
print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
wheels = [robot.getDevice('wheel'+str(x+1)) for x in range(4)]
for w in wheels:
    w.setPosition(float('inf'))
    w.setVelocity(0.)

dss = [robot.getDevice('ds_right'), robot.getDevice('ds_left')]
for x in dss:
    x.enable(10)
cam = robot.getDevice('camera')
cam.enable(30)

rangeFinder = robot.getDevice('range-finder')
rangeFinder.enable(30)

gps = robot.getDevice('gps')
gps.enable(30)

compass = robot.getDevice('compass')
compass.enable(30)

step = 0.0
# Main loop:
# - perform simulation steps until Webots is stopping the controller

last = time.time()

commands = [0. for x in range(4)]


def random_turn():
    speed = 0#(random.random()-0.5)*10.
    time = random.random()*3.
    print(speed, time)
    return speed, time
        
    
def distance_to_speed(sensor_value):
    return (sensor_value - 500) / 100.

def tokenize(text):   
    return re.split('\s|(?<!\d)[,.](?!\d)', text.lower())


def draw_rectangle(image3, i_w, i_h, ratio, x, y, w, h, colour=(255,0,0)):
    tlx = int(ratio*(x-w/2.))+int(i_w/2)
    tly = int(ratio*(y-h/2.))+int(i_h/2)
    brx = int(ratio*(x+w/2.))+int(i_w/2)-1
    bry = int(ratio*(y+h/2.))+int(i_h/2)-1
 
    cv2.line(image3, (tlx,tly),(brx,tly),colour,3)
    cv2.line(image3, (tlx,bry),(brx,bry),colour,3)
    cv2.line(image3, (tlx,tly),(tlx,bry),colour,3)
    cv2.line(image3, (brx,tly),(brx,bry),colour,3)
    
    
def draw_map(roomWidth, mapRes, objects):

    room_width = roomWidth
    map_res = mapRes
    room_map = np.full((int(map_res),int(map_res),3), 255, dtype=np.uint8)
    draw_rectangle(room_map, map_res, map_res, map_res/room_width,  0,  0, room_width, room_width)
    draw_rectangle(room_map, map_res, map_res, map_res/room_width,  3,  0, 0.7, 3.2, (0,255,0))
    draw_rectangle(room_map, map_res, map_res, map_res/room_width, -3,  0, 0.7, 3.2, (0,255,0))
    draw_rectangle(room_map, map_res, map_res, map_res/room_width,  0,  3, 3.2, 0.7, (0,255,0))
    draw_rectangle(room_map, map_res, map_res, map_res/room_width,  0, -3, 3.2, 0.7, (0,255,0))
    
    draw_rectangle(room_map, map_res, map_res, map_res/room_width,  int(gps.getValues()[0]) , int(gps.getValues()[2]), 0.5, 0.5,  (255,255,255))
    for obj in objects:
        

        draw_rectangle(room_map, map_res, map_res, map_res/room_width,   int(objects[obj][0]), int(objects[obj][1]), 0.5, 0.5,(255,255,0))
    
    cv2.namedWindow("test")

    cv2.imshow("test", room_map)
        
        
    
    
def y_rot_matrix(angle2):
    angle = -angle2
    ret = np.ndarray((3,3))
    ret[0][0] =  cos(angle);    ret[0][1] = 0;    ret[0][2] = sin(angle)
    ret[1][0] =           0;    ret[1][1] = 1;    ret[1][2] =          0
    ret[2][0] = -sin(angle);    ret[2][1] = 0;    ret[2][2] = cos(angle)
    return ret

def findTable_BestMatch(object_name, table_containers, model):
#iterate through all objects in the tables and compare the similarity 
#of the query object with object in the tables
##return the highest similarity and best table (table where most similar obj was found)
    
    bestSimilarity = None
    best_table = None
    for table in table_containers:
        for k in table:
            similarity = model.similarity(k, object_name)
            if bestSimilarity is None:
                bestSimilarity = similarity
                best_table = table
    
            elif similarity > bestSimilarity:
                bestSimilarity = similarity
                best_table = table
            
    return bestSimilarity, best_table
     

     
def get_object_and_global_coordinate_from_detection(detection):

    label = tokenize(detection[0])[0]   
    bbox_x1 = detection[1]
    bbox_y1 = detection[2]
    bbox_x2 = detection[3]
    bbox_y2 = detection[4]
                
                
    #get position of object from robot perspective
            
    #find mid point on detection boxes, and get how far obj is from robot, this is the depth
            
    bbox_midCordinate = (bbox_x1 + bbox_x2)/2, (bbox_y1 + bbox_y2)/2
    depth = rangeFinder.rangeImageGetDepth(rangeImage, rangeFinder.getWidth(), int(bbox_midCordinate[0]), int(bbox_midCordinate[1]))
    #use trigonometry to find lateral length of the object
    angle = (rangeFinder.getFov()*(bbox_midCordinate[0] - (rangeFinder.getWidth()/2))) /rangeFinder.getWidth()
    lateralLength = math.sin(angle)*depth        
            
    #get homogeneous matrix of the robot from the world origin

    robot_position = np.array([gps.getValues()[0], 0, gps.getValues()[2]])
    robot_bearing_from_world = atan2(compass.getValues()[2], compass.getValues()[0])
    robot_bearing_from_world_rotation_matrix = y_rot_matrix(-robot_bearing_from_world)
          
    object_position_from_robot = np.array([[-lateralLength], [0], [depth], [1]])

    tm = TransformManager()
    robot2world = pt.transform_from(robot_bearing_from_world_rotation_matrix, robot_position)
    tm.add_transform('robot', 'world', robot2world)
    final_transform = tm.get_transform('robot', 'world')
         
    object_position_from_world = final_transform @ object_position_from_robot
    #formate to only include x and z cood oin final answer
    object_position_from_world = [object_position_from_world[0] , object_position_from_world[2]]
    #print(f'result:\n{object_position_from_world.transpose()}')

    object = [label ,object_position_from_world]
    
    return object
    
def assign_object_to_table(object1):

    object = object1
    objects[object[0]] = object[1]
    
    shortest = 1500
    for index in range(len(tables)):
                
        distance = math.sqrt((object[1][0] - tables[index][1])**2 + (object[1][1] - tables[index][2])**2)

        if distance < shortest:
            shortest = distance
            table = tables[index][0]

    if table == "table1":
        table1[object[0]] = object[1]

                  
    if table == "table2":
        table2[object[0]] = object[1]

                    
    if table == "table3":
        table3[object[0]] = object[1]

                   
    if table == "table4":
        table4[object[0]] = object[1]
     
    
    return None
    

#first value is table cood known
objects = {}

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

while robot.step(timestep) != -1:
    ds = [x.getValue() for x in dss]
    if time.time()-last > 0.031:
        last = time.time()
        
        
        detections = []        

        rgb_scene_image = np.frombuffer(cam.getImage(), np.uint8).reshape((480,640,4))
        rangeImage = rangeFinder.getRangeImage()
        #img, x1, y1, x2, y2, detections = detect_image(yolo, rgb_scene_image, "" , input_size=YOLO_INPUT_SIZE, show=False, rectangle_colors=(255,0,0))
        rbg_scene_image_with_detections, detections= detect_image(yolo, rgb_scene_image, "" , input_size=YOLO_INPUT_SIZE, show=False, rectangle_colors=(255,0,0))
        cv2.imshow('Detections', rbg_scene_image_with_detections)     
        
        
        for obj in range(len(detections)):
            #if tokenize(detections[obj])[0] != "person":
             #   continue
            
            object = get_object_and_global_coordinate_from_detection(detections[obj])        
            assign_object_to_table(object)
            
            print(objects)
            
            #draw_map(7, 800, objects)
            
           # print("table1", table1)
            #print("table2", table2)
            #print("table3", table3)
            #print("table4", table4)
            
            #similarity, best_table = findTable_BestMatch("bottle", table_containers, model)
            #print("similarity, best_table", similarity, best_table)

          
        
        
        k = cv2.waitKey(1)
        wheel_speed = 9.
        if k == 119 or k == 82:
            for i in range(4):
                wheels[i].setVelocity(wheel_speed)
        elif k == 115 or k == 84:
            for i in range(4):
                wheels[i].setVelocity(-wheel_speed)
        elif k == 100 or k == 83:
            wheels[0].setVelocity(+wheel_speed)
            wheels[1].setVelocity(-wheel_speed)
            wheels[2].setVelocity(+wheel_speed)
            wheels[3].setVelocity(-wheel_speed)
        elif k == 97 or k == 81:
            wheels[0].setVelocity(-wheel_speed)
            wheels[1].setVelocity(+wheel_speed)
            wheels[2].setVelocity(-wheel_speed)
            wheels[3].setVelocity(+wheel_speed)
        elif k == 27 or k == 113:
            sys.exit(0)
        elif k == -1:
            for i in range(4):
                wheels[i].setVelocity(0.0)
        else:
            print('key', k)

# Enter here exit cleanup code.
