#!/usr/bin/env python
import rospy
import std_msgs.msg
import cv2
import time
from sensor_msgs.msg import Joy
from std_msgs.msg import String,Int16MultiArray
import SharedArray as sa
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import CompressedImage
from sensor_msgs.msg import Image
import os
import subprocess


bridge = CvBridge()
image_path = ''
x = {}
mouse_x = 400
mouse_y = 400
box_w = 50
traking_pt1 = (0,0)
traking_pt2 = (0,0)
detect_pt1 = (0,0)
detect_pt2 = (0,0)
new_image = 0
record_state = 0
rosbag_proc = None
gimbal_following_mode = 0

#def mouse_callback(event,x,y,flags,param):
#    global mouse_x, mouse_y, pt1, pt2
#    if event == cv2.EVENT_MOUSEMOVE:
#        mouse_x = x
#        mouse_y = y

def caculate_box_points(x,y,width,img_shape):
    d = width // 2
    a1,a2 = max(0, x - d), max(y - d, 0)
    b1,b2 = min(img_shape[1], x+d), min(img_shape[0], y+d)
    pt1 = (a1,a2)
    pt2 = (b1,b2)
    return pt1,pt2

def j1_callback(a):
    global gimbal_following_mode 
    if a.buttons[21] == 0:
        if a.buttons[22] == 0:
            gimbal_following_mode = 0
        else:
            gimbal_following_mode = 2
    else:
        gimbal_following_mode = 1




last_lock_key = 0
last_buttons = None
def j0_callback(a):
    global box_w,mouse_x,mouse_y,last_lock_key,record_state, last_buttons,rosbag_proc
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
        box_w = 4
    if a.buttons[0] == 0:
        last_lock_key = 0
    if  a.buttons[0] == 1:
        if last_lock_key == 0:
            lockon_commmand_pub.publish('lockon %d %d %d %d'%(pt1[0], pt1[1],pt2[0],pt2[1]))
        last_lock_key = 1
    if a.buttons[1] == 1:
        if last_buttons[1] == 0:
            if record_state == 0:
                rosbag_proc = subprocess.Popen('rosbag record -o ~/catkin_ws/src/myros/store/ -a __name:=my_bag',shell=True)
                rosbag_proc = subprocess.Popen('pwd',shell=True)
            else:
                os.system('rosnode kill my_bag')
            record_state = (record_state + 1) % 2
    last_buttons = a.buttons

#    print(a.axes[3], a.buttons[0])

def image_path_callback(a):
    global image_path, x, new_image
    image_path = a.data
    new_image += 1
    if a.data not in x:
        x[a.data] = sa.attach(a.data)   

def tracking_info_callback(a):
    global traking_pt1, traking_pt2
    traking_pt1 = (a.data[1], a.data[2])
    traking_pt2 = (a.data[3], a.data[4])

def detect_info_callback(a):
    global detect_pt1,detect_pt2
    detect_pt1 = (a.data[1], a.data[2])
    detect_pt2 = (a.data[3], a.data[4])
    
how_many_dot = 0
def draw_text(image):
    global how_many_dot
    font = cv2.FONT_HERSHEY_SIMPLEX 
    org = (20, 30) 
    fontScale = 0.7
    color = (0, 0, 255) 
    thickness = 2
    if record_state:
        how_many_dot = (how_many_dot + 1) % 99 
        string_list = ['Record','Record .','Record . .']
        image = cv2.putText(image, string_list[how_many_dot//33], org, font,  
                   fontScale, color, thickness, cv2.LINE_AA) 
    return image 

    

if __name__ == '__main__':
    dispaly_image_pub = rospy.Publisher('display_image/compressed', CompressedImage, queue_size=1)
    #dispaly_image_pub = rospy.Publisher('display_image', Image, queue_size=1)
    rospy.init_node('display_node', anonymous=False)
    rospy.Subscriber("/camera0/image_path/", std_msgs.msg.String, image_path_callback)
    rospy.Subscriber("/joy/j0", Joy, j0_callback)
    rospy.Subscriber("/joy/j1", Joy, j1_callback)
    rospy.Subscriber('/tracking/tracking_info', Int16MultiArray, tracking_info_callback)
    rospy.Subscriber('/cnn/detect_info', Int16MultiArray, detect_info_callback)
    lockon_commmand_pub = rospy.Publisher('lockon_command', String, queue_size = 1)
#    cv2.namedWindow('img', cv2.WND_PROP_FULLSCREEN)
#    cv2.setWindowProperty("img",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
#    cv2.setMouseCallback('img',mouse_callback)
    while not rospy.is_shutdown():
        if image_path == '':
            time.sleep(0.1)
            continue
        t0 = time.time() * 1000
        while not rospy.is_shutdown():
            if new_image >= 2:
                new_image = 0
                break
            else:
                time.sleep(0.0002)
        t1 = time.time() * 1000
        raw = x[image_path].copy()
        pt1,pt2 = caculate_box_points(mouse_x, mouse_y, box_w, raw.shape)
        if gimbal_following_mode == 1:
            cv2.rectangle(raw,pt1,pt2,(0,255,0),2)
            cv2.rectangle(raw,traking_pt1,traking_pt2,(0,0,128),2)
#        if gimbal_following_mode == 2:
        cv2.rectangle(raw,detect_pt1,detect_pt2,(128,0,0),2)


        image = cv2.resize(raw,(1024,768))
        cv2.circle(image, (512,384), 3,(0,0,255), 1)
        image = draw_text(image)
        t2 = time.time() * 1000
        ros_image = bridge.cv2_to_compressed_imgmsg(image, "jpeg")
        dispaly_image_pub.publish(ros_image)
        t3 = time.time() * 1000
#        key = cv2.waitKey(1)
###        print('%7.2f %7.2f %7.2f %7.2f'%(t1-t0, t2-t1, t3-t2, t3-t0))
#        if key == ord('q'):
#            break
