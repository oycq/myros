#!/usr/bin/env python
import rospy
import std_msgs.msg
import cv2
import time
from sensor_msgs.msg import Joy
from std_msgs.msg import String,Int16MultiArray

image_path = ''
mouse_x = 400
mouse_y = 400
box_w = 50
traking_pt1 = (0,0)
traking_pt2 = (0,0)

def mouse_callback(event,x,y,flags,param):
    global mouse_x, mouse_y, pt1, pt2
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x = x
        mouse_y = y

def caculate_box_points(x,y,width,img_shape):
    d = width // 2
    a1,a2 = max(0, x - d), max(y - d, 0)
    b1,b2 = min(img_shape[1], x+d), min(img_shape[0], y+d)
    pt1 = (a1,a2)
    pt2 = (b1,b2)
    return pt1,pt2


last_lock_key = 0
def joy_callback(a):
    global box_w,mouse_x,mouse_y,last_lock_key
    if a.buttons[6] == 1:
        box_w -= 1
    if a.buttons[8] == 1:
        box_w += 1
    if a.buttons[13] == 1:
        mouse_x -= 3
    if a.buttons[11] == 1:
        mouse_x += 3
    if a.buttons[12] == 1:
        mouse_y += 3
    if a.buttons[10] == 1:
        mouse_y -= 3
    if box_w < 4:
        box_w == 4
    if a.buttons[0] == 0:
        last_lock_key = 0
    if  a.buttons[0] == 1:
        if last_lock_key == 0:
            lockon_commmand_pub.publish('lockon %d %d %d %d'%(pt1[0], pt1[1],pt2[0],pt2[1]))
        last_lock_key = 1


#    print(a.axes[3], a.buttons[0])

def image_path_callback(a):
    global image_path
    image_path = a.data

def tracking_info_callback(a):
    global traking_pt1, traking_pt2
    traking_pt1 = (a.data[0], a.data[1])
    traking_pt2 = (a.data[2], a.data[3])
    

if __name__ == '__main__':
    rospy.init_node('display_node', anonymous=False)
    rospy.Subscriber("image_path", std_msgs.msg.String, image_path_callback)
    rospy.Subscriber("joy", Joy, joy_callback)
    rospy.Subscriber('tracking_info', Int16MultiArray, tracking_info_callback)
    lockon_commmand_pub = rospy.Publisher('lockon_command_node', String, queue_size = 1)
    cv2.namedWindow('img')
    cv2.setMouseCallback('img',mouse_callback)
    while not rospy.is_shutdown():
        if image_path == '':
            time.sleep(0.1)
            continue
        t1 = time.time() * 1000
        raw = cv2.imread(image_path)
        cv2.circle(raw, (960,600), 10,(255,0,0), 2)
        pt1,pt2 = caculate_box_points(mouse_x, mouse_y, box_w, raw.shape)
        cv2.rectangle(raw,pt1,pt2,(0,255,0),2)
        cv2.rectangle(raw,traking_pt1,traking_pt2,(0,0,255),2)
        cv2.imshow('img',raw)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        if key == ord(' '):
            lockon_commmand_pub.publish('lockon %d %d %d %d'%(pt1[0], pt1[1],pt2[0],pt2[1]))
