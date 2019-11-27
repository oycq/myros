import os
import numpy as np
import cv2
import serial#sudo pip3 install pyserial
import time
import rospy                                                                                     
import std_msgs.msg
from std_msgs.msg import String,Int16MultiArray

image_path = ''

def image_path_callback(a):
    global image_path
    image_path = a.data

if __name__ == '__main__':


    ser=serial.Serial("/dev/ttyUSB1",115200,timeout=0.001)
    rospy.init_node('camera_latency_test_node', anonymous=False)
    rospy.Subscriber("image_path", std_msgs.msg.String, image_path_callback)

    while(1):
        if image_path == '':
            time.sleep(0.1)
            continue
        image = cv2.imread(image_path)
        cv2.imshow("image",image)
        key = cv2.waitKey(1)
#        print((time.time() - last_time)* 1000, end = '\r')
        last_time = time.time()
        if key == ord('q'):
            os._exit(0)
            break
        if key == ord('t'):
            image0 = cv2.imread(image_path, 0)
            time0 = time.time()   
            ser.write(' '.encode())	

            image1 = cv2.imread(image_path)
            time1 = (time.time() - time0) * 1000   

            image2 = cv2.imread(image_path)
            time2 = (time.time() - time0 ) * 1000   

            image3 = cv2.imread(image_path)
            time3 =(time.time() - time0) * 1000

            image4 = cv2.imread(image_path)
            time4 = (time.time() - time0) * 1000   

            image5 = cv2.imread(image_path)
            time5 = (time.time() - time0 ) * 1000   

            image6 = cv2.imread(image_path)
            time6 =(time.time() - time0) * 1000

            image7 = cv2.imread(image_path)
            time7 = (time.time() - time0) * 1000   

            image8 = cv2.imread(image_path)
            time8 = (time.time() - time0 ) * 1000   

            image9 = cv2.imread(image_path)
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
     

