import face_infer
import face_trainer
import log_new_face
import news
import wolfram_access
import screen2
#import snaps
import wakeonlan
from colors import *
import shutdown
import sys
import time
import os

#set accuracy threshold needed to be reached in order to determine human id
accuracyThreshold = float(0.9)

#instantiate the screencontrol class
screenControl = screen.Drawing()

#clear the screen
screenControl.clearScreen()

#intro texts
introText = ("Hi, I am EDITH, please identify yourself")
declinedText = ("You are not an authorized user. Goodbye.")

#authorised users list
authed = ['grayson, gay, gary']

#get userid
speech_out.tts(introText)
screenControl.drawText("Identify", "yourself")
userid = speech_in.listen()

#check name of user and if one of the authorised users then continue, if not; exit
if userid in authed:
	screenControl.clearScreen()
	screenControl.drawText("Hello", userid)
	speech_out.tts("Hello, " + userid)
else:
	screenControl.clearScreen()
	screenControl.drawText("You are not", "authorized")
	speech_out.tts(declinedText)
	shutdown.shutdown()

#setup face inference
class_names, device, model_trained = face_infer.loadAndSetup()

#clear initial input variable
inputWords = ("")

#keywords lists:

#conversation
convoKeys = ['talk', 'conversation', 'chat', 'lets talk', 'talking', 'hello']
#faceID
faceKeys = ['face', 'identify', 'who', 'person']
#shutdown
shutdownKeys = ['turn off', 'shutdown', 'shut down']
#reboot
rebootKeys = ['reboot', 'restart']
#goodbye
goodbyeList = ['bye', 'goodbye', 'see ya', 'good bye']
#wolfram queries
queryKeys = ['query', 'question', 'ask', 'search', 'ask a question', 'ask question', 'where', 'what', 'why', 'when']
#news
newsKeys = ['the news', 'news', 'what is the news', 'whats the news']
#photo
photo = ['photo', 'picture', 'pic', 'take photo', 'take a photo', 'image', 'take image', 'see']
#menu
menuOpts = ['edith', 'menu', 'select', 'options', 'do something', 'they there']
#retrain
retrainKeys = ['train', 'retrain', 'train faces', 'retrain faces', 'train net', 'retrain net']
#wake on lan
wolKeys = ['wake', 'wake up', 'switch on', 'computer on', 'wake computer', 'turn on computer']

#function for taking photos
def snapPhoto():
	#draw square and text to show pic is being taken
	screenControl.clearScreen()
	screenControl.drawRectangle()
	speech_out.tts("Taking a photo, please look at target")
	#take a pic
	snaps.takePic()
	#draw ellipse to show picture has been taken successfully
	screenControl.clearScreen()
	screenControl.drawEllipse()
	screenControl.drawText("Done", "")
	time.sleep(5)

#function for running faceids
def humanid():
	screenControl.clearScreen()
	
	#set print colour for outputs
	sys.stdout.write(RED)
	
	#clear variables for loop start
	#topPrediction = ()
	#topPredictionConfidence = ()
	humanid = ("noone")
	
	#take a pic
	snapPhoto()
	
	screenControl.clearScreen()
	
	#output for logging
	print("Processing objects and looking for faces")
	screenControl.drawText("Processing", "image")
	
	#get predictions from vision analysis module
	#topPrediction, topPredictionConfidence, userid, confidence = vision_analysis.imageAnalyse(class_names, device, model_trained)
	
	humanid, confidence = face_infer.infer_face(class_names, device, model_trained)
	
	print(humanid)
	print(confidence)
	
	if confidence < accuracyThreshold:
		humanid = ("unknown")
	
	#print outputs of object inference for logging/debug
	#print(topPrediction)
	#print(topPredictionConfidence)
	
	#send outputs of object inference to chatbot
	#chatbot.dbWordsUpdate(topPrediction)

	
	#if human id none - say out loud the results from object inference
	#if userid == "noone":
	#	speech_out.tts("No faces detected")
	#	screenControl.drawText("No faces", "detected")
	
	#if human id unknown grab photos of them and log to training folder
	if humanid == "unknown":
		screenControl.clearScreen()
		print("No face identified")
		speech_out.tts("Please identify this person")
		screenControl.drawText("Please identify", "this person")
		humanid = speech_in.listen()
		sys.stdout.write(RED)
		print(humanid)
		sys.stdout.write(RESET)
		log_new_face.log_face(humanid)
		speech_out.tts("Snapping pics")
		screenControl.drawText("Snapping", "pics")
		snaps.takePics(9, humanid)
		screenControl.clearScreen()
		screenControl.drawEllipse()
		screenControl.drawText("Done", "")
	else:
		screenControl.clearScreen()
		#if human identified log out to 
		print("Face identified:" + humanid)
		screenControl.drawText("Face identified:", humanid)
		speech_out.tts(humanid)
			
	time.sleep(5)

