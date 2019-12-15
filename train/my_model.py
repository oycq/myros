import torch
import os
import torch.nn as nn
import cv2
cfg = [4,'M',8, 8, 'M', 16, 16,'M',32,32,'M',64,64, 'M', 64]
#  896    448       224         112       56  
cfg2 = [1]
haha = None 

class Model(nn.Module):

    def __init__(self):
        super(Model, self).__init__()
        self.features = self._make_layers(cfg, batch_norm=True, in_channels = 1)
        self.classifier = nn.Sequential(
            nn.Linear(64*28*28, 512),
            nn.ReLU(True),
            nn.Dropout(),
            nn.Linear(512, 512),
            nn.ReLU(True),
            nn.Dropout(),
            nn.Linear(512, 5),
            nn.Sigmoid()
        )
        self._initialize_weights()

    def forward(self, inputs):
        global haha
        x = self.features(inputs)
        haha = x.clone()
        x = torch.flatten(x,1)
        x = self.classifier(x)
        return x


    def _make_layers(self,cfg,batch_norm,in_channels = 1):
        layers = []
        for v in cfg:
            if v == 'v':
                conv2d = nn.Conv2d(in_channels, 1, kernel_size=3, padding=1, bias=False)
                layers += [conv2d, nn.BatchNorm2d(1), nn.Sigmoid()]
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
