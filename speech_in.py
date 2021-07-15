import subprocess
import time
import re
from wit import Wit

#the wit.ai API key (this is a fake one you will need to sign up for your own at wit.ai)
client_wit = Wit('')

def listen():
	inputWords = ""
	while (re.search('[a-zA-Z]', inputWords) is None):
		#using subprocess to call the sox recording software with a configuration to trim silence from the recording and stop recording when the speaker has finished
		#subprocess.call(['rec rec.wav rate 32k silence 1 0.1 2% 1 1.0 2%'], shell=True)
		subprocess.call(['arecord --device=plughw:1,0 -d 6 -f cd -t wav rec.wav'], shell=True)
		resp = None
		#use the wit.ai class to interface with the API and send off the wav file from above for STT functions
		with open('rec.wav', 'rb') as f:
		  resp = client_wit.speech(f, None, {'Content-Type': 'audio/wav'})
		#parse the response given to get the text sent back which will then become the words the bot uses
		inputWords = str(resp['_text'])
		#print the input words to the screen (debug/testing purposes)
		
	return inputWords
	
#if called direct then run the function
if __name__ == '__main__':
	print (listen())