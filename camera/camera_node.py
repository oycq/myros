#!/usr/bin/env python
import rospy
import std_msgs.msg
import PySpin
import numpy as np
import cv2
import serial#sudo pip3 install pyserial
import time
import io 
import os
import SharedArray as sa
import thread
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image

setting_list = [
    ['TriggerMode'           , 'Off'      , 'General'],
    ['StreamBufferHandlingMode'  , 'NewestOnly'      , 'Stream' ],
    ['AcquisitionMode'           , 'Continuous'      , 'General'],
#    ['PixelFormat'           , 'BayerRG8'    , 'stream'],
                ]

class Camera():
    def config_camera(self):
        cam = self.cam
        setting_list = self.setting_list
        for i in range(len(setting_list)):
            if setting_list[i][2] == 'General':
                nodemap = cam.GetNodeMap()
            if setting_list[i][2] == 'Stream':
                nodemap = cam.GetTLStreamNodeMap()
            attribute = setting_list[i][0]
            value =  setting_list[i][1]
            node =  PySpin.CEnumerationPtr(nodemap.GetNode(attribute))
            if not PySpin.IsAvailable(node) or not PySpin.IsWritable(node):
                print('Unable to set attribute : %s'%attribute)
                continue
            node_new_value = node.GetEntryByName(value)
            if not PySpin.IsAvailable(node_new_value) or not PySpin.IsReadable(node_new_value):
                print('Cant set %s --> %s'%(value,attribute))
                continue
            node.SetIntValue(node_new_value.GetValue())

        node_pixel_format = PySpin.CEnumerationPtr(nodemap.GetNode('PixelFormat'))

    def __init__(self):
        self.setting_list = setting_list
        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        num_cameras = self.cam_list.GetSize()
        if num_cameras == 0:
            self.cam_list.Clear()
            self.system.ReleaseInstance()
            print('Not enough cameras!')
            os._exit(0)
        self.cam = self.cam_list[0]
        self.cam.Init()
        self.config_camera()
        
        self.cam.BeginAcquisition()

    def __del__(self):
        self.cam.EndAcquisition()
        self.cam.DeInit()
        del self.cam
        self.cam_list.Clear()
        self.system.ReleaseInstance()

    def read(self):
        image_pt = self.cam.GetNextImage()
        if image_pt.IsIncomplete():
            print('Image incomplete with image status %d ...' % image_pt.GetImageStatus())
            os._exit(0) 
        #image_converted = image_pt.Convert(PySpin.PixelFormat_BGR8, PySpin.NEAREST_NEIGHBOR_AVG)
        image= image_pt.GetNDArray()
        image_pt.Release()
        return image

if __name__ == '__main__':
    rospy.init_node('camera_node', anonymous=False)
    image_path_pub = rospy.Publisher('image_path', std_msgs.msg.String, queue_size=1)
    raw_image_pub = rospy.Publisher('image_raw', Image, queue_size=1)
    bridge = CvBridge()
    cam = Camera()
    image_id = 0
    os.system('rm /dev/shm/*.opy')
    storing_path = 'shm://'
    x = []
    image = cam.read()
    image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2BGR)
    for i in range(20):
        x.append(sa.create("shm://%d.opy"%i,image.shape,dtype = 'uint8'))
    while not rospy.is_shutdown():
        t0 = time.time() * 1000
        raw = cam.read()
        t1 = time.time() * 1000
        image = cv2.cvtColor(raw, cv2.COLOR_BAYER_BG2BGR)
        image_id = (image_id + 1) % 20 
        image_path = storing_path + '%d.opy'%(image_id)
        x[image_id][:] = image
        image_path_pub.publish(image_path)
        t2 = time.time() * 1000
        raw_ros_image = bridge.cv2_to_imgmsg(raw, "bayer_rggb8")
        raw_image_pub.publish(raw_ros_image)
        t3 = time.time() * 1000

#        image_to_show = cv2.resize(image,(240,160))
#        cv2.circle(image_to_show, (120,60), 5,(0,0,255), 1)
#        cv2.imshow('a',image_to_show)
#        key = cv2.waitKey(1)
#        t2 = time.time() * 1000
#        print("%6.2f %6.2f"%(t1-t0,t2-t0))
#       if key == ord('q'):
#            break
        print("cap %5.2f   memory %5.2f   ros_pub %5.2f   sum %5.2f"%(t1-t0,t2-t1,t3-t2,t3-t0))
        if rospy.is_shutdown():
            del cam
            break
            
