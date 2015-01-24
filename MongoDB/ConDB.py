import pymongo
from pymongo import Connection

##########################
# Connect to MongoDB
##########################

# mongodb creates databases and collections automatically for you if they dont exist already.
# The DB will be schown firstly if there is smth already


def mongoDbConnection(collectionName):
    # default connection
    connection = Connection()
    # Getting/Creating  DB
    db = connection['DARecognition']
    # Getting/Creating Collection
    collection = db[collectionName]
    return collection

# ####Insert data into collection ####
# collection.insert({"twitterId" : "11111", "text": "blablabla"})
# collection.insert({"twitterId" : "122222", "text": "bleeeebla"})

# #### Delete unnesessary DB ####
