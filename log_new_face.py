import subprocess
import sys
import os

def log_face(name):
	#create a directory under the training folder with the new persons name
	path = ("./images/train/" + name)
	if not os.path.exists(path):
		mkdirexe = ("mkdir " + path)
		subprocess.call([mkdirexe], shell=True)
	
	#copy the most recent image into the new named folder
	copyexe = ("cp image_cam.jpg " + path)
	subprocess.call([copyexe], shell=True)

#if called direct then run the function
if __name__ == '__main__':
	name = sys.argv[1]
	print(log_face(name))