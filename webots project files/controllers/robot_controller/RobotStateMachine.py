from MiniMap import *
from RobotNavigator import *
from ObjectDetector import *
from CoordinateManager import *
from ObjectSearchManager import *
from TableClusterManager import *
from statemachine import StateMachine, State

best_tables_order = []
#stopping_angle = None
#spinning_finished = False

class RobotStateMachine(StateMachine):

    def __init__(self) :
        super().__init__()
        self.query_object = None
        self.target_table_position = None
        self.target_table = None
        self.stopping_angle = None


#states of robot
    spinning = State('spinning', initial=True)
    awaiting_command = State('Awaiting Command')
    executing_command = State('Executing Command')

#transitions between states
    done_spinning = spinning.to(awaiting_command)
    got_command = awaiting_command.to(executing_command)
    finished_execution = executing_command.to(spinning)

#method for transitions

    def on_done_spinning(self):
        print("finished spinning!")

    
    def on_got_command(self):
        print("")

    def on_finished_execution(self):
        print("back to spinning")

        
   

    def action(self ,table_containers, robot_camera, range_finder, robot_compass, robot_gps, robot_wheels):

        if(self.is_spinning):
    

            detections = get_yolo_detections_from_camera(robot_camera)
            filtered_detections = filter_detections(detections, 5)
    
            objects_with_local_coordinates = get_object_and_local_coordinate_from_detections(filtered_detections,range_finder) 
            objects_with_global_coordinate = get_object_and_global_coordinate_from_local_coordinate(objects_with_local_coordinates, robot_gps, robot_compass)

            assign_list_of_objects_to_tables(table_containers, objects_with_global_coordinate)
            draw_scene_map(table_containers, robot_gps) 

            finished_spinning = self.spin_on_spot_once(robot_compass,robot_wheels)

            if finished_spinning == True:
                self.done_spinning()




        
        if(self.is_awaiting_command):
            self.query_object = input("please enter an object to find : ")


            if self.query_object != "":
                self.target_table_position = get_best_match_table_position(self.query_object, table_containers)
                self.target_table = get_best_match_table(self.query_object, table_containers)
                
                
                self.got_command()
            else: 
                self.query_object = input("invalid input, please try again : ")

            
            

                
        
        if(self.is_executing_command):
            reached = go_to_position(self.target_table_position, 10, robot_wheels, robot_gps, robot_compass)
            print(reached)

            
            if reached == True:
                finished_spinning = self.spin_on_spot_once(robot_compass,robot_wheels)

                if finished_spinning == True:
                
                    is_found = find_object_on_table(self.target_table, self.query_object)

                    if is_found == True:
                        print("object found!!")
                    else:
                        print("still not found")
                    self.finished_execution()
                    


                if finished_spinning == False:

                    detections = get_yolo_detections_from_camera(robot_camera)
                    filtered_detections = filter_detections(detections, 5)
            
                    objects_with_local_coordinates = get_object_and_local_coordinate_from_detections(filtered_detections,range_finder) 
                    objects_with_global_coordinate = get_object_and_global_coordinate_from_local_coordinate(objects_with_local_coordinates, robot_gps, robot_compass)

                    assign_list_of_objects_to_tables(table_containers, objects_with_global_coordinate)


 
            draw_scene_map(table_containers, robot_gps)

    

    def spin_on_spot_once(self, robot_compass, robot_wheels):
        is_done = False

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
                is_done = True
                

        return is_done




