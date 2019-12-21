import rospy
from std_msgs.msg import UInt8
from geometry_msgs.msg import Vector3
from sensor_msgs.msg import Joy
from dji_sdk.srv import SDKControlAuthority
import serial 
import time
import os
import struct

height_p = 0
distance_p = 0
angle_p = 0

def rc_callback(a):
    pass

def gimbal_callback(a):
    control_data = Joy()
    control_data.axes = [0,0,0,0,0]
    control_data.axes[0] = distance_p * 4
    control_data.axes[1] = 0
    control_data.axes[2] = -height_p * a.z / 90
    control_data.axes[3] = -angle_p * a.x / 90
    control_data.axes[4] = 74
    dji_control_publisher.publish(control_data)


last_joy_state = None
def joy_callback(a):
    global height_p, distance_p, angle_p,last_joy_state
    height_p = (a.axes[2] + 1) / 2 
    angle_p = (a.axes[3] + 1) / 2
    distance_p = a.axes[4]
    if last_joy_state is None:
        last_joy_state = a
        if a.buttons[23] == 1:
            control_authority(1)
            print('authority 1')
        else:
            control_authority(0)
            print('authority 0')


        return
    try:
        if last_joy_state.buttons[23] == 0:
            if a.buttons[23] == 1:
                control_authority(1)
                print('authority 1')
        else:
            if a.buttons[23] == 0:
                control_authority(0)
                print('authority 0')
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e
    last_joy_state = a

if __name__ == '__main__':
    rospy.init_node('control_node', anonymous=False)
    rospy.wait_for_service('/dji_sdk/sdk_control_authority')
    control_authority = rospy.ServiceProxy('/dji_sdk/sdk_control_authority', SDKControlAuthority)
    rospy.Subscriber("/joy/j1", Joy, joy_callback)
    rospy.Subscriber("/gimbal/joint_angle", Vector3, gimbal_callback)
    rospy.Subscriber("/dji_sdk/rc", Joy, rc_callback)
    dji_control_publisher = rospy.Publisher('/dji_sdk/flight_control_setpoint_generic', Joy, queue_size=1)
    rospy.spin()

    


