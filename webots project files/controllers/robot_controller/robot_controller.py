import sys
import cv2
import time
from MiniMap import *
from RobotNavigator import *
from ObjectDetector import *
from CoordinateManager import *
#from RobotStateMachine import *
from ObjectSearchManager import * 
from controller import Robot, RangeFinder



robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())
step = 0.0
last = time.time()

#initialise components of robot
wheels = [robot.getDevice('wheel'+str(x+1)) for x in range(4)]
for w in wheels:
    w.setPosition(float('inf'))
    w.setVelocity(0.)

dss = [robot.getDevice('ds_right'), robot.getDevice('ds_left')]
for x in dss:
    x.enable(10)

right_path_ir = robot.getDevice('path-following-IR-sensor-right')
right_path_ir.enable(30)

left_path_ir = robot.getDevice('path-following-IR-sensor-left')
left_path_ir.enable(30)

range_finder = robot.getDevice('range-finder')
range_finder.enable(30)

robot_camera = robot.getDevice('camera')
robot_camera.enable(30)

robot_compass = robot.getDevice('compass')
robot_compass.enable(30)

robot_gps = robot.getDevice('gps')
robot_gps.enable(30)



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

def assign_list_of_objects_to_tables(objects):
 
    for object in objects:
           
        shortest = 1500
        for index in range(len(tables)):
            print()
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

        
while robot.step(timestep) != -1:
    ds = [x.getValue() for x in dss]
    if time.time()-last > 0.031:
        last = time.time()
        

        #robot_state = RobotStateMachine()
        #print(robot_state.is_spinning)
   

        detections = get_yolo_detections_from_camera(robot_camera)
        filtered_detections = filter_detections(detections, 5)

        objects_with_local_coordinates = get_object_and_local_coordinate_from_detections(filtered_detections,range_finder) 
        objects_with_global_coordinate = get_object_and_global_coordinate_from_local_coordinate(objects_with_local_coordinates, robot_gps, robot_compass)

        assign_list_of_objects_to_tables(objects_with_global_coordinate)

        draw_scene_map(table_containers, robot_gps)

        print("table1", table1)
        print("table2", table2)
        print("table3", table3)
        print("table4", table4)
        
        best_table = find_table_wtih_best_match("mouse", table_containers)
        print("similarity, best_table", best_table)

        

            
        spin_on_spot(5, wheels)
            
        cv2.waitKey(10)

        
        
        
        


# Enter here exit cleanup code.
