import os
from PIL import Image
import numpy as np
import cv2
import torchvision.transforms as transforms
import torchvision.models as models
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

margin = 0.8
imsize = 160
embedding_dim = 512

def get_embedding(path):
    cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
    image = cv2.imread(path)
    img = None
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces_rect = cascade.detectMultiScale(gray_image, scaleFactor=1.2, minNeighbors=5)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    for (x, y, w, h) in faces_rect:
        img = image[y: y+h, x: x+w][:]

    img = Image.fromarray(img)
    transform = transforms.Compose([transforms.Resize((imsize, imsize)),
                                     transforms.ToTensor(), prewhiten])
    img = transform(img)

    model = get_model()
    checkpoint = torch.load('45.pt', map_location=torch.device('cpu'))
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    img = torch.unsqueeze(img,dim=0) 
    with torch.no_grad():   
        embedding = model(img)[0]

    return embedding.numpy()

def get_faces(path):
    cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
    image = cv2.imread(path)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces_rect = cascade.detectMultiScale(gray_image, scaleFactor=1.2, minNeighbors=5)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    detected_faces = []
    detected_faces_coord = []
    for (x, y, w, h) in faces_rect:
        img = image[y: y+h, x: x+w][:]
        img = Image.fromarray(img)
        detected_faces.append(img)
        detected_faces_coord.append((x,y,w,h))

    return detected_faces, detected_faces_coord

class SiameseNetwork(nn.Module):
    def __init__(self, resnet):
        super(SiameseNetwork, self).__init__()
        self.resnet = resnet

    def forward_once(self, x):
        output = self.resnet(x)
        # output = self.avg_pool(output)
        # assert output.shape[0]==x.shape[0],print ('dimension are mismatching')
        output_embed = output.view(output.size()[0], -1)
        # output_embed = self.dp1(output)
        # output_embed = self.linear1(output_embed)
        output_embed = F.relu(output_embed)
        assert (output_embed.shape[1] == embedding_dim)
        output_embed = F.normalize(output_embed, p=2, dim=1)
        return output_embed

    def forward(self, x):
        out = self.forward_once(x)
        return out

def prewhiten(x):
    mean = x.mean()
    std = x.std()
    std_adj = std.clamp(min=1.0/(float(x.numel())**0.5))
    y = (x - mean) / std_adj
    return y

def get_model():
    resnet18 = models.resnet34(pretrained=False)
    modules = list(resnet18.children())[:-1]
    resnet18 = nn.Sequential(*modules)
    siamese_network = SiameseNetwork(resnet18)
    return siamese_network

def get_scores(label_faces_emb,detected_faces, detected_faces_coord):

    label_faces_emb = torch.tensor(label_faces_emb)
    transform1 = transforms.Compose([transforms.Resize((imsize, imsize)),
                                    transforms.ToTensor(), prewhiten])
    transform2 = transforms.Compose([transforms.Resize((imsize, imsize)), transforms.RandomHorizontalFlip(p=1.0),
                                    transforms.ToTensor(), prewhiten])

    detected_faces_1 = [transform1(face) for face in detected_faces]
    detected_faces_2 = [transform2(face) for face in detected_faces]

    detected_faces_1,detected_faces_2 = torch.stack(detected_faces_1),torch.stack(detected_faces_2)

    model = get_model()
    checkpoint = torch.load('45.pt', map_location=torch.device('cpu'))
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    with torch.no_grad():
        detected_faces_1_emb, detected_faces_2_emb = model(detected_faces_1), model(detected_faces_2)

    nl = label_faces_emb.size(0)
    nd = detected_faces_1_emb.size(0)

    dist = []

    for i in range(nl):
        for j in range(nd):
            d1 = (label_faces_emb[i] - detected_faces_1_emb[j])**2
            d2 = (label_faces_emb[i] - detected_faces_2_emb[j])**2
            avgd = (d1.sum()+d2.sum())/2
            dist.append((avgd.item(),(i,j)))

    dist = sorted(dist, key=lambda x: x[1])
    print("----------------------------------------------------------->",dist)
    visitedl = [False]*nl
    visitedd = [False]*nd

    coord_map = {}
    
    for dst, (l, d) in dist:
        if dst<margin and not visitedl[l] and not visitedd[d]:
            visitedd[d] = True; visitedl[l] = True
            coord_map[l] = detected_faces_coord[d]


    is_present = []
    coord = []
    for i in range(nl):
        if visitedl[i]:
            is_present.append(i)
            coord.append(coord_map[i])

    return is_present, coord
