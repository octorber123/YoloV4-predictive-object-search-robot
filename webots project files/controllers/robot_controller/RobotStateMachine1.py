from MiniMap import *
from RobotNavigator import *
from ObjectDetector import *
from CoordinateManager import *
from ObjectSearchManager import *
from TableClusterManager import *
from statemachine import StateMachine, State

class RobotStateMachine(StateMachine):

    def __init__(self) :
        super().__init__()
        self.query_object = None
        self.target_table_position = None
        self.target_table = None
        self.robot_direction = None
        self.ordered_list_tables = None
        self.inspection_part_one_complete = False

#states of robot
    initial_spinning = State('initial_spinning', initial=True)
    awaiting_command = State('Awaiting Command')
    processing_command = State('Executing Command')
    navigating_to_destination = State("Navigating To Destination")
    inspecting_table = State("Inspecting Table")
    verifying_object_presence = State("Verifying Object Presence")

#transitions between states
    done_initial_spinning = initial_spinning.to(awaiting_command)
    got_command = awaiting_command.to(processing_command)
    processed_command = processing_command.to(navigating_to_destination)
    reached_destination = navigating_to_destination.to(inspecting_table)
    inspection_complete = inspecting_table.to(verifying_object_presence)
    object_verification_complete = verifying_object_presence.to(awaiting_command)
    object_not_found = verifying_object_presence.to(navigating_to_destination)
    
