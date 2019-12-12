import cv2
import time
import numpy as np
import glob
import os
from  matplotlib import pyplot as plt
import rospy 

from sensor_msgs.msg import Joy

image_list = glob.glob("../store/*/*.bmp")
image_list.sort()
add_i = 1
continue_flag = 1
i = 0
mouse_x, mouse_y = (500,500)
width, height = (100,100)

cv2.namedWindow("color", cv2.WINDOW_NORMAL);
cv2.moveWindow("color", 2000,0);
cv2.setWindowProperty("color", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);
cv2.namedWindow("roi", cv2.WINDOW_NORMAL);
cv2.moveWindow("roi", 0,0);
cv2.setWindowProperty("roi", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);

def joy_callback(a):
    global width, height
    width = int(a.axes[2] * 400)
    height = int(a.axes[3] * 400)
    if width < 5:
        width = 5
    if height < 5:
        height = 5



def mouse_callback(event,x,y,flags,param):
    global mouse_x, mouse_y, pt1, pt2, i
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x = x
        mouse_y = y
    if event == cv2.EVENT_LBUTTONDOWN:
        print(i)
        i = i + 1
        f = open(pos_path,'w')
        data = (x - width // 2, y - height // 2, width, height)
        f.write('%d %d %d %d'%data)
        f.close()


def caculate_box_points(x,y,width,height,img_shape): 
    w = width // 2
    h = height // 2
    a1,a2 = max(0, x - w), max(y - h, 0)
    b1,b2 = min(img_shape[1], x + w), min(img_shape[0], y + h)
    pt1 = (a1,a2)
    pt2 = (b1,b2)
    return pt1,pt2,(a1,a2,width, height)


rospy.init_node('manual_label')
rospy.Subscriber("joy", Joy, joy_callback)
cv2.setMouseCallback('color',mouse_callback)

while(1):
    if i < 0:
        add_i = 1
        i = 0
    if i >= len(image_list):
        add_i = 0
        i = len(image_list) - 1 
        break

    continue_flag = 0
    flag_path = image_list[i][:-3] + 'no'
    pos_path = image_list[i][:-3] + 'pos'
    if os.path.exists(flag_path):
        continue_flag = 1
    if os.path.exists(pos_path):
        f = open(pos_path)
        pos_txt = f.readlines()[0]
        if 'unsure' not in pos_txt:
            continue_flag = 1

    if continue_flag:
        if add_i == 1:
            i = i + 1
        else:
            i = i - 1
        continue
    raw_image = cv2.imread(image_list[i], 0)
    color_image = cv2.cvtColor(raw_image, cv2.COLOR_BAYER_BG2BGR)
    pt1,pt2,(x,y,w,h) = caculate_box_points(mouse_x, mouse_y, width, height, raw_image.shape)
    cv2.rectangle(color_image,pt1,pt2,(255,0,0),3)
    roi = color_image[y:y+h,x:x+w,].copy()
    cv2.imshow('color',color_image)
    cv2.imshow('roi',roi)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    if key == ord('1'):
        i = i - 1
        print(i)
        add_i = 0
    if key == ord('3'):
        i = i + 1
        print(i)
        add_i = 1
    if key == ord('4'):
        i = i - 10
        add_i = 0
    if key == ord('6'):
        i = i + 10
        add_i = 1

