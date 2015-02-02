__author__ = 'snownettle'
# get first document form the collection
import conDB
import json
from tweet import Tweet


def search_first_tweet(db_name, collection_name):
    tweets_collection = conDB.get_collection(db_name, collection_name)
    tweet = tweets_collection.find_one()
    print tweet


def check_lang(tweets_collection):
    print tweets_collection.find({'lang':'de'}).count()
    print tweets_collection.find({'lang':'en'}).count()


def build_conversation(collection):
    conversation_list = []
    root_tweets = collection.find({'in_reply_to_status_id': None})
    #print 'root_tweets: ', root_tweets.count()
    for root_tweet in root_tweets:
        tweet = Tweet(root_tweet['id'])
        tweet = search_replays(tweet, collection)
        conversation_list.append(tweet)
    return conversation_list


def search_replays(tweet, collection):
    replays = collection.find({'in_reply_to_status_id': tweet.get_id()})
    print 'replays: ', replays.count()
    if replays is None:
        return tweet
    else:
        for replay in replays:
            tweet_replay = Tweet(replay['id'])
            tweet.set_replay(tweet_replay)
            tweet_replay = search_replays(tweet_replay, collection)
        return tweet


def find_all(collection):
    return collection.find()


def find_by_id(collection, record):
    return collection.find({'tweet_id': record['tweet_id']})

# def search_root_tweets(raw_tweets_collection):
#     return raw_tweets_collection.find({'in_reply_to_status_id': None})
#
#
# def build_conversation_for_roots(raw_tweets_collection, root_tweets, conversation_list):
#     for tweet in root_tweets:
#         conversation = Tweet(tweet['id'])
#         # add root tweet to json object
#         build_conversations(raw_tweets_collection, tweet, conversation)
#
#
#
# def build_conversations(raw_tweets_collection, tweet, conversation): #from root tweets
#     #list_of_replays =[]
#     replays = search_replays(raw_tweets_collection, tweet['id'])
#     if replays is None:
#         return conversation
#     else:
#         for replay in replays:
#             tweet = Tweet(replay)
#             conversation.set_replay(tweet)
#             # add to json object as replay
#             build_conversations(raw_tweets_collection, replay)
#
#
# def search_tweet_by_id(collection, tweet_id):
#     collection.find({'id': tweet_id})
#
#
# def search_replays(collection, tweet_id):
#     replays = collection.find({'in_reply_to_status_id': tweet_id})
#     if replays.count() != 0:
#         return replays
#     else:
#         return None
#
#
# def search_replays_to_replay(collection, tweet_id):
#     replays_to_replay = collection.find({'in_reply_to_status_id': tweet_id})
#     if replays_to_replay.count() != 0:
#         return replays_to_replay
#     else:
#         return None