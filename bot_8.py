#!/usr/bin/

#imports
import sys
import os
import subprocess
import time
import random
import pymongo
import datetime
import time
import numpy
from colors import *
from pymongo import MongoClient
from pprint import pprint
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz

#main class where all the workings happen
class talkLoop(object):
	
	#initialise the class with all variables required
	def __init__(self, name, client, db, responses, allwords, inputWords, globalReply, botAccuracy, debugMode):
		self.name = name
		self.client = client
		self.db = db
		self.responses = responses
		self.allwords = allwords
		self.wordsIn = inputWords
		self.globalReply = globalReply
		self.botAccuracy = botAccuracy
		self.bResponse = globalReply
		self.debugMode = debugMode
		self.updateDB(inputWords)
		
	#function for comparing string similarity
	def similar(self, a, b):
		return SequenceMatcher(None, a, b).ratio()
	
	#function for grabbing a random document from the database
	def get_random_doc(self, collection):
		count = collection.count()
		return collection.find()[random.randrange(count)]
	
	#this function generates a random sentence at any length between 1 and 10 words long
	def sentenceGen(self):
		#set a clear string and set a random integer 1-10
		result = ""
		length = random.randint(1, 10)
		
		#for the range in the integer above find a random word from the db and append to the string
		for i in range(length):
			cursor = self.get_random_doc(self.allwords)
			for x, y in cursor.items():
				if x == "word":
					cWord = (y)
					result += cWord
					result += ' '
					#clear the cursor
					del cursor
		#return the constructed sentence
		return result
	
	#this function searches the database for the input string and returns all replies for that string, returning a random one
	def dbSearch(self, searchIn):
		#search the database for inputs the bot has said prior
		cursor = self.responses.find_one({"whatbotsaid": searchIn})
		#return list of human replies to this response and choose one at random
		for x, y in cursor.items():
			if x == 'humanReply':
				chosenReply = (random.choice(y))
		#erase the cursor and return the chosen string
		del cursor
		return chosenReply
		
	#this function returns a random sentence from the entire db
	def randomSentence(self):
		cursor = self.get_random_doc(self.responses)
		for x, y in cursor.items():
			if x == 'humanReply':
				chosenReply = (random.choice(y))
		return chosenReply
	
	#the string comparison function
	def mongoFuzzyMatch(self, inputString, searchZone, termZone, setting):
		#create an empty dictionary
		compareList = {}
		#search the database passed in
		for cursor in searchZone.find():
			for x, y in cursor.items():
				#find the item in the cursor that matches the search term passed into the function, eg: 'whatbotsaid'				
				if x == termZone:
					#compare the input string to the current string in the cursor, which returns a decimal point of accuracy (0.0 > 1.0)
					
					#OLD METHOD
					#compareNo = self.similar(inputString, y)
					
					#if accuracy is off then append the string and its accuracy to the dictionary no matter the accuracy
					if setting == ('off'):
						compareNo = fuzz.token_set_ratio(inputString.lower(), y.lower())
						if compareNo > self.botAccuracy-30:
							compareList[y] = compareNo
					#if accuracy is medium then append the string and its accuracy to the dictionary only if its over the medium setting
					elif setting == ('med'):
						compareNo = fuzz.partial_ratio(inputString.lower(), y.lower())
						if compareNo > self.botAccuracy-20:
							compareList[y] = compareNo
					#if accuracy is on/high then append the string and its accuracy to the dictionary only if its over the on/high setting
					elif setting == ('on'):
						compareNo = fuzz.ratio(inputString.lower(), y.lower())
						if compareNo > self.botAccuracy:
							compareList[y] = compareNo
		#if nothing found then return a non match
		if compareList == {}:
			compareChosen = 'none_match'
		#if there are matching strings identify the highest accuracy from the dictionary made above		
		else:
			compareChosen = max(compareList.keys(), key=(lambda key: compareList[key]))
		#erase the cursor and return the chosen matching string
		del cursor
		if (self.debugMode == True):
			print(compareChosen)
		return compareChosen
	
	
	def replyTumbler(self):
		if self.name == ("--trainer--"):
			self.bResponse = self.wordsIn
			return ("")
		#find the search string using the high accuracy number - to find a decent match to what the bot has said prior
		#when this function is called it required four arguments: the human response, the database to search on, the response required from the database and the accuracy level
		searchSaid = self.mongoFuzzyMatch(self.wordsIn, self.responses, 'whatbotsaid', 'on')
		#if no matches then try with a lower accuracy to find a less similar sentence
		if searchSaid == ('none_match'):
			searchSaid = self.mongoFuzzyMatch(self.wordsIn, self.responses, 'whatbotsaid', 'med')
			if searchSaid == ('none_match'):
				searchSaid = self.mongoFuzzyMatch(self.wordsIn, self.responses, 'whatbotsaid', 'off')
				if searchSaid == ('none_match'):
					#if still no match then move onto generating a totally random reply or grab a random sentence from the db
					if searchSaid == ('none_match'):
						if random.randrange(100) <= 60:
							chosenReply = self.randomSentence()	
							self.bResponse = chosenReply
							return (chosenReply)							
						else:
							chosenReply = self.sentenceGen()
							self.bResponse = chosenReply
							return (chosenReply)
					else:
						#pass the response into the database to find prior human responses to the above sentence
						chosenReply = self.dbSearch(searchSaid)
						
		#pass the response into the database to find prior human responses to the above sentence		
		chosenReply = self.dbSearch(searchSaid)
			
		#clear the search variable
		del searchSaid
		self.bResponse = chosenReply
		return (chosenReply)

	#this function passes in the information from the loop, the input reply and the bots last reply and appends them to the database	
	def updateDB(self, wordsIn):
		self.wordsIn = wordsIn
		#search the database for prior responses the bot has said
		cursor = self.responses.find_one({"whatbotsaid": self.bResponse})
		#if none then store a new bot response with the humans reply
		if cursor is None:
			postR = {"whatbotsaid": self.bResponse, "humanReply": [self.wordsIn]}
			self.responses.insert_one(postR).inserted_id
			del cursor
		#if already existing then update the database with a new reply
		else:
			self.responses.update_one({"whatbotsaid": self.bResponse}, {'$addToSet':{"humanReply": self.wordsIn}}, upsert=True)
			#clear the cursor
			del cursor
		
		#split the input sentence into individual words and store each in the database
		wordsInDB = self.wordsIn.split(' ')
		for word in wordsInDB:
			#search the database for the word
			cursor = self.allwords.find_one({"word": word})
			#if its not already in the database then insert into the database
			if cursor is None:
				postW = {"word": word}
				self.allwords.insert_one(postW).inserted_id
			#if the word is already in the database pass and clear the cursor
			else:
				pass
			del cursor
			

