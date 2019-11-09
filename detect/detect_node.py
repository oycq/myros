#!/usr/bin/env python
import rospy
import std_msgs.msg
import cv2
import time
from sensor_msgs.msg import Joy

image_path = ''

def callback(a):
    global image_path
    image_path = a.data

if __name__ == '__main__':
    rospy.init_node('detect_node', anonymous=False)
    rospy.Subscriber("image_path", std_msgs.msg.String, callback)
    control_pub = rospy.Publisher('gimbal_control', Joy, queue_size = 1)
    while not rospy.is_shutdown():
        if image_path == '':
            time.sleep(0.1)
            continue
        t1 = time.time() * 1000
        raw = cv2.imread(image_path)
        t2 = time.time() * 1000
        high_light = raw.max()
        image = raw.copy()
        image.fill(0)
        image[raw < 150] = 255 
        t3 = time.time() * 1000
        a = image.shape[0]
        b = image.shape[1]
        max_pos = raw.argmax()
        t4 = time.time() * 1000
        if b == 0:
            print('error here eads')
            break
        x = (max_pos // b) - a // 2 
        y = (max_pos % b) - b // 2

        image[a // 2 - 4 : a // 2 + 2, :].fill(0)
        image[: , b // 2 - 4 : b // 2 + 4].fill(0)
        cv2.imshow('image',cv2.resize(image,(380,240)))

        if high_light < 150 or abs(x) > 590 or abs(y) > 950:
            control_pub.publish(axes = (0, 0, 0))
            #control_pub.publish(0, y / 500, 0)
        cv2.waitKey(1)
        print(t2 - t1, t3 -t2, t4 -t1)
