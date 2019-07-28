import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

class Drawing():

	#initialise the class with all variables required
	def __init__(self):

		# Create blank image for drawing.
		# Make sure to create image with mode '1' for 1-bit color.
		self.width = disp.width
		self.height = disp.height
		self.image = Image.new('1', (self.width, self.height))
		self.mimage = Image.new('1', (self.width, self.height))
		
		# Get drawing object to draw on image.
		self.draw = ImageDraw.Draw(self.image)
		
		# Load default font.
		self.font = ImageFont.load_default()

		# First define some constants to allow easy resizing of shapes.
		self.padding = 2
		self.shape_width = 20
		self.top = self.padding
		self.bottom = self.height-self.padding
		# Move left to right keeping track of the current x position for drawing shapes.
		self.x = self.padding
		
	def drawStats(self):
		# Clear display.
		self.clearScreen()
		
		while True:
			
			# Draw a black filled box to clear the image.
			self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)

			# Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
			cmd = "hostname -I | cut -d\' \' -f1"
			IP = subprocess.check_output(cmd, shell = True )
			cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
			CPU = subprocess.check_output(cmd, shell = True )
			cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
			MemUsage = subprocess.check_output(cmd, shell = True )
			cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
			Disk = subprocess.check_output(cmd, shell = True )

			# Write two lines of text.

			self.draw.text((self.x, self.top),       "IP: " + str(IP),  font=self.font, fill=255)
			self.draw.text((self.x, self.top+8),     str(CPU), font=self.font, fill=255)
			self.draw.text((self.x, self.top+16),    str(MemUsage),  font=self.font, fill=255)
			self.draw.text((self.x, self.top+25),    str(Disk),  font=self.font, fill=255)
			
			# Flip the image so its the right way around in the glasses lense
			self.mimage = self.image.transpose(Image.FLIP_TOP_BOTTOM)
			
			# Display image.
			disp.image(self.mimage)
			disp.display()
			time.sleep(.1)

	def drawText(self, MESSAGE1, MESSAGE2):
	
		# Write two lines of text.
		self.draw.text((self.x, self.top),    MESSAGE1,  font=self.font, fill=255)
		self.draw.text((self.x, self.top+20), MESSAGE2, font=self.font, fill=255)
		
		# Flip the image so its the right way around in the glasses lense
		self.mimage = self.image.transpose(Image.FLIP_TOP_BOTTOM)
		#self.mimage = self.image.transpose(Image.FLIP_LEFT_RIGHT)
		
		# Display image.
		disp.image(self.mimage)
		disp.display()
		
		self.x += self.shape_width+self.padding

			
	def drawImage(self, image_file):
		# Clear display.
		disp.clear()
		disp.display()

		# Load image based on OLED display self.height.  Note that image is converted to 1 bit color.
		if disp.height == 64:
			self.image = Image.open('happycat_oled_64.ppm').convert('1')
		else:
			self.image = Image.open('happycat_oled_32.ppm').convert('1')

		# Alternatively load a different format image, resize it, and convert to 1 bit color.
		#image = Image.open('happycat.png').resize((disp.self.self.width, disp.self.height), Image.ANTIALIAS).convert('1')

		# Display image.
		disp.image(self.image)
		disp.display()
		
	def drawRectangle(self):

		# Draw a rectangle.
		self.draw.rectangle((self.x, self.top, self.x+self.shape_width, self.bottom), outline=255, fill=0)

		# Load default font.
		font = ImageFont.load_default()
		
		# Flip the image so its the right way around in the glasses lense
		self.mimage = self.image.transpose(Image.FLIP_TOP_BOTTOM)

		# Display image.
		disp.image(self.mimage)
		disp.display()
		
		self.x += self.shape_width+self.padding
		
	def drawTriangle(self):
	
		# Draw a triangle.
		self.draw.polygon([(self.x, self.bottom), (self.x+self.shape_width/2, self.top), (self.x+self.shape_width, self.bottom)], outline=255, fill=0)
		
		# Flip the image so its the right way around in the glasses lense
		self.mimage = self.image.transpose(Image.FLIP_TOP_BOTTOM)
		
		# Display image.
		disp.image(self.mimage)
		disp.display()
		
		self.x += self.shape_width+self.padding


	def drawEllipse(self):

		# Draw an ellipse.
		self.draw.ellipse((self.x, self.top , self.x+self.shape_width, self.bottom), outline=255, fill=0)

		# Flip the image so its the right way around in the glasses lense
		self.mimage = self.image.transpose(Image.FLIP_TOP_BOTTOM)

		# Display image.
		disp.image(self.mimage)
		disp.display()
		
		self.x += self.shape_width+self.padding


	def drawLine(self):

		# Draw an X.
		self.draw.line((self.x, self.bottom, self.x+self.shape_width, self.top), fill=255)
		self.draw.line((self.x, self.top, self.x+self.shape_width, self.bottom), fill=255)

		# Flip the image so its the right way around in the glasses lense
		self.mimage = self.image.transpose(Image.FLIP_TOP_BOTTOM)

		# Display image.
		disp.image(self.mimage)
		disp.display()
		
		self.x += self.shape_width+self.padding

	def clearScreen(self):
		disp.clear()
		disp.display()

		# Create blank image for drawing.
		# Make sure to create image with mode '1' for 1-bit color.
		self.width = disp.width
		self.height = disp.height
		self.image = Image.new('1', (self.width, self.height))
		self.mimage = Image.new('1', (self.width, self.height))

		# Get drawing object to draw on image.
		self.draw = ImageDraw.Draw(self.image)
		
		# First define some constants to allow easy resizing of shapes.
		self.padding = 2
		self.shape_width = 20
		self.top = self.padding
		self.bottom = self.height-self.padding
		# Move left to right keeping track of the current x position for drawing shapes.
		self.x = self.padding


#if called direct then run the function
if __name__ == '__main__':
	demo = Drawing()
	demo.drawText("DEMO", "1")
