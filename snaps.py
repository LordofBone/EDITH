import time
import os
from picamera import PiCamera

camera = PiCamera()
camera.rotation = 270

def takePic():
	camera.start_preview()
	time.sleep(1)
	camera.capture('image_cam.jpg')
	camera.stop_preview()

def takePics(num, name):
	
	for i in range(num):
		nameFolder = ("./images/train/" + name + "/image_cam" + str(i) + ".jpg")
		camera.start_preview()
		time.sleep(1)
		camera.capture(nameFolder)
		camera.stop_preview()
		#time.sleep(3)
		
#if called direct then run the function
if __name__ == '__main__':
	takePic()