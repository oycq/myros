#!/usr/bin/env python
import rospy
import std_msgs.msg
import cv2
import time
from sensor_msgs.msg import Joy
from std_msgs.msg import String,Int16MultiArray
import time
import SharedArray as sa

image_path = ''
x = {}

bbox = (0,0,0,0)

def create_tracker():
    #return cv2.TrackerKCF_create()

    csrt = cv2.TrackerCSRT_create()
    #csrt_setting = cv2.FileStorage("csrt_settings.yaml",cv2.FILE_STORAGE_WRITE) 
    #csrt.write(csrt_setting)
    #csrt_settings = cv2.FileStorage("csrt_settings.yaml",cv2.FILE_STORAGE_READ)
    #csrt.read(csrt_settings.root())
    return csrt

    #return cv2.TrackerMOSSE_create()
    #return cv2.TrackerMedianFlow_create()


tracker = create_tracker()
state = False

def image_path_callback(a):
    global image_path,x
    image_path = a.data
    if a.data not in x:
        x[a.data] = sa.attach(a.data)

def lockon_command_callback(a):
    print(a)
    global tracker,bbox, raw_img, state
    a = a.data.split(' ')
    if a[0] == 'lockon':
        a1, a2, a3, a4 = int(a[1]), int(a[2]), int(a[3]), int(a[4])
        b1, b2 = a3 - a1, a4 - a2
        bbox = (a1, a2, b1, b2)
        tracker = create_tracker()
        tracker.init(raw_img, bbox)
        state = True

if __name__ == '__main__':
    rospy.init_node('traking_node', anonymous=False)
    rospy.Subscriber("/camera0/image_path", String, image_path_callback)
    rospy.Subscriber("/ui/lockon_command", String, lockon_command_callback)
    tracking_info_pub = rospy.Publisher('tracking_info', Int16MultiArray, queue_size = 1)
    while not rospy.is_shutdown():
        if image_path == '':
            time.sleep(0.1)
            continue
        raw_img = x[image_path].copy()
        if state is True:
            state, bbox = tracker.update(raw_img)
            pt1 = (int(bbox[0]),int(bbox[1]))
            pt2 = (int(bbox[0]+bbox[2]),int(bbox[1]+bbox[3]))
            a = Int16MultiArray()
            a.data = (1, pt1[0], pt1[1], pt2[0], pt2[1],\
                    raw_img.shape[1], raw_img.shape[0])
            tracking_info_pub.publish(a)
        else:
            a = Int16MultiArray()
            a.data = (0, 0, 0, 0, 0,
                    raw_img.shape[1], raw_img.shape[0])
            tracking_info_pub.publish(a)
            time.sleep(0.02)


#            display_img = raw_img.copy()
#            cv2.rectangle(display_img,pt1,pt2,(0,0,255),2)
#        else:
#            display_img = raw_img.copy()
#        cv2.imshow('display', display_img)
#        key = cv2.waitKey(1)
#        if key == ord('q'):
#            break

