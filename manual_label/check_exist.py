import cv2
import glob
import os

image_list = glob.glob("../store/*/*.bmp")
image_list.sort()
i = 0

def draw_text(image, txt, color):
    font = cv2.FONT_HERSHEY_SIMPLEX 
    org = (20, 30) 
    fontScale = 0.7
    thickness = 2
    image = cv2.putText(image, txt, org, font,  
                   fontScale, color, thickness, cv2.LINE_AA) 
    return image 

while(True):
    image = cv2.imread(image_list[i], 0)
    image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2BGR)
    image = cv2.resize(image, (1024, 768))
    flag_path = image_list[i][:-3] + 'no'
    if os.path.exists(flag_path):
        image = draw_text(image, 'No', (0,0,255))
    else:
        image = draw_text(image, 'Yes', (255,0,0))
    cv2.imshow('a',image)
    key = cv2.waitKey(0)
    if key == ord('q'):
        break
    if key == ord('1'):
        i -= 1
    if key == ord('3'):
        i += 1
    if key == ord('4'):
        i -= 10
    if key == ord('6'):
        i += 10
    if key == ord('7'):
        i -= 100
    if key == ord('9'):
        i += 100
    if key == ord('y') and os.path.exists(flag_path):
        os.system('rm %s'%flag_path)
        i = i + 1
    if key == ord('n') and not os.path.exists(flag_path):
        os.system('touch %s'%flag_path)
        i = i + 1
    if i < 0:
        i = 0
    if i >= len(image_list):
        i = image_list - 1

        



