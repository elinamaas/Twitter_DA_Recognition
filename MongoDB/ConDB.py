__author__ = 'snownettle'
import pymongo
from pymongo import Connection

##########################
# Connect to MongoDB
##########################

# mongodb creates databases and collections automatically for you if they dont exist already.
# The DB will be schown firstly if there is smth already


def get_collection(dbName, collectionName):
    # default connection
    connection = Connection()
    # drop Db
    #connection.drop_database(dbName)
    # Getting/Creating  DB

    db = connection[dbName]
    # Getting/Creating Collection
    collection = db[collectionName]
    return collection


def check_tweets_amount(collectionName):
    return collectionName.count()
