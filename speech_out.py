import sys
import subprocess

def tts(input):
	#use subprocess again to initialise espeak (the TTS) and say the bots response
	subprocess.call(['espeak', '-v', 'mb-us1+f3', input])

#if called direct then run the function
if __name__ == '__main__':
	text = sys.argv[1]
	tts(text)