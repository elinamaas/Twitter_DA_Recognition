__author__ = 'snownettle'
from readData import rawTwitterData, annotatedData_read
from mongoDB import mongoDB_configuration, importTwitterConversation, queries
from annotatedData.editing_annotated_tweets import segmentation, merge_annotations, rewrite_segmentation, merge_da_children
from annotatedData.annotated_tweets_final import editing_annotated_tweets
from statistics import annotatedData_stat
from annotation.dialogue_acts_tree import build_da_taxonomy
import glob
import os


database = 'DARecognition'

# make all connection to db here
collectionRawTwitterData = mongoDB_configuration.get_collection(database, 'rawTwitterData')
collectionAnnotatedData = mongoDB_configuration.get_collection(database, 'annotatedTwitterData')
rawTwitterConversation_path = 'DATA/twitterConversation'
annotatedData_path = 'DATA/annotationed/webanno-projectexport/annotation'

if mongoDB_configuration.check_tweets_amount(collectionRawTwitterData) == 0:
    #  Import raw twitter_objects conversation in DB
    rawTwitterData.import_raw_twitter_data(rawTwitterConversation_path, collectionRawTwitterData)

else:
    print 'Collection ' + collectionRawTwitterData.name + ' is already existed'

amountOfRawTweets = queries.check_tweets_amount(collectionRawTwitterData)
print 'There are ',  amountOfRawTweets, ' raw tweets in DB.'


if mongoDB_configuration.check_tweets_amount(collectionAnnotatedData) == 0:
    annotatedData_read.read_annotated_docs(annotatedData_path, collectionAnnotatedData)
else:
    print 'Collection ' + collectionAnnotatedData.name + ' is already existed'
amountOdAnnotatedTweets = mongoDB_configuration.check_tweets_amount(collectionAnnotatedData)

editing_annotated_tweets(collectionAnnotatedData)
