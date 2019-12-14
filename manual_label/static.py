jjport cv2
import time
import numpy as np
import glob
import os

image_list = glob.glob("../store/*/*.bmp")
image_list.sort()
image_shape = cv2.imread(image_list[0], 0).shape
background = cv2.imread(image_list[0], 0)
background = cv2.cvtColor(background, cv2.COLOR_BAYER_BG2BGR)
points_list = []
have_plane = 0
no_plane = 0
others = 0
s = 896

for i in range(len(image_list)):
    continue_flag = 0
    flag_path = image_list[i][:-3] + 'no'
    pos_path = image_list[i][:-3] + 'pos'
    if os.path.exists(flag_path):
        continue
    if os.path.exists(pos_path):
        f = open(pos_path)
        pos_txt = f.readlines()[0]
        if 'unsure' not in pos_txt:
            x,y,w,h = pos_txt.split(' ')
            x,y,w,h = int(x), int(y), int(w), int(h)
            points_list.append((x,y,w,h,image_list[i]))

cv2.namedWindow("background", cv2.WINDOW_NORMAL);
cv2.moveWindow("background", 2000,0);
cv2.setWindowProperty("background", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);

for point in points_list:
    x = point[0] + point[2] // 2
    y = point[1] + point[3] // 2
    cv2.circle(background, (x,y), 2, (0,0,255), 1)
cv2.imshow('background',background)
cv2.waitKey(0)

I = 0
key = 0
for (x,y,w,h,image_path) in points_list:
    a = y + h
    b = x + w  
    for i in range(image_shape[0] - s):
        for j in range(image_shape[1] - s):
            if i <= y and j <= x and i + s> a and j + s> b:
                have_plane += 1
#                if have_plane % 100000 == 0:
#                    image = cv2.imread(image_path,0)
#                    cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
#                    image = image[i:i+s,j:j+s]
#                    cv2.imshow('have_plane', image)
#                    key = cv2.waitKey(0)
            else:
                if i + s< y or i > a or j + s< x or j > b:
                    no_plane += 1
#                    if no_plane % 100000 == 0:
#                        image = cv2.imread(image_path,0)
#                        cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
#                        image = image[i:i+s,j:j+s]
#                        cv2.imshow('no_plane', image)
#                        key = cv2.waitKey(0)
                else:
                    others += 1
            if key == ord('q'):
                os._exit(0)
    print(have_plane, no_plane,others,no_plane * 1.0/ (have_plane + no_plane),I)
    I += 1
    
