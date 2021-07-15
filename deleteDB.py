import sys
import random
import pymongo
from pymongo import MongoClient

def delDB():
	client = MongoClient('localhost', 27017)
	db = client.words_database

	client.drop_database(db)
	
	self._ensure_opened()

if __name__ == "__main__":
	delDB()
