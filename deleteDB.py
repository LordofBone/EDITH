import sys
import random
import pymongo
import sys
from pymongo import MongoClient

def delDB():
	client = MongoClient('localhost', 27017)
	db = client.words_database

	client.drop_database(db)

if __name__ == "__main__":
	delDB()
