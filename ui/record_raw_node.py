#!/usr/bin/env python
import rospy
import std_msgs.msg
import cv2
import time
from sensor_msgs.msg import Joy
from std_msgs.msg import String,Int16MultiArray
import SharedArray as sa
from datetime import datetime


image_path = ''
x = {}
record_state = 0
image_shape = None
start_time = None
video_writer = None
new_frame = 0

def image_path_callback(a):
    global image_path, x, new_frame
    image_path = a.data
    new_frame = 1
    if a.data not in x:
        x[a.data] = sa.attach(a.data)   

last_joy_state = 0
def joy_callback(a):
    global last_joy_state, start_time, video_writer,record_state
    if a.buttons[1] == 1:
        if last_joy_state == 0:
            if record_state == 0:
                if video_writer is not None:
                    video_writer.release()
                print('start recording')
                start_time = time.time() 
                date_time = datetime.now().strftime("20%y-%m-%d-%H:%M:%S")
                video_writer = cv2.VideoWriter('../store/%s.avi'%date_time, \
                        cv2.VideoWriter_fourcc(*'MJPG'), 30, (image_shape[1],image_shape[0]))
            #    video_writer = cv2.VideoWriter('../store/%s.avi'%date_time, \
            #            cv2.VideoWriter_fourcc(*'avc1'), 30, (image_shape[1],image_shape[0]))

                print(video_writer)
                record_state = 1
            else:
                record_state = 0
                print('stop recording')
    last_joy_state = a.buttons[1]


if __name__ == '__main__':
    rospy.init_node('record_raw_node', anonymous=False)
    rospy.Subscriber("image_path", std_msgs.msg.String, image_path_callback)
    rospy.Subscriber("joy", Joy, joy_callback)
    record_state_pub = rospy.Publisher('record_state', String, queue_size = 1)
    while(not rospy.is_shutdown()):
        if image_path is not '':
            img = x[image_path].copy()
            image_shape = img.shape
            break

    while(not rospy.is_shutdown()):
        if not (new_frame and record_state):
            time.sleep(0.001)
        else:
            time0 = time.time()
            img = x[image_path].copy()
            cv2.imwrite('../store/0.bmp',img)
            #video_writer.write(img)
            time1 = time.time()
            print(time1 * 1000 - time0 * 1000)

