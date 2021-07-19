import cv2
import numpy as np


def draw_scene_map(table_containers, robot_gps):

    """
    this method draws the room, robot , tables , and objects on tables

    :param table_containers  : contains list of tables and each table is has list of objects on them
    :param robot_gps         : used to draw the robot in scene
    
    :output: displays mini map
    """ 
    
    room_width = 7
    map_res = 700
    
    #define the room as an image
    room_map = np.full((int(map_res),int(map_res),3), 255, dtype=np.uint8)
    
    #draw room
    draw_rectangle(room_map, ' ', 0,  0, room_width, room_width)
    
    #draw the tables
    draw_rectangle( room_map, ' ', 3,  0, 0.7, 3.2, (0,255,0))
    draw_rectangle( room_map, ' ', -3,  0, 0.7, 3.2, (0,255,0))
    draw_rectangle( room_map, ' ', 0,  3, 3.2, 0.7, (0,255,0))
    draw_rectangle( room_map, ' ', 0, -3, 3.2, 0.7, (0,255,0))
    
    #draw robot
    draw_rectangle(room_map, 'robot',-robot_gps.getValues()[0], -robot_gps.getValues()[2], 0.1, 0.1 , (0,0,255))
    
    #draw objects
    for table in table_containers:

         for object in list(table.keys())[1:]:   
   
             draw_rectangle(room_map, object, -table[object][0], -table[object][1], 0.1, 0.1 , (0,0,0))
 
    cv2.namedWindow("map")
    cv2.imshow("map", room_map)
    
    
def draw_rectangle(image, label, x, y, w, h, colour=(255,0,0)):

    """
    this method draws a rectangle on an image
    
    :param image  : the image to draw rectangle on, should be as np array
    :param label  : the string label to be drawn right of the rectangle
    :param x, y   : the position of rectangle on the of image
    :param w      : the width of rectangle
    :param h      : the height of rectangle
    :param colour : the colour of rectangle
    
    :return: None
    """ 
    
    map_res = 700
    room_width = 7
    
    i_w = map_res
    i_h = map_res
    ratio = map_res/room_width
    
    
    tlx = int(ratio*(x-w/2.))+int(i_w/2)
    tly = int(ratio*(y-h/2.))+int(i_h/2)
    brx = int(ratio*(x+w/2.))+int(i_w/2)-1
    bry = int(ratio*(y+h/2.))+int(i_h/2)-1
 
    cv2.line(image, (tlx,tly),(brx,tly),colour,3)
    cv2.line(image, (tlx,bry),(brx,bry),colour,3)
    cv2.line(image, (tlx,tly),(tlx,bry),colour,3)
    cv2.line(image, (brx,tly),(brx,bry),colour,3)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.5
    thickness = 1
    offset = 5
    label_point = (brx+offset, bry+offset)
    
    cv2.putText(image, label, label_point, font, fontScale, colour, thickness, cv2.LINE_AA)
    
    
        
