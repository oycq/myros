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
i = 0
threshold = 128
mouse_x, mouse_y,width = (500,500,100)
csrt = cv2.TrackerCSRT_create()
csrt_state = False
if_update_csrt = False
draw_previous = 0
have_record =  0
threshold_bias = 0
add_i =  True
unsure_flag = 0


def draw_text(image, txt, color):
    font = cv2.FONT_HERSHEY_SIMPLEX 
    org = (20, 30) 
    fontScale = 0.7
    thickness = 2
    image = cv2.putText(image, txt, org, font,  
                   fontScale, color, thickness, cv2.LINE_AA) 
    return image 

def mouse_callback(event,x,y,flags,param):
    global mouse_x, mouse_y, pt1, pt2
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x = x
        mouse_y = y

def caculate_box_points(x,y,width,img_shape): 
    d = width // 2
    if csrt_state == True:
        x = int(csrt_box[0] + csrt_box[2] / 2)
        y = int(csrt_box[1] + csrt_box[3] / 2)
    a1,a2 = max(0, x - d), max(y - d, 0)
    b1,b2 = min(img_shape[1], x + d), min(img_shape[0], y+d)
    pt1 = (a1,a2)
    pt2 = (b1,b2)
    return pt1,pt2

def get_hist_graph(roi):
    global threshold
    hist = cv2.calcHist([roi],[0],None,[256],[0,256])
    for j in range(256):
        if j < 60:
            continue
        if hist[j][0] > 1000:
            threshold = j + threshold_bias
            break
    lines = plt.plot(hist,color='r')
    fig.canvas.draw()
    lines[0].remove() 
    hist_img = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8,
            sep='')
    hist_img = hist_img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    hist_img = cv2.cvtColor(hist_img,cv2.COLOR_RGB2BGR)
    line_pos = int(threshold / 256.0 * 496 + 81)
    cv2.line(hist_img, (line_pos, 61), (line_pos, 428), (255, 0, 0), 2)
    return hist_img

def update_csrt(color_image):
    global csrt_state,if_update_csrt,csrt_box,draw_previous
    if csrt_state == True:
        if if_update_csrt:
            csrt_state, csrt_box = csrt.update(color_image)
            if_update_csrt = 0
        mash = (int(csrt_box[0]),int(csrt_box[1]))
        bar = (int(csrt_box[0]+csrt_box[2]),int(csrt_box[1]+csrt_box[3]))
        if draw_previous == 0:
            cv2.rectangle(color_image,mash,bar,(0,255,0),2)
    else:
        draw_previous = 1
    if unsure_flag == 1:
        font = cv2.FONT_HERSHEY_SIMPLEX 
        org = (20, 30) 
        fontScale = 0.7
        color = (0, 0, 255) 
        thickness = 2
        cv2.putText(color_image, 'unsure', org, font,  
                   fontScale, color, thickness, cv2.LINE_AA) 
    return color_image


def joy_callback(a):
    global width,threshold_bias
    width = int(a.axes[2] * 500 + 520)
    threshold_bias = a.axes[4] * 20
    #use_traking_data = a.buttons[3]

fig = plt.figure()
plt.title("Grayscale Histogram")
plt.xlabel("Bins")
plt.ylabel("# of Pixels")
plt.xlim([0,256])
plt.ylim([0,10000])

cv2.namedWindow("color", cv2.WINDOW_NORMAL);
cv2.moveWindow("color", 2000,0);
cv2.setWindowProperty("color", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);
cv2.namedWindow("roi", cv2.WINDOW_NORMAL);
cv2.moveWindow("roi", 0,0);
cv2.setWindowProperty("roi", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);
cv2.namedWindow("hist");
cv2.moveWindow("hist", 0,0);
cv2.namedWindow("thr");
cv2.moveWindow("thr", 0,600);
rospy.init_node('manual_label')
rospy.Subscriber("joy", Joy, joy_callback)
cv2.setMouseCallback('color',mouse_callback)


