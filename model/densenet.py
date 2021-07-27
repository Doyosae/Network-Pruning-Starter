import math
import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
from torchsummary import summary



class Bottleneck(nn.Module):
    def __init__(self, in_planes, growth_rate):
        super(Bottleneck, self).__init__()
        self.bn1   = nn.BatchNorm2d(in_planes)
        self.conv1 = nn.Conv2d(in_planes, 4 * growth_rate, kernel_size = 1, bias = False)
        self.bn2   = nn.BatchNorm2d(4 * growth_rate)
        self.conv2 = nn.Conv2d(4 * growth_rate, growth_rate, kernel_size = 3, padding = 1, bias = False)

    def forward(self, x):
        out = self.bn1(x)
        out = F.relu(out)
        out = self.conv1(out)
        out = self.bn2(out)
        out = F.relu(out)
        out = self.conv2(out)
        out = torch.cat([out,x], 1)

        return out



class Transition(nn.Module):
    def __init__(self, in_planes, out_planes):
        super(Transition, self).__init__()
        self.bn   = nn.BatchNorm2d(in_planes)
        self.conv = nn.Conv2d(in_planes, out_planes, kernel_size=1, bias=False)

    def forward(self, x):
        out = self.bn(x)
        out = F.relu(out)
        out = self.conv(out)
        out = F.avg_pool2d(out, 2)

        return out



class DenseNet(nn.Module):
    def __init__(self, block, nblocks, growth_rate=12, reduction=0.5, num_classes=10):
        super(DenseNet, self).__init__()
        self.growth_rate = growth_rate

        num_planes = 2*growth_rate
        self.conv1 = nn.Conv2d(3, num_planes, kernel_size=3, padding=1, bias=False)

        self.dense1 = self.make_layers(block, num_planes, nblocks[0])
        num_planes  = num_planes + nblocks[0]*growth_rate
        out_planes  = int(math.floor(num_planes*reduction))
        self.trans1 = Transition(num_planes, out_planes)
        num_planes  = out_planes

        self.dense2 = self.make_layers(block, num_planes, nblocks[1])
        num_planes  = num_planes + nblocks[1]*growth_rate
        out_planes  = int(math.floor(num_planes*reduction))
        self.trans2 = Transition(num_planes, out_planes)
        num_planes  = out_planes

        self.dense3 = self.make_layers(block, num_planes, nblocks[2])
        num_planes  = num_planes + nblocks[2]*growth_rate
        out_planes  = int(math.floor(num_planes*reduction))
        self.trans3 = Transition(num_planes, out_planes)
        num_planes  = out_planes

        self.dense4 = self.make_layers(block, num_planes, nblocks[3])
        num_planes  = num_planes + nblocks[3]*growth_rate

        self.bn     = nn.BatchNorm2d(num_planes)
        self.linear = nn.Linear(num_planes, num_classes)

    def make_layers(self, block, in_planes, nblock):
        layers = []
        for i in range(nblock):
            layers.append(block(in_planes, self.growth_rate))
            in_planes += self.growth_rate
        return nn.Sequential(*layers)

    def forward(self, x):
        out = self.conv1(x)
        out = self.trans1(self.dense1(out))
        out = self.trans2(self.dense2(out))
        out = self.trans3(self.dense3(out))
        out = self.dense4(out)
        out = F.avg_pool2d(F.relu(self.bn(out)), 4)
        out = out.view(out.size(0), -1)
        out = self.linear(out)
        return out



def DenseNet121(growth_rate = 32):
    return DenseNet(Bottleneck, [6, 12, 24, 16], growth_rate = growth_rate)


def DenseNet169(growth_rate = 32):
    return DenseNet(Bottleneck, [6, 12, 32, 32], growth_rate = growth_rate)


def DenseNet201(growth_rate = 32):
    return DenseNet(Bottleneck, [6, 12, 48, 32], growth_rate = growth_rate)


def DenseNet161(growth_rate = 32):
    return DenseNet(Bottleneck, [6, 12, 36, 24], growth_rate = growth_rate)