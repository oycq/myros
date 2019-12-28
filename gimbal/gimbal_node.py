#!/usr/bin/env python
import rospy
import std_msgs.msg
from geometry_msgs.msg import Vector3
from sensor_msgs.msg import Joy
from std_msgs.msg import Int16MultiArray
import serial 
import time
import os
import struct
from threading import Lock

ser = serial.Serial('/dev/gimbal_uart',115200)  # open serial port
time.sleep(1)

def speed_control(speed_pitch = 0, speed_roll = 0, speed_yaw = 0):
    angle_pitch = 0
    angle_roll = 0
    angle_yaw = 0
    mode = 1
    command_id = 67
    payload_size = 3 + 2 * 3 + 2 * 3
    header_check_sum = (command_id + payload_size) % 256

    speed_roll  = int(speed_roll/0.1220740379)
    angle_roll  = int(angle_roll/0.02197265625)
    speed_pitch = int(speed_pitch/0.1220740379)
    angle_pitch = int(angle_pitch/0.02197265625)
    speed_yaw   = int(speed_yaw/0.1220740379)
    angle_yaw   = int(angle_yaw/0.02197265625)
    
    payload = struct.pack('<BBBhhhhhh', mode, mode, mode, 
            speed_roll, angle_roll, speed_pitch, angle_pitch, speed_yaw, angle_yaw)
    payload_check_sum = 0
    try:
        for byte_int in payload:
            payload_check_sum = (payload_check_sum + ord(byte_int)) % 256
    except TypeError:
        for byte_int in payload:
            payload_check_sum = (payload_check_sum + byte_int) % 256
    bytes_to_send = b'\x3e' + struct.pack('<BBB',command_id, payload_size, header_check_sum)\
                + payload + struct.pack('<B',payload_check_sum)
    o = time.time() *1000
    ser.write(bytes_to_send)
    ser.read(6)

def send_cmd(command_id):
    payload_size = 0
    header_check_sum = (command_id + payload_size) % 256
    bytes_to_send = b'\x3e' + struct.pack('<BBBBB',
            command_id, payload_size, header_check_sum, 0, 0)
    ser.write(bytes_to_send)
    ser.read(6)

def motor_off():
    send_cmd(109)

def motor_on():
    send_cmd(77)

def get_status():
    mode = 281
    command_id = 88 
    payload_size = 10
    header_check_sum = (command_id + payload_size) % 256
    payload = struct.pack('<IHHH', mode, 0,0,0)
    payload_check_sum = 0
    try:
        for byte_int in payload:
            payload_check_sum = (payload_check_sum + ord(byte_int)) % 256
    except TypeError:
        for byte_int in payload:
            payload_check_sum = (payload_check_sum + int(byte_int)) % 256
    payload_check_sum_1u = struct.pack('<B',payload_check_sum) 
    
    bytes_to_send = b'\x3e' + struct.pack('<BBBIHHHB', 
                command_id , payload_size , header_check_sum, \
                mode, 0,0,0,  payload_check_sum)
    ser.write(bytes_to_send)
    payload = ser.read(31)
    payload = payload[4:30]
    imu_angle = []
    imu_speed = []
    imu_acc = []
    joint_angle = []
    for i in range(12):
        data = struct.unpack('<h',payload[i*2 + 2: i*2 + 4])[0]
        if i in [0,1,2]:
            imu_angle.append(data * 0.02197265625)
        if i in [3,4,5]:
            joint_angle.append(data * 0.02197265625)
        if i in [6,7,8]:
            imu_speed.append(data * 0.06103701895)
        if i in [9,10,11]:
            imu_acc.append(data / 512)
#    print('%15.2f   %15.2f   %15.2f'%(imu_angle[0], imu_angle[1], imu_angle[2]),end = '\r')
#    print('%15.2f   %15.2f   %15.2f'%(joint_angle[0], joint_angle[1], joint_angle[2]))
#    print('%15.2f   %15.2f   %15.2f'%(imu_speed[0], imu_speed[1], imu_speed[2]),end = '\r')
#    print('%15.2f   %15.2f   %15.2f'%(imu_acc[0], imu_acc[1], imu_acc[2]),end = '\r')
    return imu_angle,imu_speed,imu_acc,joint_angle


speed_pitch = 0
speed_roll = 0
speed_yaw = 0
lock = Lock()
good_track = 0
use_traking_data = False
pitch_control = 0
yaw_control = 0
roll_control = 0

def gimbal_speed_control(a):
    global yaw_control, pitch_control, roll_control
    yaw_control = a.x
    roll_control = a.y
    pitch_control = a.z

if __name__ == '__main__':
    rospy.init_node('gimbal_node', anonymous=False)
    rospy.Subscriber("speed_control", Vector3, gimbal_speed_control)
    gimbal_imu_angle = rospy.Publisher('imu_angle', Vector3, queue_size=1)
    gimbal_imu_speed = rospy.Publisher('imu_speed', Vector3, queue_size=1)
    gimbal_joint_angle = rospy.Publisher('joint_angle', Vector3, queue_size=1)
    while not rospy.is_shutdown():
        imu_angle,imu_speed,imu_acc,joint_angle = get_status()
        gimbal_imu_angle.publish(imu_angle[2], imu_angle[0], -imu_angle[1])
        gimbal_imu_speed.publish(imu_speed[2], imu_speed[1], imu_speed[0])
        gimbal_joint_angle.publish(joint_angle[2], joint_angle[0], -joint_angle[1])
        speed_control(-pitch_control, roll_control, yaw_control)


#    motor_on()
##    while(1):
##        get_status()
#    speed_control(10,0,0)
#    time.sleep(0.5)
#    speed_control(-10,0,0)
#    time.sleep(0.5)
#    speed_control(0,10,0)
#    time.sleep(0.5)
#    speed_control(0,-10,0)
#    time.sleep(0.5)
#    speed_control(0,0,10)
#    time.sleep(0.5)
#    speed_control(0,0,-10)
#    time.sleep(0.5)
#    speed_control(0,0,0)