#function for retraining the net with new faces
def reTrain():
	screenControl.clearScreen()
	speech_out.tts("Training neural net with new face, please wait")
	screenControl.drawText("Training", "new face(s)")
	face_trainer.face_train()
	speech_out.tts("Training complete")
	screenControl.drawText("Training", "complete")
	#reload model and classes containing names into face inference module
	class_names, device, model_trained = face_infer.loadAndSetup()

#chatbot conversation function
def convoAI(inputWords, userid):
	screenControl.clearScreen()
		
	screenControl.drawText("In", "conversation")
	
	#run conversation loop
	while True:
		#bot gives initial greeting
		#send off input and human id to chatbot
		reply = chatbot.conversation(inputWords, userid)
		
		#print reply for debugging/logging
		sys.stdout.write(BLUE)
		print(reply)
		sys.stdout.write(RESET)
		
		#use tts for saying reply
		speech_out.tts(reply)
		#human response is taken and printed - then loops around putting the input back into the conversation module
		inputWords = speech_in.listen()
		if inputWords in goodbyeList:
			screenControl.clearScreen()
			return
		sys.stdout.write(BLUE)
		print(inputWords)
		sys.stdout.write(RESET)

#wolfram query and response function
def queryWolframAlpha():
	#draw instructions on screen
	screenControl.clearScreen()	
	screenControl.drawText("Ask a", "question")
	
	#get the question from the speech to text engine
	question = speech_in.listen()
	
	#send the answer into wolfram and get the answer string
	answer = wolfram_access.runQuery(question)
	
	#put the string through tts
	speech_out.tts(answer)
	
	#and draw the answer on screen and keep it there for a bit
	screenControl.drawText("Answer:", answer)
	
	time.sleep(5)
	
#wake on lan function 
def runWakeOnLAN():
	#draw instructions on screen
	screenControl.clearScreen()	
	screenControl.drawText("Computer", "name")
	
	while True:
	
		#instruct user
		speech_out.tts("Please name computer to switch on.")
		
		#get the question from the speech to text engine
		pcNameInput = speech_in.listen()
		
		if pcNameInput == "exit":
			return
		
		#send the computer name off to the wol module
		if wakeonlan.computerOn(pcNameInput) == False:
			speech_out.tts("Computer not found, please try again")
			continue
		else:
			break
		
	
	#put the string through tts
	speech_out.tts("Turning on" + pcNameInput)
	
	#and draw the answer on screen and keep it there for a bit
	screenControl.drawText("Turning on:", pcNameInput)
	
	time.sleep(5)
	
#news function
def showNews():
	newsList = []
	newsList = news.getNews()
	screenControl.clearScreen()
	screenControl.drawText("The", "news")
	
	for i in newsList:
		speech_out.tts(i)

#main menu functions
def menu():
	#display to user that the glasses are ready for commands
	screenControl.clearScreen()
	screenControl.drawText("Make", "Selection")
	speech_out.tts("What would you like to do")

	#start listening
	inputWords = ("")
	inputWords = speech_in.listen()
	
	if inputWords in photo:
		snapPhoto()
		return
	if inputWords in convoKeys:
		convoAI(inputWords, userid)
		return
	if inputWords in queryKeys:
		queryWolframAlpha()
		return
	if inputWords in newsKeys:
		showNews()
		return
	if inputWords in faceKeys:
		humanid()
		return
	if inputWords in retrainKeys:
		reTrain()
		return
	if inputWords in wolKeys:
		runWakeOnLAN()
		return
	if inputWords in rebootKeys:
		screenControl.drawText("Rebooting", "")
		speech_out.tts("Rebooting")
		shutdown.reboot()
	if inputWords in shutdownKeys:
		screenControl.drawText("Shutting", "Down")
		speech_out.tts("Shutting Down")
		shutdown.shutdown()
	else:
		screenControl.clearScreen()
		screenControl.drawText("Try", "again")
		speech_out.tts("Please try again")
		menu()

#listening loop to intitiate the menu		
while True:
	#display to the user that the glasses are ready for commands
	screenControl.clearScreen()
	screenControl.drawText("Hello", userid)

	#start listening
	inputWords = ("")
	inputWords = speech_in.listen()
	
	#if one of the menu keywords is spoken then open the menu
	if inputWords in menuOpts:
		menu()