#method for transitions

    def on_done_initial_spinning(self):
        print("finished initial_spinning!")

    
    def on_got_command(self):
        print("")
   

    def action(self ,table_containers, robot_camera, range_finder, robot_compass, robot_gps, robot_wheels):
        draw_scene_map(table_containers, robot_gps) 

        if self.is_initial_spinning :
    

            detections = get_yolo_detections_from_camera(robot_camera)
            filtered_detections = filter_detections(detections, 5)
            objects_with_local_coordinates = get_object_and_local_coordinate_from_detections(filtered_detections,range_finder) 
            objects_with_global_coordinate = get_object_and_global_coordinate_from_local_coordinate(objects_with_local_coordinates, robot_gps, robot_compass)

            assign_list_of_objects_to_tables(table_containers, objects_with_global_coordinate)

            finished_initial_spinning = self.spin_on_spot_once(robot_compass,robot_wheels)

            if finished_initial_spinning == True:
                
                self.done_initial_spinning()

        
        if self.is_awaiting_command :
            self.query_object = input("please enter an object to find : ")


            if self.query_object != "":

                self.got_command()
            else: 
                self.query_object = input("invalid input, please try again : ")


        if self.is_processing_command :

            self.ordered_list_tables = get_list_of_best_match_tables(self.query_object, table_containers)
            self.processed_command()

        if self.is_navigating_to_destination :
            if len(self.ordered_list_tables) == 0 or len(self.ordered_list_tables) == None:
                raise Exception("no list of tables retured from best match table method, please check processing command state")
            else:
                self.target_table = self.ordered_list_tables[0]
                self.target_table_position = self.target_table["table_pos"]

            reached_table = go_to_position(self.target_table_position, 10, robot_wheels, robot_gps, robot_compass)      

            if reached_table == True:
                self.reached_destination()

        if self.is_inspecting_table :
            
            finished_inspection = self.inspect_table(robot_compass,robot_wheels)

            if finished_inspection == False:

                detections = get_yolo_detections_from_camera(robot_camera)
                filtered_detections = filter_detections(detections, 5)
        
                objects_with_local_coordinates = get_object_and_local_coordinate_from_detections(filtered_detections,range_finder) 
                objects_with_global_coordinate = get_object_and_global_coordinate_from_local_coordinate(objects_with_local_coordinates, robot_gps, robot_compass)

                assign_list_of_objects_to_tables(table_containers, objects_with_global_coordinate)
            
            elif finished_inspection == True:
                self.inspection_complete()
            
        if self.is_verifying_object_presence :
            is_found = find_object_on_table(self.target_table, self.query_object)

            if is_found == True:
                print(self.query_object + " found!!")
                self.ordered_list_tables = None
                self.object_verification_complete()
            else:
                
                self.ordered_list_tables.pop(0)
                if len(self.ordered_list_tables) == 0:

                    print("Sorry "+ self.query_object +" was not found on any table")
                    self.ordered_list_tables = None
                    self.object_verification_complete()
                else :
                    print(self.query_object +", not found, trying another table")
                    self.object_not_found()
            


    def inspect_table(self, robot_compass, robot_wheels):

        inspection_complete = False

        if self.robot_direction == None:
            self.robot_direction = robot_compass.getValues()

        if self.inspection_part_one_complete == False and inspection_complete == False:
            finished_clockwise_spin = self.half_turn_clockwise(robot_compass, robot_wheels)
            

            if finished_clockwise_spin == True:
                self.inspection_part_one_complete = True
                

        if self.inspection_part_one_complete == True:
            finished_anticlockwise_spin = self.half_turn_anticlockwise(robot_compass, robot_wheels)

            if finished_anticlockwise_spin == True:
                inspection_complete = True
                self.robot_direction = None
                self.inspection_part_one_complete = False
        
        return inspection_complete


    def half_turn_clockwise(self, robot_compass, robot_wheels):
        finished_clockwise_spin = False

        robot_direction = np.array([self.robot_direction[0], self.robot_direction[2]])
        stopping_bearing_one = robot_direction @ self.two_dimentional_rot_matrix(45)
        

        current_bearing = self.get_bearing_in_degrees(robot_compass, 0)
        stopping_bearing_one = self.get_bearing_in_degrees(None, stopping_bearing_one)
        stopping_bearing_two = stopping_bearing_one + 20

        spin_on_spot(5,robot_wheels)

        if stopping_bearing_two > 360:
            stopping_bearing_two = stopping_bearing_two - 360
            
        if stopping_bearing_two < stopping_bearing_one:
            if stopping_bearing_two > current_bearing:
                spin_on_spot(0,robot_wheels)
                finished_clockwise_spin= True

        elif stopping_bearing_one < current_bearing and stopping_bearing_two > current_bearing:
            spin_on_spot(0,robot_wheels)
            finished_clockwise_spin= True

        return finished_clockwise_spin

    def half_turn_anticlockwise(self, robot_compass, robot_wheels):
        finished_anticlockwise_spin = False

        robot_direction = np.array([self.robot_direction[0], self.robot_direction[2]])
        stopping_bearing_one = robot_direction @ self.two_dimentional_rot_matrix(-45)
        

        current_bearing = self.get_bearing_in_degrees(robot_compass, 0)
        stopping_bearing_one = self.get_bearing_in_degrees(None, stopping_bearing_one)
        stopping_bearing_two = stopping_bearing_one - 20

        spin_on_spot(-5,robot_wheels)

        if stopping_bearing_two < 0:
            stopping_bearing_two = stopping_bearing_two + 360
            
        if stopping_bearing_two > stopping_bearing_one:
            if stopping_bearing_two < current_bearing:
                spin_on_spot(0,robot_wheels)
                finished_anticlockwise_spin= True

        elif stopping_bearing_one > current_bearing and stopping_bearing_two < current_bearing:
            spin_on_spot(0,robot_wheels)
            finished_anticlockwise_spin= True                

        return finished_anticlockwise_spin

    def spin_on_spot_once(self, robot_compass, robot_wheels):
        finished_initial_spinning_once = False

        if self.robot_direction == None:
            self.robot_direction = atan2(robot_compass.getValues()[2], robot_compass.getValues()[0]) 

        
        current_angle = atan2(robot_compass.getValues()[2], robot_compass.getValues()[0])

        spin_on_spot(5, robot_wheels)

        offset_one = 0.1 + self.robot_direction
        offset_two = 0.2 + self.robot_direction

        if offset_one > 3.1 or offset_two > 3.1:
                
                offset_one = -3 
                offset_two = -2.9

        if  offset_one  < current_angle  and current_angle < offset_two:
                spin_on_spot(0, robot_wheels)
                self.robot_direction = None
                finished_initial_spinning_once = True
                

        return finished_initial_spinning_once

    def two_dimentional_rot_matrix(self, angle2):
        angle = angle2
        ret = np.ndarray((2,2))
        ret[0][0] =  cos(angle);    ret[0][1] = -sin(angle);  
        ret[1][0] =  sin(angle);    ret[1][1] =  cos(angle);    
        return ret
    

    def get_bearing_in_degrees(self, compass, north):
        if compass != None:
            north = compass.getValues()
            rad = atan2(north[0], north[2])

        else:
            rad = atan2(north[0], north[1])

        bearing = (rad - 1.5708) / math.pi * 180.0
        if bearing < 0.0:
            bearing = bearing + 360.0

        return bearing
        