while(True):
    time0 = time.time() * 1000######################
    flag_path = image_list[i][:-3] + 'no'
    pos_path = image_list[i][:-3] + 'pos'
    if os.path.exists(flag_path):
        if add_i:
            i = i + 1
        else:
            i = i - 1
        continue
    if os.path.exists(pos_path):
        f = open(pos_path)
        pos_txt = f.readlines()[0]
        if 'unsure' not in pos_txt:
            unsure_flag = 0
            x1,y1,w1,h1 = pos_txt.split(' ')
            x1,y1,w1,h1 = int(x1), int(y1), int(w1), int(h1)
            #x1,y1 = x1 - pt1[0], y1 - pt1[1]
            have_record = 1
        else:
            unsure_flag = 1


    raw_image = cv2.imread(image_list[i], 0)
    color_image = cv2.cvtColor(raw_image, cv2.COLOR_BAYER_BG2BGR)
    raw_color_image = color_image.copy()
    grey_image = cv2.cvtColor(raw_image, cv2.COLOR_BAYER_BG2GRAY)
    color_image = update_csrt(color_image)
    if draw_previous == 1 and have_record:
        cv2.rectangle(color_image,(x1,y1),(x1+w1,y1+h1),(255,0,0),2)
    pt1,pt2 = caculate_box_points(mouse_x, mouse_y, width, grey_image.shape)
    roi = grey_image[pt1[1]:pt2[1],pt1[0]:pt2[0]].copy()
    cv2.rectangle(color_image,pt1,pt2,(255,0,0),3)

    hist_graph = get_hist_graph(roi)


    _,thr= cv2.threshold(roi,threshold,255,cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(thr, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if len(contours) is not 0:
        contour = max(contours, key = cv2.contourArea)
        x,y,w,h = cv2.boundingRect(contour)
    thr = cv2.resize(thr,(480,480))
    roi = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR) 
    if len(contours) is not 0:
        cv2.rectangle(roi,(x,y),(x+w,y+h),(0,255,0),1)


    cv2.imshow('color',color_image)
    cv2.imshow('hist', hist_graph)
    cv2.imshow('thr', thr)
    cv2.imshow('roi',roi)

    key = cv2.waitKey(1)
    
    if key == ord('q'):
        break
    if key == ord('1'):
        print(i)
        add_i = 0
        if_update_csrt = 1
        i -= 1
    if key == ord('3'):
        print(i)
        add_i = 1
        i += 1
        if_update_csrt = 1
    if key == ord('4'):
        add_i = 0
        i -= 10
    if key == ord('6'):
        add_i = 1
        i += 10
    if key == ord('7'):
        add_i = 0
        i -= 100
    if key == ord('9'):
        add_i = 1
        i += 100
    if key == ord('2'):
        add_i = 1
        if_update_csrt = 1
        draw_previous = 0
        f = open(pos_path,'w')
        f.write('%d %d %d %d'%(csrt_box[0],csrt_box[1],csrt_box[2],csrt_box[3]))
        f.close()
        i += 1
    if key == ord('/'):
        add_i = 1
        f = open(pos_path,'w')
        f.write('unsure')
        f.close()
        i += 1
    if key == ord('8'):
        add_i = 1
        f = open(pos_path,'w')
        f.write('%d %d %d %d'%(x+pt1[0],y+pt1[1],w,h))
        f.close()
        i += 1
    if key == ord('5'):
        add_i = 1
        if_update_csrt = 1
        f = open(pos_path,'w')
        draw_previous = 0
        i += 1
        csrt = cv2.TrackerCSRT_create()
        csrt_settings = cv2.FileStorage("csrt_settings.yaml",cv2.FILE_STORAGE_READ) 
        csrt.read(csrt_settings.root())
    #   csrt_settings = cv2.FileStorage("csrt_settings1.yaml",cv2.FILE_STORAGE_WRITE) 
    #   csrt.write(csrt_settings)
        csrt_box = (x+pt1[0],y+pt1[1],w,h)
        csrt.init(raw_color_image, csrt_box)
        csrt_state = True 
        f.write('%d %d %d %d'%(x+pt1[0],y+pt1[1],w,h))
        f.close()
    if key == ord('*'):
        add_i = 1
        draw_previous = (draw_previous + 1) % 2

    if key == ord('.'):
        add_i = 1
        csrt_state = False

    if i < 0:
        i = 0
    if i >= len(image_list):
        i = image_list - 1
    time3 = time.time() * 1000######################
    #print(time1 - time0, time3 - time2)

