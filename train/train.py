import torch
import numpy as np
import os
import my_model as my_model
import progressbar
import torch.nn as nn
import my_dataset
import torch.optim as optim
import datetime
import wandb
import cv2
import random
import time

K1 = 1 
K2 = 100
K3 = 100
K4 = 1
BATCH_SIZE = 15
CUDA = 1
WANDB = 1 
LOAD = 0
cv2.namedWindow("a", cv2.WINDOW_NORMAL);
cv2.moveWindow("a", 0,0);
cv2.setWindowProperty("a", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);
cv2.namedWindow("b", cv2.WINDOW_NORMAL);
cv2.moveWindow("b", 3840,0);
cv2.setWindowProperty("b", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);


if WANDB:
    wandb.init()
    history_directory = '../store/history/%s'%datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    os.mkdir(history_directory)
    #wandb.watch(model)

model = my_model.Model()
optimizer = optim.Adam(model.parameters())
if CUDA:
    model = model.cuda()

if LOAD:
    model.load_state_dict(torch.load('../store/history/2019-12-12-22-59-06/60:0.model'))
    optimizer.load_state_dict(torch.load('../store/history/2019-12-12-22-59-06/60:0.adam'))
model.train()


def test():
    with torch.no_grad():
#        bar.start()
        model.eval()
        correct_count = 0 
        sum_count = 0
        for j, (inputs, ground_truth) in enumerate(test_loader):
            if CUDA:
                inputs = inputs.cuda()
                ground_truth = ground_truth.cuda()
            outputs = model(inputs)
            correct_count += ((outputs[:,0] > 0.5) == (ground_truth[:,0] == 1)).sum().item()
            sum_count += BATCH_SIZE
#            bar.update(j)
#        bar.finish()
    return correct_count / sum_count * 100

train_set = my_dataset.MyDataset('train')
test_set = my_dataset.MyDataset('test')
train_loader = torch.utils.data.DataLoader(train_set, BATCH_SIZE,\
        shuffle = True, num_workers = 5, drop_last =  True) 
test_loader = torch.utils.data.DataLoader(test_set, BATCH_SIZE,\
        shuffle = True, num_workers = 5, drop_last =  True)
loss_f1 = nn.BCELoss()
loss_f2 = nn.MSELoss()
m = nn.Sigmoid()
mm = nn.ReLU()

for epoch in range(20000000):
    print('----- epoch %d -----'%epoch) 
    time0 = time.time()
#    test_result = test()
#    print(test_result)
    for i, (inputs, ground_truth, ground_truth1) in enumerate(train_loader):
        if CUDA:
            inputs = inputs.cuda()
            ground_truth = ground_truth.cuda()
            ground_truth1 = ground_truth1.cuda()
        _, outputs1, outputs = model(inputs)
        outputs = outputs.contiguous().view(-1,5)
        ground_truth = ground_truth.contiguous().view(-1 ,5)

        index = ground_truth[:,0] != -1
        loss1 = loss_f1(m(outputs[index,0]), ground_truth[index,0]) * K1
        index = ground_truth[:,0] == 1
        loss2 = loss_f2(outputs[index,1:3], ground_truth[index,1:3]) * K2
        loss3 = loss_f2(mm(outputs[index,3:])**0.5, (ground_truth[index,3:])**0.5) * K3
        loss4 = loss_f2(outputs1[:,0:2], ground_truth1[:,0:2]) * K2 * K4
        loss5 = loss_f2(mm(outputs1[:,2:])**0.5, (ground_truth1[:,2:])**0.5) * K3 * K4
        loss = loss1 + loss2 + loss3 + loss4 + loss5
        optimizer.zero_grad() 
        loss.backward()
        optimizer.step()
#        print("%10.5f%10.5f%10.5f"%(loss1, loss2, loss3))

        if WANDB:
            wandb.log({'loss1':loss1.item(),
                       'loss2':loss2.item(),
                       'loss3':loss3.item(),
                       'loss4':loss4.item(),
                       'loss5':loss5.item(),
                       'loss':loss.item(),
                       })

        if i % 4 == 0:
            ii = random.randrange(0,20)
            jj = random.randrange(0,36)
            p =  ii * 37 + jj
            image = inputs[0,0].cpu().numpy()[ii * 32: ii * 32 + 896, jj * 32:jj *32 + 896]
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            if outputs[p,0] > 0.5:
                x,y,w,h = outputs[p,1].item(),outputs[p,2].item(),outputs[p,3].item(),outputs[p,4].item()
                k = my_dataset.s
                x,y,w,h = int(x*k - w*k/2 + k /2),int(y*k - h*k/2 + k/2),int(w*k),int(h*k)
                cv2.rectangle(image,(x,y),(x+w,y+h),(0,0,255),2)
            k = my_dataset.s
            x,y,w,h = ground_truth[p,1].item(),ground_truth[p,2].item(),ground_truth[p,3].item(),ground_truth[p,4].item()
            x,y,w,h = int(x*k - w*k/2 + k/2),int(y*k - h*k/2 + k/2),int(w*k),int(h*k)
            cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.imshow('a',image)

            image = inputs[0,0].cpu().numpy()
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            x,y,w,h = ground_truth1[0,0].item(),ground_truth1[0,1].item(),ground_truth1[0,2].item(),ground_truth1[0,3].item()
            x,y,w,h = int(x*2048 - w*1024 + 1024),int(y*1536- h*768 + 768),int(w*2048),int(h*1536)
            cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
            x,y,w,h = outputs1[0,0].item(),outputs1[0,1].item(),outputs1[0,2].item(),outputs1[0,3].item()
            x,y,w,h = int(x*2048 - w*1024 + 1024),int(y*1536- h*768 + 768),int(w*2048),int(h*1536)
            cv2.rectangle(image,(x,y),(x+w,y+h),(0,0,255),2)
            cv2.imshow('b',image)
        key = cv2.waitKey(1)
                


            
    print(time.time() - time0)

    if epoch % 10 == 0 and WANDB:
        torch.save(optimizer.state_dict(),'%s/%d:%d.adam'%(history_directory,epoch,0))
        torch.save(model.state_dict(),'%s/%d:%d.model'%(history_directory,epoch,0))

