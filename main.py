__author__ = 'snownettle'
from readData import rawTwitterData, annotatedData_read
from mongoDB import mongoDB_configuration, importTwitterConversation, queries
from annotatedData.editing_annotated_tweets import segmentation, merge_annotations, rewrite_segmentation, merge_da_children
from annotatedData.tweets_after_editing import write_to_file
from statistics import annotatedData_stat
from annotation.dialogue_acts_tree import build_da_taxonomy
import glob
import os
import tweet


database = 'DARecognition'

# make all connection to db here
collectionRawTwitterData = mongoDB_configuration.get_collection(database, 'rawTwitterData')
collectionAnnotatedData = mongoDB_configuration.get_collection(database, 'annotatedTwitterData')
rawTwitterConversation_path = 'DATA/twitterConversation'
annotatedData_path = 'DATA/annotationed/webanno-projectexport/annotation'

if mongoDB_configuration.check_tweets_amount(collectionRawTwitterData) == 0:
    #  Import raw twitter conversation in DB
    rawTwitterData.import_raw_twitter_data(rawTwitterConversation_path, collectionRawTwitterData)

else:
    print 'Collection ' + collectionRawTwitterData.name + ' is already existed'

amountOfRawTweets = mongoDB_configuration.check_tweets_amount(collectionRawTwitterData)
print 'There are ',  amountOfRawTweets, ' raw tweets in DB.'


if mongoDB_configuration.check_tweets_amount(collectionAnnotatedData) == 0:
    annotatedData_read.read_annotated_docs(annotatedData_path, collectionAnnotatedData)
else:
    print 'Collection ' + collectionAnnotatedData.name + ' is already existed'
amountOdAnnotatedTweets = mongoDB_configuration.check_tweets_amount(collectionAnnotatedData)

list_of_annotated_tweets = segmentation(collectionAnnotatedData)
annotatedData_stat.number_of_annotated_tweet(list_of_annotated_tweets)
annotatedData_stat.numbers_of_tweets_agreed_by_three(list_of_annotated_tweets)

print 'First merge of tags after reading the data' #choosing where is the number bigger
#first merge of tags, after building the list
list_of_annotated_tweets = merge_annotations(list_of_annotated_tweets)
rewrite_segmentation(list_of_annotated_tweets)
list_of_tweets_done, list_of_tweets_for_editing = annotatedData_stat.numbers_of_agreed_tweets_after_merging(list_of_annotated_tweets)

print 'First merge of tag children'
#first merge of children
da_taxonomy = build_da_taxonomy()
merge_da_children(list_of_annotated_tweets, da_taxonomy)
rewrite_segmentation(list_of_annotated_tweets)
list_of_tweets_done, list_of_tweets_for_editing = annotatedData_stat.numbers_of_agreed_tweets_after_merging(list_of_annotated_tweets)

print 'Second merge of tags'
#second merge of tags
list_of_annotated_tweets = merge_annotations(list_of_annotated_tweets)
rewrite_segmentation(list_of_annotated_tweets)
list_of_tweets_done, list_of_tweets_for_editing = annotatedData_stat.numbers_of_agreed_tweets_after_merging(list_of_annotated_tweets)

write_to_file(list_of_tweets_for_editing, 'tweet_to_edit.csv')
write_to_file(list_of_tweets_done, 'done_tweet.csv')

