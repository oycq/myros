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

def get_data(I):
    x,y,w,h,image_path = points_list[I]
    g1 = np.array([float(x)/2048  + w/4096.0 - 0.5 , float(y)/1536 + h/3072.0 - 0.5, float(w)/2048, float(h)/1536])
    gr = (1536 - s) // 32 + 1
    gc = (2048- s) // 32 + 1
    g = np.zeros((gr, gc, 5), dtype = np.float)
    image = cv2.imread(image_path,0)
    image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2GRAY) 
    for ii in range(gr):
        for jj in range(gc):
            i = float(ii * 32)
            j = float(jj * 32)
            if i <= y and j <= x and i + s> y + h and j + s> x + w:
                g[ii,jj] = np.array((1, (x-j+w/2)/s - 0.5, (y-i+h/2)/s - 0.5,float(w)/s,float(h)/s))
            else:
                if i + s< y or i > y + h or j + s< x or j > x + w:
                    g[ii,jj] = np.array((0,0,0,0,0))
                else:
                    g[ii,jj] = np.array((-1,0,0,0,0))
    return image, g , g1 
    
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
        image, g, g1 =  get_data(index)
        inputs = torch.tensor(image,dtype = torch.float32) / 255
        inputs = inputs.unsqueeze(0)
        ground_truth = torch.tensor(g,dtype = torch.float32)
        ground_truth1 = torch.tensor(g1,dtype = torch.float32)
        return inputs, ground_truth, ground_truth1 

if __name__ == '__main__':
    aa = 0
    print(len(points_list))
    for i in range(1000000):
        ii = random.randrange(0,20)
        jj = random.randrange(1,36)
        image, g = get_data(i % len(points_list))
        g = g * s
        x,y,w,h = g[ii,jj][1],g[ii,jj][2],g[ii,jj][3],g[ii,jj][4]
        x = int(x - w / 2)
        y = int(y - h / 2)
        w , h = int(w), int(h)
        image = image[ii * 32:ii *32 + s, jj *32:jj *32 + s]
        cv2.rectangle(image, (x,y),(x+w,y+h),(0,255,0),2)
        cv2.imshow('a', image)
        key = cv2.waitKey(0)
        if key == ord('q'):
            break

#if __name__ == '__main__':
#    train_set = MyDataset('train')
#    test_set = MyDataset('test')
#    train_loader = data.DataLoader(train_set, 100, shuffle = True, num_workers = 4, drop_last =  True)
#    test_loader = data.DataLoader(test_set, 100, shuffle = True, num_workers = 4, drop_last =  True)
#    for i, (inputs,ground_truth)  in enumerate(train_loader):
#        print(i,inputs.shape, ground_truth.shape)
