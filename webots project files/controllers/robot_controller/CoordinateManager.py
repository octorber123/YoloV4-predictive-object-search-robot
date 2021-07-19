import re
import math
import numpy as np

from pytransform3d import rotations as pr
from math import sin, cos, atan2, sqrt, pi
from pytransform3d import transformations as pt
from pytransform3d.transform_manager import TransformManager


def get_object_and_local_coordinate_from_detections(detections, range_finder):

    """
    this method - calculates object position from perspective of robot.

    :param detection     : a list containing the names of objects and coordiantes (top left and bottom right corner) of their bounding boxes
    :param range_finder  : is robot's range finder sensor

    :return: a list with object names , lateral lengths and their depths.
    """ 
    objects_and_local_coordinates = []
    for detection in detections:
        label = tokenize(detection[0])[0]
        bbox_x1 = detection[1]
        bbox_y1 = detection[2]
        bbox_x2 = detection[3]
        bbox_y2 = detection[4]
		        
        # get midpoint of bounding box            
        bbox_midCordinate = (bbox_x1 + bbox_x2)/2, (bbox_y1 + bbox_y2)/2
    
        range_image = range_finder.getRangeImage()
        depth = range_finder.rangeImageGetDepth(range_image, range_finder.getWidth(), int(bbox_midCordinate[0]), int(bbox_midCordinate[1]))
    
        #use trigonometry to find lateral length of the object
        angle = (range_finder.getFov()*(bbox_midCordinate[0] - (range_finder.getWidth()/2))) /range_finder.getWidth()
        lateral_length = math.sin(angle)*depth  
    
        objects_and_local_coordinates.append([label, lateral_length, depth])

    return objects_and_local_coordinates


def get_object_and_global_coordinate_from_local_coordinate(objects_with_local_coordinates, robot_gps, robot_compass):

    """
    this method - uses kinematics to calculate the object's global coordinate from its local coordinate( which is from the robot).

    :param object_with_local_coordinate  : list contains the names of objects, and their local coordinates (lateral length and depth)
    :param robot_gps                     : is robot's gps sensor
    :param robot_compass                 : is robot's compass sensor
    
    :return: a list with objects names' and their global coordinate
    """ 
    objects_with_global_coordinates = []
    
    for object in objects_with_local_coordinates:

        label = object[0]
        lateral_length = object[1]
        depth = object[2]

        object_position_from_robot = np.array([[-lateral_length], [0], [depth], [1]])
    
        robot_position_in_world = np.array([robot_gps.getValues()[0], 0, robot_gps.getValues()[2]])
        robot_bearing_from_world = atan2(robot_compass.getValues()[2], robot_compass.getValues()[0])
        robot_bearing_from_world_rotation_matrix = y_rot_matrix(-robot_bearing_from_world)

        tm = TransformManager()
        #get homogeneous matrix robot->world 
        robot2world = pt.transform_from(robot_bearing_from_world_rotation_matrix, robot_position_in_world)
        
        tm.add_transform('robot', 'world', robot2world)
        robot_to_world = tm.get_transform('robot', 'world')
    
        #multiply robot -> world homogenous matrix with local object coordinate to get glocal object coordinate
        object_position_from_world = robot_to_world @ object_position_from_robot
        object_position_from_world = [object_position_from_world[0] , object_position_from_world[2]]


        objects_with_global_coordinates.append([label ,object_position_from_world])
    
    return objects_with_global_coordinates
    
def get_object_and_global_coordinate_from_detections(detections, range_finder, robot_gps, robot_compass):
    
    objects_with_global_cood = []
    
    for detection in detections:

        label = tokenize(detection[0])[0]
        bbox_x1 = detection[1]
        bbox_y1 = detection[2]
        bbox_x2 = detection[3]
        bbox_y2 = detection[4]
		        
        # get midpoint of bounding box            
        bbox_midCordinate = (bbox_x1 + bbox_x2)/2, (bbox_y1 + bbox_y2)/2
    
        range_image = range_finder.getRangeImage()
        depth = range_finder.rangeImageGetDepth(range_image, range_finder.getWidth(), int(bbox_midCordinate[0]), int(bbox_midCordinate[1]))
    
        #use trigonometry to find lateral length of the object
        angle = (range_finder.getFov()*(bbox_midCordinate[0] - (range_finder.getWidth()/2))) /range_finder.getWidth()
        lateral_length = math.sin(angle)*depth  
                
        object_position_from_robot = np.array([[-lateral_length], [0], [depth], [1]])
    
        robot_position_in_world = np.array([robot_gps.getValues()[0], 0, robot_gps.getValues()[2]])
        robot_bearing_from_world = atan2(robot_compass.getValues()[2], robot_compass.getValues()[0])
        robot_bearing_from_world_rotation_matrix = y_rot_matrix(-robot_bearing_from_world)
          

        tm = TransformManager()
        #get  matrix robot->world 
        robot2world = pt.transform_from(robot_bearing_from_world_rotation_matrix, robot_position_in_world)
        tm.add_transform('robot', 'world', robot2world)
        robot_to_world_matrix = tm.get_transform('robot', 'world')
    
        #multiply robot -> world  matrix with local object coordinate to get glocal object coordinate
        object_position_from_world = robot_to_world_matrix @ object_position_from_robot
        object_position_from_world = [object_position_from_world[0] , object_position_from_world[2]]
    
        
        objects_with_global_cood.append([label ,object_position_from_world])
    
    return objects_with_global_cood
    
def get_local_coordinate_of_point(point_position, robot_gps, robot_compass):
        

    point_position_from_world = np.array([[point_position[0]], [0], [point_position[1]], [1]])

    robot_position_in_world = np.array([robot_gps.getValues()[0], 0, robot_gps.getValues()[2]])
    robot_bearing_from_world = atan2(robot_compass.getValues()[2], robot_compass.getValues()[0])
    robot_bearing_from_world_rotation_matrix = y_rot_matrix(-robot_bearing_from_world)
          

    tm = TransformManager()
    #get  matrix robot->world 
    robot2world = pt.transform_from(robot_bearing_from_world_rotation_matrix, robot_position_in_world)
    tm.add_transform('robot', 'world', robot2world)
    world_to_robot_matrix = tm.get_transform('world', 'robot')
    
    #multiply world -> robot matrix with global point coordinate to get local point coordinate
    point_position_from_robot = world_to_robot_matrix @ point_position_from_world
    point_position_from_robot = [point_position_from_robot[0] , point_position_from_robot[2]]
    
    return point_position_from_robot
    
def get_angle_of_point_from_robot(point_position):

    angle = atan2(point_position[0],point_position[1]) 

    return angle

    
def tokenize(text):
    #DELIM = '[ \r\n\t0123456789;:.,/\(\)\"\'-]+'   
    DELIM = '\s|(?<!\d)[,.](?!\d)'  
    return re.split(DELIM, text.lower())
    
    
def y_rot_matrix(angle2):
    angle = -angle2
    ret = np.ndarray((3,3))
    ret[0][0] =  cos(angle);    ret[0][1] = 0;    ret[0][2] = sin(angle)
    ret[1][0] =           0;    ret[1][1] = 1;    ret[1][2] =          0
    ret[2][0] = -sin(angle);    ret[2][1] = 0;    ret[2][2] = cos(angle)
    return ret


