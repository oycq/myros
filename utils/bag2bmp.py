import rospy
import numpy as np
import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import rosbag
import sys
import time
import os
import glob

bridge = CvBridge()
for bag_name in glob.glob("../store/*.bag"):

    folder_name = bag_name[:-4]
    if os.path.exists(folder_name):
        continue
    else:
        print(folder_name)
        os.mkdir(folder_name)
    bag = rosbag.Bag(bag_name)
    t0 = bag.get_start_time()
    tn = bag.get_end_time()
    count = 0
    for topic, msg, t in bag.read_messages(topics=['/image_raw']):
        time0 = time.time() * 1000
        count += 1
        image = bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        #image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2BGR)
        if count %  10 == 0:
            image_id = str(100000 + count // 10)[1:]
            cv2.imwrite('%s/%s.bmp'%(folder_name,image_id),image)
            print('%.2f%% %d'%(100*(t.to_sec()-t0)/(tn-t0),count/10))