def dbWordsUpdate(objectIn):
	#split the input sentence into individual words and store each in the database
	wordsInDB = objectIn.split(' ')
	for word in wordsInDB:
		#search the database for the word
		cursor = allwords.find_one({"word": word})
		#if its not already in the database then insert into the database
		if cursor is None:
			postW = {"word": word}
			allwords.insert_one(postW).inserted_id
		#if the word is already in the database pass and clear the cursor
		else:
			pass
		del cursor
		
def conversation(inputWords, personName):
	#if person name is already initialised as a class with talk loop then check if its the same as the previous person from last response
	if personName in name_dict:
		if personName == prevPerson["prev_person"]:
			#if it is still the same person chatbot talking to put their response in and get a reply from the bot
			name_dict[personName].updateDB(inputWords)
			globalReply = (name_dict[personName].replyTumbler())
		else:
			#if it is a different person from before then get a reponse from the bot using the humans prior response - to continue the conversation
			globalReply = (name_dict[personName].replyTumbler())
	else:
		#if human new then initialise them with the talk loop class
		name_dict.update({personName: talkLoop(name=personName, client=client, db=db, responses=responses, allwords=allwords, inputWords="hello", globalReply="hello", botAccuracy=botAccuracy, debugMode=debugMode)})
		#get an intial reply
		globalReply = (name_dict[personName].replyTumbler())
		#combine the greeting with the humans name
		globalReply = str(globalReply + " " + personName)
	
	#set previous person
	prevPerson["prev_person"] = personName
	
	#return the reply
	return globalReply
		
#setting up variables for mongodb
client = MongoClient('localhost', 27017)
db = client.words_database
responses = db.responses
allwords = db.allwords

#accuracy variable (percentage)
botAccuracy = 95
debugMode = False

#blank variables
name_dict = {}
prevPerson = {"prev_person": ""}

#if called direct then run the function
if __name__ == '__main__':
	if len(sys.argv) > 1:
		try:
			sys.argv[1] = int(sys.argv[1])
		except ValueError:
			print ('There are two optional switches: accuracy <0-100> and <-debug>')
			sys.exit()
			
		botAccuracy = sys.argv[1]

		if len(sys.argv) > 2:
			try:
				sys.argv[2] = str(sys.argv[2])
			except ValueError:
				print ('There are two optional switches: accuracy <0-100> and <-debug>')
				sys.exit()
			
			if sys.argv[2] == ("-debug"):
				debugMode = True
			else:
				print ('There are two optional switches: accuracy <0-100> and <-debug>')
				sys.exit()

	
	#request name
	sys.stdout.write(BLUE)
	name = input('Your name:	')
	sys.stdout.write(RESET)
	
	#get reply and print for logging/debugging
	reply = conversation(input, name)
	sys.stdout.write(RED)
	print("Bot: " + reply)
	sys.stdout.write(RESET)

	while True:
		#get another response and print
		sys.stdout.write(BLUE)
		input = input('You:	')
		sys.stdout.write(RESET)#
		#if response is blank, rerun loop
		if input == (""):
			continue
		#with 'change_name' typed in it will request new name - for debugging and testing
		if input == ("change_name"):
			sys.stdout.write(BLUE)
			name = raw_input('Your name:	')
			sys.stdout.write(RESET)
			#get another reply
			reply = conversation(input, name)
			#print reply
			sys.stdout.write(RED)
			print("Bot: " + reply)
			sys.stdout.write(RESET)
			#rerun the loop with new name
			continue
		#for a normal response grab another reply and print
		reply = conversation(input, name)
		sys.stdout.write(RED)
		print("Bot: " + reply)
		sys.stdout.write(RESET)
