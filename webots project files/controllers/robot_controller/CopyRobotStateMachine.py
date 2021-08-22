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
        self.stopping_angle = None



#states of robot
    initial_spinning = State('spinning', initial=True)
    awaiting_command = State('Awaiting Command')
    processing_command = State('Processing Command')
    navigating_to_destination = State('Navigating to destination')
    inspecting_tables = State('Inspecting tables')
    verifying_object_presence = ('Verifying object presence')

#transitions between states
    get_command = initial_spinning.to(awaiting_command)
    process_command = awaiting_command.to(processing_command)
    navigate_to_destination = processing_command.to(navigating_to_destination)
    inspect_tables = navigating_to_destination.to(inspecting_tables)
    verify_object_presence = inspecting_tables.to(verifying_object_presence)



#method for transitions

    def on_get_command(self):
        print("finished spinning!")

    
    def on_process_command(self):
        print("")

    def on_navigate_to_destination(self):
        print("")
    
    def on_inspect_tables(self):
        print("")

    def on_verify_object_presence(self):
        print("")

   # def on_finished_execution(self):
   #     print("back to spinning")   
    
    def action1(self ,table_containers, robot_camera, range_finder, robot_compass, robot_gps, robot_wheels):
        

        if self.is_initial_spinning :

            detections = get_yolo_detections_from_camera(robot_camera)
            filtered_detections = filter_detections(detections, 5)
            
            objects_with_local_coordinates = get_object_and_local_coordinate_from_detections(filtered_detections,range_finder) 
            objects_with_global_coordinate = get_object_and_global_coordinate_from_local_coordinate(objects_with_local_coordinates, robot_gps, robot_compass)

            assign_list_of_objects_to_tables(table_containers, objects_with_global_coordinate)
            draw_scene_map(table_containers, robot_gps) 

            finished_spinning = self.spin_on_spot_once(robot_compass,robot_wheels)

            if finished_spinning == True:
                self.get_command()

        if self.is_awaiting_command :
            self.query_object = input("please enter an object to find : ")

            if self.query_object != "":               
                self.process_command()
            else: 
                self.query_object = input("invalid input, please try again : ")
        

        if self.is_processing_command :

            self.target_table_position = get_best_match_table_position(self.query_object, table_containers)
            self.target_table = get_best_match_table(self.query_object, table_containers)

            self.navigate_to_destination()


        if self.is_navigating_to_destination :

            reached_table = go_to_position(self.target_table_position, 10, robot_wheels, robot_gps, robot_compass)
            if reached_table == True:
                
                self.inspect_tables()

        if self.is_inspecting_tables :

            finished_spinning = self.spin_on_spot_once(robot_compass,robot_wheels)

            if finished_spinning == False:

                detections = get_yolo_detections_from_camera(robot_camera)
                filtered_detections = filter_detections(detections, 5)
            
                objects_with_local_coordinates = get_object_and_local_coordinate_from_detections(filtered_detections,range_finder) 
                objects_with_global_coordinate = get_object_and_global_coordinate_from_local_coordinate(objects_with_local_coordinates, robot_gps, robot_compass)

                assign_list_of_objects_to_tables(table_containers, objects_with_global_coordinate)
                
            elif finished_spinning == True:

                self.verify_object_presence()


        if self.is_verifying_object_presence :

            is_found = find_object_on_table(self.target_table, self.query_object)

            if is_found == True:
                print("object found!!")
            else:
                print("still not found")

            print("all states work in round 1")
            self.finished_execution()



            

    def spin_on_spot_once(self, robot_compass, robot_wheels):
        finished_spinning_once = False

        if self.stopping_angle == None:
            self.stopping_angle = atan2(robot_compass.getValues()[2], robot_compass.getValues()[0]) 

        current_angle = atan2(robot_compass.getValues()[2], robot_compass.getValues()[0])

        spin_on_spot(5, robot_wheels)

        offset_one = 0.1 + self.stopping_angle
        offset_two = 0.2 + self.stopping_angle

        if offset_one > 3.1 or offset_two > 3.1:
                
                offset_one = -3 
                offset_two = -2.9

        if  offset_one  < current_angle  and current_angle < offset_two:
                spin_on_spot(0, robot_wheels)
                self.stopping_angle = None
                finished_spinning_once = True
                

        return finished_spinning_once




