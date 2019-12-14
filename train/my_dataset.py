import cv2
import time
import numpy as np
import glob
import os
import random
import torch
from torch.utils.data import Dataset
from torch.utils import data


image_list = glob.glob("../store/*/*.bmp")
image_list.sort()
image_shape = cv2.imread(image_list[0], 0).shape
points_list = []
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

def get_image(I):
    x,y,w,h,image_path = points_list[I]
    loop = 0
    a = y + h
    b = x + w  
    while(1):
        i = random.randint(0,image_shape[0] - s - 1)
        j = random.randint(0,image_shape[1] - s - 1)
        if i <= y and j <= x and i + s> a and j + s> b:
            image = cv2.imread(image_path,0)
            image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2GRAY) 
            image = image[i:i+s,j:j+s,].copy()
            return image, (x-j, y-i, w, h), 1
        else:
            if i + s< y or i > a or j + s< x or j > b:
                image = cv2.imread(image_path,0)
                image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2GRAY) 
                image = image[i:i+s,j:j+s,].copy()
                return image, (0,0,0,0), 0
            else:
                loop += 1
                if loop > 30:
                    I = (I + 1) %  len(points_list)
                    x,y,w,h,image_path = points_list[I]
                    loop = 0
                    a = y + h
                    b = x + w  
                continue
    
class MyDataset(Dataset):
    def __init__(self, train_test):
        self.train_test = train_test

    def __len__(self):
        if self.train_test ==  'train':
            return len(points_list)* 2 // 3
        else:
            return len(points_list)// 3 - 1

    def __getitem__(self,index):
        if self.train_test == 'test':
            index += len(points_list) * 2 // 3
        image, (x,y,w,h),state =  get_image(index)
        inputs = torch.tensor(image,dtype = torch.float) / 255
        inputs = inputs.unsqueeze(0)
        ground_truth = torch.tensor([state, float(x + w / 2)/s, float(y + h / 2)/s ,float(w)/s, float(h)/s])

        return inputs, ground_truth

#if __name__ == '__main__':
#    aa = 0
#    print(len(points_list))
#    for i in range(1000000):
#        image, (x, y, w, h), state= get_image(i % len(points_list))
#        cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
#        cv2.imshow('%d'%state, image)
#        key = cv2.waitKey(1)
#        aa += state
#        print(aa,i,aa/(i+1.0))
#        if key == ord('q'):
#            break

if __name__ == '__main__':
    train_set = MyDataset('train')
    test_set = MyDataset('test')
    train_loader = data.DataLoader(train_set, 100, shuffle = True, num_workers = 4, drop_last =  True)
    test_loader = data.DataLoader(test_set, 100, shuffle = True, num_workers = 4, drop_last =  True)
    for i, (inputs,ground_truth)  in enumerate(train_loader):
        print(i,inputs.shape, ground_truth.shape)
