from statemachine import StateMachine, State

class RobotStateMachine(StateMachine):

#states of robot
    spining = State('Spining', initial=True)
    awaiting_command = State('Awaiting Command')
    executing_command = State('Executing Command')

#transitions between states

    get_command = spining.to(awaiting_command)
    find_object = awaiting_command.to(executing_command)
    back_to_spin = awaiting_command.to(spining)
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



    
robot = RobotStateMachine()
#print(robot.current_state)

robot.get_command()
#print(robot.current_state)

robot.back_to_spin()
#print(robot.current_state)

robot.get_command()
#print(robot.current_state)

robot.find_object()
#print(robot.current_state)

robot.return_to_get_command()
#print(robot.current_state)

robot.back_to_spin()
#print(robot.current_state)



