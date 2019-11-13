import torch
import torch.nn as nn
import torch.nn.functional as F
embedding_dim = 512
import torchvision.models as models
import numpy as np

import os
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import onnx
from onnx_tf.backend import prepare
import tensorflow as tf


model_onnx = onnx.load('model_simple.onnx')
tf_rep = prepare(model_onnx)
print ("done")
# Print out tensors and placeholders in model (helpful during inference in TensorFlow)
print(tf_rep.tensor_dict)

# Export model as .pb file
tf_rep.export_graph('model_simple.pb')

# class SiameseNetwork(nn.Module):
#     def __init__(self, resnet):
#         super(SiameseNetwork, self).__init__()
#         self.resnet = resnet
#
#     def forward_once(self, x):
#         output = self.resnet(x)
#         # output = self.avg_pool(output)
#         # assert output.shape[0]==x.shape[0],print ('dimension are mismatching')
#         output_embed = output.view(output.size()[0], -1)
#         # output_embed = self.dp1(output)
#         # output_embed = self.linear1(output_embed)
#         output_embed = F.relu(output_embed)
#         assert (output_embed.shape[1] == embedding_dim)
#         output_embed = F.normalize(output_embed, p=2, dim=1)
#         return output_embed
#
#     def forward(self, x):
#         out = self.forward_once(x)
#         return out
#
# def prewhiten(x):
#     mean = x.mean()
#     std = x.std()
#     std_adj = std.clamp(min=1.0/(float(x.numel())**0.5))
#     y = (x - mean) / std_adj
#     return y
#
# def get_model():
#     resnet18 = models.resnet34(pretrained=False)
#     modules = list(resnet18.children())[:-1]
#     resnet18 = nn.Sequential(*modules)
#     siamese_network = SiameseNetwork(resnet18)
#     return siamese_network
#
#
# model_pytorch = get_model()
# checkpoint = torch.load('45.pt', map_location=torch.device('cpu'))
# model_pytorch.load_state_dict(checkpoint['model_state_dict'])
# model_pytorch.eval()
# # Single pass of dummy variable required
# dummy_input = torch.zeros((1,3,160,160))
# dummy_output = model_pytorch(dummy_input)
# print(dummy_output)
#
# # Export to ONNX format
# torch.onnx.export(model_pytorch, dummy_input, 'model_simple.onnx', input_names=['input'], output_names=['output'])