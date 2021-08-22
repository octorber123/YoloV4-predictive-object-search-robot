import sys
sys.path.append('/usr/local/webots/lib/controller/python38/')
import time
import cv2
from MiniMap import *
from RobotNavigator import *
from ObjectDetector import *
from CoordinateManager import *
from RobotStateMachine import *
from ObjectSearchManager import * 
from TableClusterManager import *
from controller import Robot, RangeFinder



robot = Robot()
# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())
step = 0.0
last = time.time()

#initialise components of robot
robot_wheels = [robot.getDevice('wheel'+str(x+1)) for x in range(4)]
for w in robot_wheels:
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



table1 = {}
table1["table_pos"] = [0,3]
table2 = {}
table2["table_pos"] = [-3,0]
table3 = {}
table3["table_pos"] = [0,-3]
table4 = {}
table4["table_pos"] = [3,0]

table_containers = [table1, table2, table3, table4]
robot_state_machine = RobotStateMachine()

def two_dimentional_rot_matrix(angle2):
    angle = -angle2
    ret = np.ndarray((2,2))
    ret[0][0] =  cos(angle);    ret[0][1] = -sin(angle);  
    ret[1][0] =  sin(angle);    ret[1][1] =  cos(angle);    
    return ret


query = None 
x = 0
stopping_angle = None    
while robot.step(timestep) != -1:
    ds = [x.getValue() for x in dss]
    if time.time()-last > 0.031:
        last = time.time()


        robot_state_machine.action(table_containers, robot_camera, range_finder, robot_compass, robot_gps, robot_wheels)

        cv2.waitKey(10)
  
        

        
        
        
        


