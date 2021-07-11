
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
    right_speed = max_speed * 0.5
      
   
    wheels[0].setVelocity(left_speed)
    wheels[1].setVelocity(right_speed)
    wheels[2].setVelocity(left_speed)
    wheels[3].setVelocity(right_speed)
