import numpy as np
from CoordinateManager import *

def follow_path(max_speed, path_ir_sensor_left, path_ir_sensor_right, wheels):
    """
    this method makes the robot follow a path

    :param max_speed             : max turn speed
    :param wheels                : the  motors of the robot
    :param path_ir_sensor_left   : the infrared sensor facing on the groung for path detection on the left
    :param path_ir_sensor_right  : the infrared sensor facing on the groung for path detection on the right
    
    
    :return: None
    """ 
    
    left_speed = max_speed
    right_speed = max_speed
      
    left_ir_value = path_ir_sensor_left.getValue()
    right_ir_value = path_ir_sensor_right.getValue()
        
    if(left_ir_value > right_ir_value and 129 < left_ir_value < 337):
        
        left_speed = -left_speed * 0.20
        
    if(right_ir_value > left_ir_value and 129 < right_ir_value < 337):

        right_speed = -right_speed * 0.20

   
    wheels[0].setVelocity(left_speed)
    wheels[1].setVelocity(right_speed)
    wheels[2].setVelocity(left_speed)
    wheels[3].setVelocity(right_speed)
    
def spin_on_spot(max_speed, wheels):


    left_speed = max_speed 
    right_speed = -max_speed
      
   
    wheels[0].setVelocity(left_speed)
    wheels[1].setVelocity(right_speed)
    wheels[2].setVelocity(left_speed)
    wheels[3].setVelocity(right_speed)

def go_to_position(global_point_cood, max_speed, wheels, robot_gps, robot_compass):

    local_point_position = get_local_coordinate_of_point(global_point_cood, robot_gps, robot_compass)
    point_angle = get_angle_of_point_from_robot(local_point_position)

    angle_offset = 0.1
    distance_offset = 1.5
  
    reached = False
    distance = np.linalg.norm(local_point_position)

    left_speed = max_speed * 0.5
    right_speed = max_speed * 0.5
    
    if point_angle > angle_offset:
        left_speed = -max_speed * 0.1
        right_speed = max_speed * 0.1
        
    if point_angle < -angle_offset:
        left_speed = max_speed * 0.1
        right_speed = -max_speed * 0.1
        
    if distance < distance_offset:
        left_speed = 0
        right_speed = 0
        reached = True
    
    wheels[0].setVelocity(left_speed)
    wheels[1].setVelocity(right_speed)
    wheels[2].setVelocity(left_speed)
    wheels[3].setVelocity(right_speed)
    
    return reached
    

def turn_to_point(global_point, max_speed, robot_gps, robot_compass, wheels):

    local_point_position = get_local_coordinate_of_point(global_point, robot_gps, robot_compass)
    point_angle = get_angle_of_point_from_robot(local_point_position)

    angle_offset = 0.1

    left_speed = -max_speed * 0.0
    right_speed = max_speed * 0.0

    if point_angle > angle_offset:
        left_speed = -max_speed  
        right_speed = max_speed 
        
    if point_angle < -angle_offset:
        left_speed = max_speed 
        right_speed = -max_speed 

    
    wheels[0].setVelocity(left_speed)
    wheels[1].setVelocity(right_speed)
    wheels[2].setVelocity(left_speed)
    wheels[3].setVelocity(right_speed)
    

    if left_speed == 0 and right_speed == 0:
        reached = True
    else:
        reached = False

    return reached

            
def setSpeed( adv, rot, wheels):
    
    radius=0.04
    separation=0.12
    max_speed=10
    left_wheel  = (adv - (rot*separation)/2.) / radius
    right_wheel = (adv + (rot*separation)/2.) / radius
    left  = max(min( left_wheel, max_speed), -max_speed)
    right = max(min(right_wheel, max_speed), -max_speed)
    wheels[0].setVelocity(left)
    wheels[1].setVelocity(right)
    wheels[2].setVelocity(left)
    wheels[3].setVelocity(right)