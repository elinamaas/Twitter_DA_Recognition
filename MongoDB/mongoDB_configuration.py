__author__ = 'snownettle'
import pymongo
from pymongo import Connection

##########################
# Connect to MongoDB
##########################

# mongodb creates databases and collections automatically for you if they dont exist already.
# The DB will be schown firstly if there is smth already

db_name = 'DARecognition'
collectionNameAllAnnotations = 'annotatedTwitterDataAllOntologies'
pathToAnnotatedData = 'DATA/annotationed/webanno-projectexport/annotation'
pathAnnotatedDataRAW = 'DATA/annotated_tweets_raw.txt'


def get_collection(database_name, collection_name):
    # default connection
    connection = Connection()
    # drop Db
    #connection.drop_database(dbName)
    # Getting/Creating  DB

    db = connection[database_name]
    # Getting/Creating Collection
    collection = db[collection_name]

    return collection


def check_tweets_amount(collection_name):
    return collection_name.count()
