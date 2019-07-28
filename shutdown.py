import subprocess

#shutdown
def shutdown():
	subprocess.call('sudo shutdown now', shell=True)
	
#reboot
def reboot():
	subprocess.call('sudo restart now', shell=True)
	
#if called direct then run the function
if __name__ == '__main__':
	shutdown()
