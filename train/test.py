import torch
import numpy as np
import os
import my_model as my_model
import torch.nn as nn
import my_dataset
import torch.optim as optim
import datetime
import cv2
import random
import time
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import rosbag
import rospy


BATCH_SIZE = 10
CUDA = 1
FP16 = 0
LOAD = 1
cv2.namedWindow("a", cv2.WINDOW_NORMAL);
cv2.moveWindow("a", 0,0);
cv2.setWindowProperty("a", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);
#cv2.namedWindow("b", cv2.WINDOW_NORMAL);
#cv2.moveWindow("b", 1920,0);
#cv2.setWindowProperty("b", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);


model = my_model.Model()
bridge = CvBridge()
bag = rosbag.Bag('../store/_2019-12-03-17-19-24.bag')

if CUDA:
    model = model.cuda()
    if FP16:
        model = model.half()

if LOAD:
    model.load_state_dict(torch.load('../store/history/2019-12-18-09-28-07/600:0.model'))
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
        if confi > 0.95:
            x,y,w,h = outputs[0,0].item(),outputs[0,1].item(),outputs[0,2].item(),outputs[0,3].item()
            x,y,w,h = int(x*2048 - w*1024 + 1024),int(y*1536 - h*768 + 768),int(w*2048),int(h*1546)
            cv2.rectangle(image,(x,y),(x+w,y+h),(0,0,255),2)
    cv2.imshow('a',image)

count = 0
for topic, msg, t in bag.read_messages(topics=['/image_raw']):
    count += 1
    if count % 4 != 0:
        continue
    key = cv2.waitKey(10)
    if key == ord('q'):
        break
    if key == ord(' '):
        continue_flag = 1
        continue
    image = bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
    image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2GRAY) 
    analysis(image)


