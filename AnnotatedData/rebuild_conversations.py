__author__ = 'snownettle'
import glob
import os
from general import read_file
from postgres import insert_to_table


def build_conversations_annotated(filename):
    tweets_tuple = ()
    tweet_list = list()
    content = read_file.readTXT(filename)
    for tweet in read_file.iterparse(content):
        tweet_id = tweet['id']
        in_reply_to = tweet['in_reply_to_status_id']
        if in_reply_to is None:
            in_reply_to = 0
        if tweet_id not in tweet_list:
            current_tuple = (tweet_id, in_reply_to)
            help_tuple = (current_tuple,) + tweets_tuple
            tweets_tuple = help_tuple
        tweet_list.append(tweet_id)
    insert_to_table.insert_annotated_conversations(tweets_tuple)
    # return tweets_tuple


def insert_tweets(filename):
    tweets_tuple = ()
    tweet_list = list()
    content = read_file.readTXT(filename)
    for tweet in read_file.iterparse(content):
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
    insert_to_table.insert_raw_tweets(tweets_tuple)
    # return tweets_tuple

# tweets = insert_tweets('../DATA/annotated_tweets_raw.txt')

# tweets = build_conversations_annotated('../DATA/annotated_tweets_raw.txt')
# insert_to_table.insert_annotated_conversations(tweets)
