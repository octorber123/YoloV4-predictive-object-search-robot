import numpy as np
import cv2


def draw_rectangle(image3, i_w, i_h, ratio, x, y, w, h, colour=(255,0,0)):
    tlx = int(ratio*(x-w/2.))+int(i_w/2)
    tly = int(ratio*(y-h/2.))+int(i_h/2)
    brx = int(ratio*(x+w/2.))+int(i_w/2)-1
    bry = int(ratio*(y+h/2.))+int(i_h/2)-1
 
    cv2.line(image3, (tlx,tly),(brx,tly),colour,3)
    cv2.line(image3, (tlx,bry),(brx,bry),colour,3)
    cv2.line(image3, (tlx,tly),(tlx,bry),colour,3)
    cv2.line(image3, (brx,tly),(brx,bry),colour,3)


room_width = 5.
map_res = 800.


k = 0
while k != 27:
    room_map = np.full((int(map_res),int(map_res),3), 255, dtype=np.uint8)
    draw_rectangle(room_map, map_res, map_res, map_res/room_width,  0,  0, room_width, room_width)
    draw_rectangle(room_map, map_res, map_res, map_res/room_width,  2,  0, 0.7, 1.2, (0,255,0))
    draw_rectangle(room_map, map_res, map_res, map_res/room_width, -2,  0, 0.7, 1.2, (0,255,0))
    draw_rectangle(room_map, map_res, map_res, map_res/room_width,  0,  2, 1.2, 0.7, (0,255,0))
    draw_rectangle(room_map, map_res, map_res, map_res/room_width,  0, -2, 1.2, 0.7, (0,255,0))
   
    cv2.namedWindow("test")

    cv2.imshow("test", room_map)
    k = cv2.waitKey(0)
