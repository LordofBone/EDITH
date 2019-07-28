#thanks to https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html

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
import os.path
import copy
import pandas as pd
from skimage import io, transform
from torch.utils.data import Dataset, DataLoader

#ignore warnings
import warnings
warnings.filterwarnings("ignore")

#path to the inference model
PATH = "./nn_model/faces_ft.pt"

#number of epochs for passing images through the model in training
no_epochs = 10

#number of faces to train off of
number_of_faces = len(os.listdir('./images/train'))

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

#the data loaders for getting images into the program for training
data_dir = 'images/'
image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x),
										  data_transforms[x])
				  for x in ['train', 'val']}
dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=4,
											 shuffle=True, num_workers=4)
			  for x in ['train', 'val']}
			  
dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
class_names = image_datasets['train'].classes

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

#get a batch of training data
inputs, classes = next(iter(dataloaders['train']))

#make a grid from batch
out = torchvision.utils.make_grid(inputs)

def train_model(model, criterion, optimizer, scheduler, num_epochs=no_epochs):
	since = time.time()

	best_model_wts = copy.deepcopy(model.state_dict())
	best_acc = 0.0

	for epoch in range(num_epochs):
		print('Epoch {}/{}'.format(epoch, num_epochs - 1))
		print('-' * 10)

		#each epoch has a training and validation phase
		for phase in ['train', 'val']:
			if phase == 'train':
				scheduler.step()
				model.train()  #set model to training mode
			else:
				model.eval()   #set model to evaluate mode

			running_loss = 0.0
			running_corrects = 0

			#iterate over data.
			for inputs, labels in dataloaders[phase]:
				inputs = inputs.to(device)
				labels = labels.to(device)

				#zero the parameter gradients
				optimizer.zero_grad()

				#forward
				#track history if only in train
				with torch.set_grad_enabled(phase == 'train'):
					outputs = model(inputs)
					_, preds = torch.max(outputs, 1)
					loss = criterion(outputs, labels)

					#backward + optimize only if in training phase
					if phase == 'train':
						loss.backward()
						optimizer.step()

				#statistics
				running_loss += loss.item() * inputs.size(0)
				running_corrects += torch.sum(preds == labels.data)

			epoch_loss = running_loss / dataset_sizes[phase]
			epoch_acc = running_corrects.double() / dataset_sizes[phase]

			print('{} Loss: {:.4f} Acc: {:.4f}'.format(
				phase, epoch_loss, epoch_acc))

			#deep copy the model
			if phase == 'val' and epoch_acc > best_acc:
				best_acc = epoch_acc
				best_model_wts = copy.deepcopy(model.state_dict())

		print()

	time_elapsed = time.time() - since
	print('Training complete in {:.0f}m {:.0f}s'.format(
		time_elapsed // 60, time_elapsed % 60))
	print('Best val Acc: {:4f}'.format(best_acc))

	#load best model weights
	model.load_state_dict(best_model_wts)
	return model
	
def face_train():

	# TODO: need to figure out how to add a single additional image to a previously trained model, at the moment it seems to just reset the whole model
	# if the prior dataset isnt included (so cant deleted other training data)
	
	#when training check for existance of existing model and load it, make a new one if not
	# if os.path.exists(PATH):
		# print("Using existing model")
		# #load pretrained model from local directory
		# model_ft = torch.load(PATH)
		# num_ftrs = model_ft.fc.in_features
		# model_ft.fc = nn.Linear(num_ftrs, number_of_faces)
		
		# model_ft = model_ft.to(device)

		# criterion = nn.CrossEntropyLoss()

		# # Observe that all parameters are being optimized
		# optimizer_ft = optim.SGD(model_ft.parameters(), lr=0.001, momentum=0.9)

		# # Decay LR by a factor of 0.1 every 7 epochs
		# exp_lr_scheduler = lr_scheduler.StepLR(optimizer_ft, step_size=7, gamma=0.1)

		# model_ft = train_model(model_ft, criterion, optimizer_ft, exp_lr_scheduler,
							   # num_epochs=no_epochs)

	# else:
		# print("Using a new model")
		#load a pretrained model
	
	#get the number of faces from the number of training folders
	number_of_faces = len(os.listdir('./images/train'))
	class_names = image_datasets['train'].classes
	
	#load a pretrained model
	model_ft = models.resnet18(pretrained=True)
	num_ftrs = model_ft.fc.in_features
	model_ft.fc = nn.Linear(num_ftrs, number_of_faces)

	model_ft = model_ft.to(device)

	criterion = nn.CrossEntropyLoss()

	#observe that all parameters are being optimized
	optimizer_ft = optim.SGD(model_ft.parameters(), lr=0.001, momentum=0.9)

	#decay LR by a factor of 0.1 every 7 epochs
	exp_lr_scheduler = lr_scheduler.StepLR(optimizer_ft, step_size=7, gamma=0.1)

	#train the model on the face data
	model_ft = train_model(model_ft, criterion, optimizer_ft, exp_lr_scheduler,
						   num_epochs=no_epochs)

	#save the model
	torch.save(model_ft, PATH)

#if called direct then run the function	
if __name__ == '__main__':
	print(face_train())