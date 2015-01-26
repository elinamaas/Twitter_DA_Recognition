# get first document form the collection
import conDB

def searchFirstTweet(dbName, collectionName):
    tweetsCollection = conDB.getCollection(dbName, collectionName)
    tweet = tweetsCollection.find_one()
    print tweet