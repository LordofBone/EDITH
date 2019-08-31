import subprocess
import re
import sys

#function for searching whether the computer name is present
def findWholeWord(w):
	return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

def computerOn(inputText):
	mac = ''
	computer = ''
	#load the macs file
	macfile = open('macs.txt','r')
	macs = macfile.readlines()
	print (inputText)
	#search through items in macs and see if input is matched, if so mac address is returned
	for item in macs:
		for word in inputText.split():
			print (word, item)
			if (findWholeWord(word)(item)):
				computer, mac = item.split(',')
	if mac == '':
		return(False)
	else:
		#make wake command
		wakeCommand = ('wakeonlan ' + mac)
		wakeNotification = str("waking computer " + computer)
		#send wake on lan packet 6 times to be safe
		for x in range(6):
			subprocess.call([wakeCommand], shell=True)
		macfile.close()
		return(True)