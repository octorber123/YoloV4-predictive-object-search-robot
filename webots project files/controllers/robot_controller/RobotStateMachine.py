from statemachine import StateMachine, State

class RobotStateMachine(StateMachine):

#states of robot
    spinning = State('spinning', initial=True)
    awaiting_command = State('Awaiting Command')
    executing_command = State('Executing Command')

#transitions between states

    get_command = spinning.to(awaiting_command)
    find_object = awaiting_command.to(executing_command)
    back_to_spin = awaiting_command.to(spinning)
    return_to_get_command = executing_command.to(awaiting_command)
    
#method for transitions

    def on_get_command(self):
        print('enter the object to find:')
    
    def on_find_object(self):
        print("finding object")
        
    def on_back_to_spin(self):
        print("no response, back to spinning! ")
        
    def on_return_to_get_command(self):
        print("object found/notfound,  please enter another object to find")
    
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
        
        
    

    




