import rospy
import numpy as np
import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import CompressedImage
from sensor_msgs.msg import Image
import rosbag
import sys
import time
import os
import glob

UI_DISPLAY = 0
BAG_NAME = "../store/_2019-12-28-16-58-17.bag"
TOPIC_NAME = "/ui/display_image/compressed"
OUTPUT_NAME = '/home/oycq/video.avi'
COMPRESSED = 1
FPS = 60
SHAPE = (1024,768)
fourcc = cv2.VideoWriter_fourcc(*"MPEG")
writer = cv2.VideoWriter(OUTPUT_NAME, fourcc, FPS, (1024,768))

bridge = CvBridge()
bag = rosbag.Bag(BAG_NAME)
t0 = bag.get_start_time()
tn = bag.get_end_time()
count = 0
for topic, msg, t in bag.read_messages(topics=[TOPIC_NAME]):
    time0 = time.time() * 1000
    count += 1
    if COMPRESSED == 0:
        image = bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2BGR)
    else:
        image = bridge.compressed_imgmsg_to_cv2(msg)
    if UI_DISPLAY:
        cv2.imshow('a',image)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
    writer.write(image)
    if count %  10 == 0:
        image_id = str(100000 + count // 10)[1:]
        print('%.2f%% %d'%(100*(t.to_sec()-t0)/(tn-t0),count/10))

