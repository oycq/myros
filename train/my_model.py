import torch
import os
import torch.nn as nn
import cv2
#cfg = [8,'M',8, 8, 'M', 16, 16,'M',32,32,'M',64,64, 'M', 128,128,'v']
cfg = [4,'M',4, 4, 'M', 8, 8,'M',16,16,'M',32,32, 'M', 64,64,'v']
cfg2 = [1]

class Model(nn.Module):

    def __init__(self):
        super(Model, self).__init__()
        self.features = self._make_layers(cfg, batch_norm=True, in_channels = 1)
        self.supper= nn.Sequential(
            nn.Linear(37*21*5, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace = True),
            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace = True),
            nn.Linear(512, 4),
        )
        self._initialize_weights()

    def forward(self, inputs):
        x = self.features(inputs)
        x = x.permute(0,2,3,1)
        confi = torch.max(x[:,:,:,0])
        confi = torch.sigmoid(confi)
        y = x.flatten(1)
        y = self.supper(y)
        return confi, y, x


    def _make_layers(self,cfg,batch_norm,in_channels = 1):
        layers = []
        fcn_deep = 128 
        for v in cfg:
            if v == 'v':
                conv2d = nn.Conv2d(64, fcn_deep // 4, kernel_size=28, padding=0, bias=False)
                layers += [conv2d, nn.BatchNorm2d(fcn_deep // 4), nn.ReLU(inplace=True)]
                conv2d = nn.Conv2d(fcn_deep // 4, fcn_deep, kernel_size=1, padding=0, bias=False)
                layers += [conv2d, nn.BatchNorm2d(fcn_deep), nn.ReLU(inplace=True)]
                conv2d = nn.Conv2d(fcn_deep, fcn_deep, kernel_size=1, padding=0, bias=False)
                layers += [conv2d, nn.BatchNorm2d(fcn_deep), nn.ReLU(inplace=True)]
                conv2d = nn.Conv2d(fcn_deep, fcn_deep, kernel_size=1, padding=0, bias=False)
                layers += [conv2d, nn.BatchNorm2d(fcn_deep), nn.ReLU(inplace=True)]
                conv2d = nn.Conv2d(fcn_deep, 5, kernel_size=1, padding=0, bias=False)
                layers += [conv2d]
                continue
            if v == 'M':
                layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
            else:
                conv2d = nn.Conv2d(in_channels, v, kernel_size=3, padding=1, bias=False)
                if batch_norm:
                    layers += [conv2d, nn.BatchNorm2d(v), nn.ReLU(inplace=True)]
                else:
                    layers += [conv2d, nn.ReLU(inplace=True)]
                in_channels = v
        return nn.Sequential(*layers)

    def _initialize_weights(self):
        for i,m in enumerate(self.modules()):
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                if m.weight is not None:
                   nn.init.constant_(m.weight, 1)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
