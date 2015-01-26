from readData import readFileWithData
from mongoDB import conDB,importTwitterConversation, queries
import glob
import os

database = 'DARecognition'
collectionRawTwitterData = 'rawTwitterData'

if (conDB.checkAmount(database, collectionRawTwitterData) == 0):
### Import raw twitter conversation in DB ##########
    for filename in glob.iglob(os.path.join('DATA/twitterConversation','*.txt')):
        content = readFileWithData.readTXT(filename)
        print filename + ' will be added to DB'
        importTwitterConversation.importData(database, collectionRawTwitterData, content)
        print filename + ' is added to DB'
else:
    print 'collection ' + collectionRawTwitterData + ' is already exists'

amountOfTweets = conDB.checkAmount(database, collectionRawTwitterData)
print 'There are ',  amountOfTweets, ' tweets in DB.'
queries.searchFirstTweet(database, collectionRawTwitterData )