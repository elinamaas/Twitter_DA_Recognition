__author__ = 'snownettle'
# from __future__ import division
from mongoDB import mongoDBQueries
from tweet import Tweet
from mongoDB import mongoDB_configuration
from treelib import Tree
import sys
from general import check_lang
import nltk


class Conversation:
    def __init__(self, tweet):
        self.root_tweet = tweet
        self.conversation_tree = Tree()
        self.conversation_tree.create_node(tweet, tweet)
        self.depth = int()
        self.tweets_id = list()
        self.tweets_id.append(tweet)
        self.width = int()

    def add_replay(self, tweet, parent_tweet):
        self.conversation_tree.create_node(tweet, tweet, parent=parent_tweet)
        self.tweets_id.append(tweet)

    def set_depth(self):
        self.depth = self.conversation_tree.depth() + 1

    def find_depth(self):
        return self.depth

    def get_tweets_id(self):
        return self.tweets_id

    def set_width(self):
        self.width = len(self.tweets_id)

    def find_width(self):
        return self.width

    def get_conversation_tree(self):
        return self.conversation_tree


def build_conversation(collection):
    sys.setrecursionlimit(1500)
    root_tweets = mongoDBQueries.search_root_tweets(collection)
    conversations_list = list()
    tweets_list = set()
    test_list = set()
    count = 0
    number_of_root_tweets = root_tweets.count()
    for root_tweet in collection.find({'in_reply_to_status_id': None}).batch_size(500):
        count += 1
        tweet_id = root_tweet['id']
        tweet_id = int(tweet_id)
        if tweet_id in tweets_list:
            continue

        else:
            tweet_text = root_tweet['text']
            german = check_lang.check_german(tweet_text)
            if german is True:
                tweets_list.add(tweet_id)
                conversation = Conversation(tweet_id)
                find_replays(collection, tweet_id, tweets_list, conversation)
                conversation.set_depth()
                conversation.set_width()
                test_list.add(conversation.find_depth())
                conversations_list.append(conversation)

            if count % 10000 == 0:
                print('in progress...' + '%.2f' % (count*100/float(number_of_root_tweets)) + '%')
                # ############TEST###############
                # break
        # if count == 20000:
        #     return conversations_list

    print 'There are: ' + str(len(tweets_list)) + 'tweets'
    print 'There are: ' + str(len(conversations_list)) + ' conversations'
    print 'Check: ' + str(sum(test_list))
    print test_list
    return conversations_list


def find_replays(collection, tweet, tweets_list, conversation):
    replays = mongoDBQueries.search_replays(collection, tweet)
    if replays is not None:
        for replay in replays:
            tweet_text = replay['text']
            if check_lang.check_german(tweet_text) is True:
                tweet_id = replay['id']
                tweet_id = int(tweet_id)
                if tweet_id in tweets_list:
                    continue
                else:
                    new_tweet = tweet_id
                    tweets_list.add(new_tweet)

                    conversation.add_replay(new_tweet, tweet)
                    find_replays(collection, new_tweet, tweets_list, conversation)


# def check_lang(collection_conversation, collection_raw_data):
#     # conversations_list = collection_conversation.find().batch_size(500)
#     #     queries.find_all(collection_conversation) ##maybe batch size if too slow
#     for conversation in collection_conversation.find().batch_size(500):
#         root_tweet_id = conversation['root_tweet_id']
#         tweets = collection_raw_data.find({'id': root_tweet_id})
#             # queries.find_by_id(collection_raw_data, root_tweet_id)
#         for tweet in tweets:
#             tweet_text = tweet['text']
#
#             print tweet_text



# collectionRawData = mongoDB_configuration.get_collection('DARecognition', 'rawTwitterData')
# collectionConversationTree = mongoDB_configuration.get_collection('DARecognition', 'conversationTree')