__author__ = 'snownettle'
from readData import rawTwitterData, annotatedData_read
from mongoDB import conDB, importTwitterConversation, queries
from AnnotatedData.editing_annotated_tweets import segmentation, merge_annotations
from AnnotatedData.tweets_for_editing import write_to_file
from statistics import annotatedData_stat
import glob
import os
import tweet


database = 'DARecognition'

# make all connection to db here
collectionRawTwitterData = conDB.get_collection(database, 'rawTwitterData')
collectionAnnotatedData = conDB.get_collection(database, 'annotatedTwitterData')
rawTwitterConversation_path = 'DATA/twitterConversation'
annotatedData_path = 'DATA/annotationed/webanno-projectexport/annotation'

if conDB.check_tweets_amount(collectionRawTwitterData) == 0:
    #  Import raw twitter conversation in DB
    rawTwitterData.import_raw_twitter_data(rawTwitterConversation_path, collectionRawTwitterData)

else:
    print 'Collection ' + collectionRawTwitterData.name + ' is already existed'

amountOfRawTweets = conDB.check_tweets_amount(collectionRawTwitterData)
print 'There are ',  amountOfRawTweets, ' raw tweets in DB.'


if conDB.check_tweets_amount(collectionAnnotatedData) == 0:
    annotatedData_read.read_annotated_docs(annotatedData_path, collectionAnnotatedData)
else:
    print 'Collection ' + collectionAnnotatedData.name + ' is already existed'
amountOdAnnotatedTweets = conDB.check_tweets_amount(collectionAnnotatedData)

list_of_annotated_tweets = segmentation(collectionAnnotatedData)
annotatedData_stat.number_of_annotated_tweet(list_of_annotated_tweets)
annotatedData_stat.numbers_of_tweets_agreed_by_three(list_of_annotated_tweets)

list_of_annotated_tweets = merge_annotations(list_of_annotated_tweets)
list_of_tweets_for_editing = annotatedData_stat.numbers_of_agreed_tweets_after_merging(list_of_annotated_tweets)

write_to_file(list_of_tweets_for_editing)

