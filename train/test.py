import torch
import numpy as np
import os
import my_model as my_model
import torch.nn as nn
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
LOAD = 0
#cv2.namedWindow("b", cv2.WINDOW_NORMAL);
#cv2.moveWindow("b", 1920,0);
#cv2.setWindowProperty("b", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);


model = my_model.Model()
bridge = CvBridge()
bag = rosbag.Bag('../store/_2019-12-03-17-19-24.bag')
k = 896

if CUDA:
    model = model.cuda()
    if FP16:
        model = model.half()

if LOAD:
    model.load_state_dict(torch.load('/home/oycq/myros/store/history/2019-12-16-21-14-07/300:0.model'))
model.train()
m = nn.Sigmoid()


def analysis(image):
    with torch.no_grad():
        model.eval()
        inputs = torch.tensor(image,dtype = torch.float32)
        if CUDA:
            inputs = inputs.cuda()
            if FP16:
                inputs = inputs.half() 

        inputs = inputs / 255
        inputs = inputs.unsqueeze(0).unsqueeze(0)
        outputs = model(inputs)
        if outputs[0][0][0][0]  > 1:
            pass 
        max_conf = [0,0,0]
        time0 = time.time() * 1000
        for i in range(21):
            for j in range(37):
                output = outputs[0,i,j]
                if output[0] > max_conf[2]:
                    max_conf = [i,j, output[0]]
        time1 = time.time() * 1000
        if max_conf[2] > 1:
            i = max_conf[0]
            j = max_conf[1]
            output = outputs[0,i,j]
            img = image[i * 32: i *  32 + 896, j * 32: j * 32 + 896]
            x,y,w,h = output[1].item(),output[2].item(),output[3].item(),output[4].item()
            x,y,w,h = int(x*k - w*k/2 + k /2),int(y*k - h*k/2 + k/2),int(w*k),int(h*k)
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
        print(time1 - time0)
count = 0
for topic, msg, t in bag.read_messages(topics=['/image_raw']):
    count += 1
    if count % 4 != 0:
        continue
    image = bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
    image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2GRAY) 
    analysis(image)


