#!/usr/bin/env python
import rospy
import std_msgs.msg
import cv2
import time
from sensor_msgs.msg import Joy
from std_msgs.msg import String,Int16MultiArray

image_path = ''

bbox = (0,0,0,0)

#tracker = cv2.TrackerKCF_create()
tracker = cv2.TrackerCSRT_create()
state = False

def image_path_callback(a):
    global image_path
    image_path = a.data

def lockon_command_callback(a):
    print(a)
    global tracker,bbox, raw_img, state
    a = a.data.split(' ')
    if a[0] == 'lockon':
        a1, a2, a3, a4 = int(a[1]), int(a[2]), int(a[3]), int(a[4])
        b1, b2 = a3 - a1, a4 - a2
        bbox = (a1, a2, b1, b2)
        tracker = cv2.TrackerCSRT_create()
        tracker.init(raw_img, bbox)
        state = True

if __name__ == '__main__':
    rospy.init_node('traking_node', anonymous=False)
    rospy.Subscriber("image_path", String, image_path_callback)
    rospy.Subscriber("lockon_command_node", String, lockon_command_callback)
    control_pub = rospy.Publisher('gimbal_control', Joy, queue_size = 1)
    tracking_info_pub = rospy.Publisher('tracking_info', Int16MultiArray, queue_size = 1)
    while not rospy.is_shutdown():
        if image_path == '':
            time.sleep(0.1)
            continue
        raw_img = cv2.imread(image_path, cv2.IMREAD_ANYCOLOR)
        if state is True:
            state, bbox = tracker.update(raw_img)
            pt1 = (int(bbox[0]),int(bbox[1]))
            pt2 = (int(bbox[0]+bbox[2]),int(bbox[1]+bbox[3]))
            a = Int16MultiArray()
            a.data = (pt1[0], pt1[1], pt2[0], pt2[1],\
                    raw_img.shape[1], raw_img.shape[0])
            tracking_info_pub.publish(a)
#            display_img = raw_img.copy()
#            cv2.rectangle(display_img,pt1,pt2,(0,0,255),2)
#        else:
#            display_img = raw_img.copy()
#        cv2.imshow('display', display_img)
#        key = cv2.waitKey(1)
#        if key == ord('q'):
#            break

