__author__ = 'snownettle'
import glob
import os
from mongoDB import importData
from general import read_file
from postgres import insert_to_table


def import_raw_twitter_data(directory_path, collection):
    for filename in glob.iglob(os.path.join(directory_path,'*.txt')):
            content = read_file.readTXT(filename)
            print filename + ' will be added to DB'
            importData.import_from_file(collection, content)
            print filename + ' is added to DB'


def import_to_postgres(directory_path):
    for filename in glob.iglob(os.path.join(directory_path, '*.txt')):
        tweets_tuple = ()
        tweet_list = list()
        print 'Inserting to postgres: ' + filename
        content = read_file.readTXT(filename)
        records = read_file.iterparse(content)
        for tweet in records:
            tweet_id = tweet['id']
            in_reply_to = tweet['in_reply_to_status_id']
            text = tweet['text']
            if in_reply_to is None:
                in_reply_to = 0
            if tweet_id not in tweet_list:
                current_tuple = (tweet_id, in_reply_to, text)
                help_tuple = (current_tuple,) + tweets_tuple
                tweets_tuple = help_tuple
            tweet_list.append(tweet_id)
        print 'start'
        insert_to_table.insert_raw_tweets(tweets_tuple)



