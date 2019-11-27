import os
import numpy as np
import cv2
import serial#sudo pip3 install pyserial
import time
import rospy                                                                                     
import std_msgs.msg
from std_msgs.msg import String,Int16MultiArray
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

image = None
bridge = CvBridge()

def image_callback(a):
    global image
    image = bridge.imgmsg_to_cv2(a, "passthrough")

if __name__ == '__main__':


    ser=serial.Serial("/dev/ttyUSB1",115200,timeout=0.001)
    rospy.init_node('camera_latency_test_node', anonymous=False)
    rospy.Subscriber("image", Image, image_callback)

    time.sleep(1)
    while(1):
        cv2.imshow("image",image)
        key = cv2.waitKey(1)
#        print((time.time() - last_time)* 1000, end = '\r')
        last_time = time.time()
        if key == ord('q'):
            os._exit(0)
            break
        if key == ord('t'):
            image0 = image.copy()
            time0 = time.time()   
            ser.write(' '.encode())	

            time.sleep(0.01)
            image1 = image.copy()
            time1 = (time.time() - time0) * 1000   


            image2 = image.copy()
            time2 = (time.time() - time0 ) * 1000   

            image3 = image.copy()
            time3 =(time.time() - time0) * 1000

            image4 = image.copy()
            time4 = (time.time() - time0) * 1000   

            image5 = image.copy()
            time5 = (time.time() - time0 ) * 1000   

            image6 = image.copy()
            time6 =(time.time() - time0) * 1000

            image7 = image.copy()
            time7 = (time.time() - time0) * 1000   

            image8 = image.copy()
            time8 = (time.time() - time0 ) * 1000   

            image9 = image.copy()
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
     

