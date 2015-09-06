__author__ = 'snownettle'
# Crawling tweets for annotated data, put in the DB.

from mongoDB import mongoDBQueries
from mongoDB import mongoDB_configuration
import json
import tweepy
import time
from general import read_file


def get_all_ids(collection):
    records = mongoDBQueries.find_all(collection)
    tweet_id_list = set()
    for record in records:
        tweet_id = record['tweet_id']
        tweet_id = int(tweet_id)
        if tweet_id in tweet_id_list:
            continue
        else:
            tweet_id_list.add(tweet_id)
    return tweet_id_list


def check_crawled(data):
    tweet_id_list = set()
    if data is not None:
        for record in read_file.iterparse(data):
            tweet_id = record['id']
            tweet_id = int(tweet_id)
            tweet_id_list.add(tweet_id)
    return tweet_id_list


def crawling(collection, crawled_tweets):
    tweet_id_list = get_all_ids(collection)
    new_tweet_list = [x for x in tweet_id_list if x not in crawled_tweets]
    # create authentication handlers given pre-existing keys
    consumer_key = 'NWggz4ewmIuZNRPS7FWmkbHxO'
    consumer_secret = 'Qa5pa9UaJKPJ6ZDpSQhh250RvUaDJTlHXlOHOC4pWBawvvvffU'
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token('', '')
    api = tweepy.API(auth, retry_count=3, retry_delay=5, retry_errors=set([401, 404, 500, 503]),
                     parser=tweepy.parsers.JSONParser())
    with open("../DATA/annotated_tweets_raw.txt", "a") as outfile:
        for tweet_id in new_tweet_list:
            try:
                data = api.get_status(tweet_id)
                json.dump(data, outfile)
                outfile.write('\n')

                print data
            except tweepy.TweepError:
                print 'sleeping...'
                time.sleep(60 * 15)
                continue


