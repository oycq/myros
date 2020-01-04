#!/usr/bin/env python
import rospy
from std_msgs.msg import UInt8
from geometry_msgs.msg import Vector3
from sensor_msgs.msg import Joy
from dji_sdk.srv import SDKControlAuthority
from std_msgs.msg import Int16MultiArray
import serial 
import time
import os
import struct
import math 

DJI_ONLINE = 1
JOY_CONTROL_EXP = 5.5
TRAKING_K = 0.1

height_p = 0
distance_p = 0
angle_p = 0
gimbal_position_mode = 0
gimbal_following_mode = 0
joy0_pitch = 0
joy0_yaw = 1
joy0_data_available = 0
joint_yaw = 0
joint_pitch = 0
joint_data_available = 0
gimbal_imu_pitch = 0
gimbal_imu_yaw = 0
gimbal_imu_data_available = 0
tracking_condition = 0
tracking_x = 0
tracking_z = 0
tracking_data_available = 0
detect_condition = 0
detect_x = 0
detect_z = 0
detect_data_available = 0


def rc_callback(a):
    pass

def joint_angle_callback(a):
    global joint_data_available, joint_yaw, joint_pitch 
    joint_yaw = a.x
    joint_pitch = a.z
    joint_data_available = 1
    control_data = Joy()
    control_data.axes = [0,0,0,0,0]
    control_data.axes[0] = distance_p * 4
    control_data.axes[1] = 0
    control_data.axes[2] = -height_p * a.z / 90
    control_data.axes[3] = -angle_p * a.x / 90
    control_data.axes[4] = 74
    dji_control_publisher.publish(control_data)

def gimbal_imu_callback(a):
    global gimbal_imu_data_available, gimbal_imu_yaw, gimbal_imu_pitch
    gimbal_imu_yaw = a.x
    gimbal_imu_pitch = a.z
    gimbal_imu_data_available = 1

def joy0_callback(a):
    global joy0_yaw, joy0_pitch, joy0_data_available
    joy0_pitch = -a.axes[1]
    joy0_yaw = -a.axes[0]
    joy0_data_available = 1

last_joy_state = None
def joy1_callback(a):
    global height_p, distance_p, angle_p,last_joy_state,\
            gimbal_following_mode, gimbal_position_mode
    height_p = (a.axes[2] + 1) / 2 
    angle_p = (a.axes[3] + 1) / 2
    distance_p = a.axes[4]
    if a.buttons[12] == 0:
        if a.buttons[13] == 0:
            gimbal_position_mode = 0
        else:
            gimbal_position_mode = 2
    else:
        gimbal_position_mode = 1
    if a.buttons[21] == 0:
        if a.buttons[22] == 0:
            gimbal_following_mode = 0
        else:
            gimbal_following_mode = 2
    else:
        gimbal_following_mode = 1
    if DJI_ONLINE:
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

def tracking_info_callback(a):
    global tracking_x, tracking_z, tracking_condition, tracking_data_available
    tracking_condition = a.data[0]
    tracking_x = (a.data[1] + a.data[3] - a.data[5]) / 2 
    tracking_z = - (a.data[2] + a.data[4] - a.data[6]) / 2
    tracking_data_available = 1

def detect_info_callback(a):
    global detect_x, detect_z, detect_condition, detect_data_available
    detect_condition = a.data[0]
    detect_x = (a.data[1] + a.data[3] - a.data[5]) / 2 
    detect_z = - (a.data[2] + a.data[4] - a.data[6]) / 2
    detect_data_available = 1


if __name__ == '__main__':
    rospy.init_node('control_node', anonymous=False)
    rospy.wait_for_service('/dji_sdk/sdk_control_authority')
    control_authority = rospy.ServiceProxy('/dji_sdk/sdk_control_authority', SDKControlAuthority)
    rospy.Subscriber("/joy/j1", Joy, joy1_callback)
    rospy.Subscriber("/joy/j0", Joy, joy0_callback)
    rospy.Subscriber("/gimbal/joint_angle", Vector3, joint_angle_callback)
    rospy.Subscriber("/gimbal/imu_angle", Vector3, gimbal_imu_callback)
    rospy.Subscriber("/dji_sdk/rc", Joy, rc_callback)
    rospy.Subscriber('/tracking/tracking_info', Int16MultiArray, tracking_info_callback)
    rospy.Subscriber('/cnn/detect_info', Int16MultiArray, detect_info_callback)
    dji_control_publisher = rospy.Publisher('/dji_sdk/flight_control_setpoint_generic', Joy, queue_size=1)
    gimbal_speed_control_publisher = rospy.Publisher('/gimbal/speed_control', Vector3, queue_size=1)
    while not rospy.is_shutdown():
        time.sleep(0.0002)
        if gimbal_following_mode == 0 and gimbal_position_mode == 0:
            if not joy0_data_available:
                continue
            joy0_data_available = 0
            yaw_control = math.exp(JOY_CONTROL_EXP * abs(joy0_yaw)) -1
            pitch_control = math.exp(JOY_CONTROL_EXP * abs(joy0_pitch)) -1
            yaw_control *= -1 if joy0_yaw < 0 else 1
            pitch_control *= -1 if joy0_pitch < 0 else 1
            gimbal_speed_control_publisher.publish(yaw_control,0,pitch_control)
        if gimbal_following_mode == 0 and gimbal_position_mode in [1,2]:
            if not (joint_data_available and gimbal_imu_data_available):
                continue
            joint_data_available = 0
            gimbal_imu_data_available = 0
#            pitch_control = -100 * height_p * gimbal_imu_pitch
#            yaw_control = -100 * angle_p * joint_yaw
#            print(100 * height_p, 100 *angle_p)
            if gimbal_position_mode == 1:
                expect_yaw, expect_pitch = 0,0
            if gimbal_position_mode == 2:
                expect_yaw, expect_pitch = 0,-90
            pitch_control = 4.5 * (expect_pitch - gimbal_imu_pitch)
            yaw_control = 4.5 * (expect_yaw - joint_yaw)
            gimbal_speed_control_publisher.publish(yaw_control,0,pitch_control)
        if gimbal_following_mode == 1:
            if not tracking_data_available:
                continue
            tracking_data_available = 0
            if tracking_condition:
                gimbal_speed_control_publisher.publish(tracking_x*TRAKING_K, 0, tracking_z*TRAKING_K)
        if gimbal_following_mode == 2:
            if not detect_data_available:
                continue
            detect_data_available = 0
            if detect_condition:
                gimbal_speed_control_publisher.publish(detect_x*TRAKING_K, 0, detect_z*TRAKING_K)


