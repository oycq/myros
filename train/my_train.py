import torch
import os
import my_model as my_model
#import progressbar
import torch.nn as nn
import my_dataset
import torch.optim as optim
import datetime
#import wandb

THRESH_HOLD = 0.7
K1 = 4
BATCH_SIZE = 10

#wandb.init()

model = my_model.Model().cuda()
#wandb.watch(model)
#model.load_state_dict(torch.load('../data/history/2019-07-10 16:51:25.453881/1:20000.model'))
model.train()
optimizer = optim.Adam(model.parameters())
#optimizer.load_state_dict(torch.load('../data/history/2019-07-10 16:51:25.453881/1:20000.adam'))

history_directory = '../store/history/%s'%datetime.datetime.now().strftime("%Y-%m-%d-%M-%M-%s")
os.mkdir(history_directory)

#def test(model):
#    with torch.no_grad():
#        bar.start()
#        model.eval()
#        correct_count = 0 
#        sum_count = 0
#        for j, (input_batch, label_batch) in enumerate(my_dataloader.test_loader):
#            input_batch = input_batch.cuda()
#            input_batch = input_batch.float()
#            input_batch = input_batch / 255
#            label_batch = label_batch.cuda().squeeze()
#            dense, outputs = model(input_batch)
##            loss = criterion(outputs, label_batch)
#            _, predicted = torch.max(outputs,1)
#            sum_count += batch_size
#            correct_count += (predicted == label_batch).sum().item()
#            bar.update(j)
#        bar.finish()
#        return correct_count / sum_count * 100

train_set = my_dataset.MyDataset('train')
test_set = my_dataset.MyDataset('test')
train_loader = torch.utils.data.DataLoader(train_set, BATCH_SIZE, \
        shuffle = True, num_workers = 4, drop_last =  True) 
test_loader = torch.utils.data.DataLoader(test_set, BATCH_SIZE, 
        shuffle = True, num_workers = 4, drop_last =  True)
loss_f = nn.MSELoss()

for epoch in range(200):
    print('----- epoch %d -----'%epoch) 
    for i, (inputs, ground_truth) in enumerate(my_dataloader.train_loader):
        inputs = inputs.cuda()
        inputs = inputs.float() / 255
        ground_truth = ground_truth.cuda()
        outputs = model(inputs)

        loss1 = loss_f(outputs[:,0], outputs[:,0]) * K1
        index = outputs[:,0] > THRESH_HOLD
        loss2 = loss_f(outputs[index,1:], ground_truth[index,1:])
        loss = loss1 + loss2
        optimizer.zero_grad() 
        loss.backward()
        optimizer.step()


#        wandb.log({'i':i,
#                   'train_loss':loss.item(),
#                   'train_loss_min':info[0].item(),
#                   'train_loss_max':info[1]})
#        if i % 500 == 0:
#            torch.save(optimizer.state_dict(),'%s/%d:%d.adam'%(history_directory,epoch,i))
#            torch.save(model.state_dict(),'%s/%d:%d.model'%(history_directory,epoch,i))

    print("%10.5f%10.5f%10.5f"%(loss1, loss2, loss))
