#!/user/bin/env python

#imports
from __future__ import print_function, division

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import numpy as np
import torchvision
from torchvision import datasets, models, transforms, utils
import time
import os
import copy
#import pandas as pd
from skimage import io, transform
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F
from PIL import Image

#ignore warnings
import warnings
warnings.filterwarnings("ignore")

PATH=("./nn_model/faces_ft.pt")

#process image
def process_image(image_path):
	#load Image
	img = Image.open(image_path)
	
	#get the dimensions of the image
	width, height = img.size
	
	#resize by keeping the aspect ratio, but changing the dimension
	#so the shortest size is 255px
	img = img.resize((255, int(255*(height/width))) if width < height else (int(255*(width/height)), 255))
	
	#get the dimensions of the new image size
	width, height = img.size
	
	#set the coordinates to do a center crop of 224 x 224
	left = (width - 224)/2
	top = (height - 224)/2
	right = (width + 224)/2
	bottom = (height + 224)/2
	img = img.crop((left, top, right, bottom))
	
	#turn image into numpy array
	img = np.array(img)
	
	#make the color channel dimension first instead of last
	img = img.transpose((2, 0, 1))
	
	#make all values between 0 and 1
	img = img/255
	
	#normalize based on the preset mean and standard deviation
	img[0] = (img[0] - 0.485)/0.229
	img[1] = (img[1] - 0.456)/0.224
	img[2] = (img[2] - 0.406)/0.225
	
	#add a fourth dimension to the beginning to indicate batch size
	img = img[np.newaxis,:]
	
	#turn into a torch tensor
	image = torch.from_numpy(img)
	image = image.float()
	return image
									   
def loadAndSetup():
	#data augmentation and normalization for training
	#just normalization for validation
	data_transforms = {
		'train': transforms.Compose([
			transforms.RandomResizedCrop(224),
			transforms.RandomHorizontalFlip(),
			transforms.ToTensor(),
			transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
		]),
		'val': transforms.Compose([
			transforms.Resize(256),
			transforms.CenterCrop(224),
			transforms.ToTensor(),
			transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
		]),
	}

	#dataloaders
	data_dir = 'images/'
	image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x),
											  data_transforms[x])
					  for x in ['train', 'val']}
	dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
	class_names = image_datasets['train'].classes
	
	device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

	model_trained = torch.load(PATH)
	print("Model loaded")
	
	return class_names, device, model_trained

def infer_face(class_names, device, model_trained):
	
	was_training = model_trained.training
	model_trained.eval()

	with torch.no_grad():	
		inputs = process_image("image_cam.jpg")
		inputs = inputs.to(device)

		outputs = model_trained(inputs)

		#print(class_names)

		#use softmax to get confidences
		m = nn.Softmax()
		
		#print(m(outputs).cpu())
 
		confidence_list = (m(outputs).cpu())
		
		for x in confidence_list:
			confidence_list_unpacked = x
			
		_, preds = torch.max(outputs, 1)
		
		for j in range(inputs.size()[0]):
			#strip out non-relevant information
			top = str(confidence_list_unpacked[class_names.index(class_names[preds[j]])])
			top = top.replace("tensor", "")
			top = top.replace("(", "")
			top = top.replace(")", "")
			#return prediction and confidence
			return(format(class_names[preds[j]])), (float(top))

	model_trained.train(mode=was_training)
	
#if called direct then run the function
if __name__ == '__main__':
	class_names, device, model_trained = loadAndSetup()
	print(infer_face(class_names, device, model_trained))