#!/usr/bin/env python
import torch
import numpy as np
import os
import sys
base_path = "/home/oycq/catkin_ws/src/myros/"
sys.path.insert(1, base_path + 'train')
import my_model as my_model
from torch import nn
from std_msgs.msg import String,Int16MultiArray
import datetime
import cv2
import random
import time
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import rospy
import SharedArray as sa


BATCH_SIZE = 10
CUDA = 1
FP16 = 0
LOAD = 1
#cv2.namedWindow("a", cv2.WINDOW_NORMAL);
#cv2.moveWindow("a", 0,0);
#cv2.setWindowProperty("a", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);
image_path = ''
x = {}
#cv2.namedWindow("b", cv2.WINDOW_NORMAL);
#cv2.moveWindow("b", 1920,0);
#cv2.setWindowProperty("b", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);


model = my_model.Model()
bridge = CvBridge()

def image_path_callback(a):
    global image_path,x
    image_path = a.data
    if a.data not in x:
        x[a.data] = sa.attach(a.data)

if CUDA:
    model = model.cuda()
    if FP16:
        model = model.half()

if LOAD:
    model.load_state_dict(torch.load(base_path + 'store/history/2019-12-18-09-28-07/600:0.model'))
model.train()
m = nn.Sigmoid()


def analysis(image):
    with torch.no_grad():
        model.eval()
        inputs = torch.tensor(image,dtype = torch.float32).cuda()
        if CUDA:
            inputs = inputs.cuda()
            if FP16:
                inputs = inputs.half() 
        inputs = inputs / 255
        inputs = inputs.unsqueeze(0).unsqueeze(0)
        confi, outputs , _= model(inputs)
        a = Int16MultiArray()
        a.data = (0, 0, 0, 0, 0,
                  image.shape[1], image.shape[0])
        if confi > 0.99:
            x,y,w,h = outputs[0,0].item(),outputs[0,1].item(),outputs[0,2].item(),outputs[0,3].item()
            x,y,w,h = int(x*2048 - w*1024 + 1024),int(y*1536 - h*768 + 768),int(w*2048),int(h*1546)
            #cv2.rectangle(image,(x,y),(x+w,y+h),(0,0,255),2)
            a.data = (1, x, y, x+w, y+h, image.shape[1], image.shape[0])
        tracking_info_pub.publish(a)
#    cv2.imshow('a',image)

if __name__ == '__main__':
    rospy.init_node('cnn_node', anonymous = False)
    rospy.Subscriber("/camera0/image_path", String, image_path_callback)
    tracking_info_pub = rospy.Publisher('detect_info', Int16MultiArray, queue_size = 1)
    while not rospy.is_shutdown():
        if image_path == '':
            time.sleep(0.1)
            continue
        image = x[image_path].copy()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
        analysis(image)

#        key = cv2.waitKey(1)
#        if key == ord('q'):
#            break
#
