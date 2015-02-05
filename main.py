__author__ = 'snownettle'
from readData import rawTwitterData, annotatedData_read
from mongoDB import conDB, importTwitterConversation, queries
from statistics import annotatedData_stat
import glob
import os
import tweet


database = 'DARecognition'
# collectionRawTwitterData = 'rawTwitterData'
# make all connection to db here
collectionRawTwitterData = conDB.get_collection(database, 'rawTwitterData')
collectionAnnotatedData = conDB.get_collection(database, 'annotatedTwitterData')
rawTwitterConversation_path = 'DATA/twitterConversation'
annotatedData_path = 'DATA/annotationed/webanno-projectexport/annotation'

if conDB.check_tweets_amount(collectionRawTwitterData) == 0:
    #  Import raw twitter conversation in DB
    rawTwitterData.import_raw_twitter_data(rawTwitterConversation_path, collectionRawTwitterData)
    # for filename in glob.iglob(os.path.join('DATA/test','*.txt')):
    #     content = rawTwitterData.readTXT(filename)
    #     print filename + ' will be added to DB'
    #     importTwitterConversation.importData(collectionRawTwitterData, content)
    #     print filename + ' is added to DB'
else:
    print 'Collection ' + collectionRawTwitterData.name + ' is already existed'

amountOfRawTweets = conDB.check_tweets_amount(collectionRawTwitterData)
print 'There are ',  amountOfRawTweets, ' raw tweets in DB.'
# queries.search_first_tweet(database, collectionRawTwitterData)
#conversations = queries.check_lang(database, collectionRawTwitterData)
# conversations = queries.build_conversation(collectionRawTwitterData)
# for conversation in conversations:
#     conversation.conversation_length()


# collectionAnnotatedData.drop()

if conDB.check_tweets_amount(collectionAnnotatedData) == 0:
    annotatedData_read.read_annotated_docs(annotatedData_path, collectionAnnotatedData)
else:
    print 'Collection ' + collectionAnnotatedData.name + ' is already existed'
amountOdAnnotatedTweets = conDB.check_tweets_amount(collectionAnnotatedData)
# print 'There are ', amountOdAnnotatedTweets, ' annotated tweets by linguistic students in DB'

annotatedData_stat.segmentation(collectionAnnotatedData)

