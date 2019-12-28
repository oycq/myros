import os
import numpy as np
import cv2
import serial#sudo pip3 install pyserial
import time
import rospy                                                                                     
import std_msgs.msg
from std_msgs.msg import String,Int16MultiArray
import SharedArray as sa

from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image

bridge = CvBridge()
realsense_image = None
realsense_available = 0

image_path = ''
x = {}

def realsense_callback(a):
    global realsense_image, realsense_available
    realsense_image = bridge.imgmsg_to_cv2(a, "bgr8")
    realsense_available = 1

def got():
    global realsense_available
    while(not realsense_available):
        time.sleep(0.00001)
    realsense_available = 0
    return realsense_image

if __name__ == '__main__':
    ser=serial.Serial("/dev/ttyUSB1",115200,timeout=0.001)
    rospy.init_node('camera_latency_test_node', anonymous=False)
    rospy.Subscriber("/camera/color/image_raw",Image, realsense_callback)

    while(not rospy.is_shutdown()):
        if realsense_image is None:
            time.sleep(0.1)
            continue
        image = got()
        cv2.imshow("image",image)
        key = cv2.waitKey(1)
#        print((time.time() - last_time)* 1000, end = '\r')
        last_time = time.time()
        if key == ord('q'):
            os._exit(0)
            break
        if key == ord('t'):
            image0 = got()
            time0 = time.time()   
            ser.write(' '.encode())	
            time.sleep(0.010)

            image1 = got()
            time1 = (time.time() - time0) * 1000   

            image2 = got()
            time2 = (time.time() - time0 ) * 1000   

            image3 = got()
            time3 =(time.time() - time0) * 1000

            image4 = got()
            time4 = (time.time() - time0) * 1000   

            image5 = got()
            time5 = (time.time() - time0 ) * 1000   
            image6 = got()
            time6 =(time.time() - time0) * 1000

            image7 = got()
            time7 = (time.time() - time0) * 1000   

            image8 = got()
            time8 = (time.time() - time0 ) * 1000   

            image9 = got()
            time9 =(time.time() - time0) * 1000


            cv2.imshow('before key', image0)
            cv2.imshow('%.2fms' % time1, image1)
            cv2.imshow('%.2fms' % time2, image2)
            cv2.imshow('%.2fms' % time3, image3)
            cv2.imshow('%.2fms' % time4, image4)
            cv2.imshow('%.2fms' % time5, image5)
            cv2.imshow('%.2fms' % time6, image6)
            cv2.imshow('%.2fms' % time7, image7)
            cv2.imshow('%.2fms' % time8, image8)
            cv2.imshow('%.2fms' % time9, image9)

        if key == ord('r'):
            cv2.destroyAllWindows()
    ser.close()
     

