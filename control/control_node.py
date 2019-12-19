import rospy
import std_msgs.msg
from geometry_msgs.msg import Vector3
from sensor_msgs.msg import Joy
import serial 
import time
import os
import struct

def rc_callback(a):
    print(a.axes)

if __name__ == '__main__':
    rospy.init_node('control_node', anonymous=False)
    rospy.Subscriber("/dji_sdk/rc", Joy, rc_callback)
    rospy.spin()

    


