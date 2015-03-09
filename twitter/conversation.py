__author__ = 'snownettle'
# from __future__ import division
from mongoDB import queries
from tweet import Tweet
from mongoDB import mongoDB_configuration
from treelib import Tree


class Conversation:
    def __init__(self, tweet):
        self.root_tweet = tweet
        self.conversation_tree = Tree()
        self.conversation_tree.create_node(tweet, tweet)
        self.depth = int()

    def add_replay(self, tweet, parent_tweet):
        self.conversation_tree.create_node(tweet, tweet, parent=parent_tweet)
        return self

    def set_depth(self):
        self.depth = self.conversation_tree.depth()

    def find_depth(self):
        return self.depth


def build_conversation(collection):
    root_tweets = queries.search_root_tweets(collection)
    conversations_list = list()
    tweets_list = set()
    test_list = list()
    count = 0
    ids_list = list()
    number_of_root_tweets = root_tweets.count()
    for root_tweet in root_tweets:
        count += 1
        tweet_id = root_tweet['id']
        if tweet_id in ids_list:
            continue
        # tweet = root_tweet['id']
        # if tweet in tweets_list:
        #     print 'duplicate'
        #     continue

        else:
            ids_list.append(tweet_id)
            tweet = Tweet(tweet_id)
            tweets_list.add(tweet)
            conversation = Conversation(tweet)
            find_replays(collection, tweet, tweets_list, conversation, ids_list)
            # if len(replays_list) != 0:
            #     for replay in replays_list:
            # conversation.add_replay(replay, tweet)
            conversation.set_depth()
            test_list.append(conversation.find_depth())
            conversations_list.append(conversation)
            if count % 10000 == 0:
                print('in progress...' + '%.2f' % (count*100/float(number_of_root_tweets)) + '%')

    print 'There are: ' + str(len(tweets_list)) + 'tweets'
    print 'There are: ' + str(len(conversations_list)) + ' conversations'
    indices = [i for i, x in enumerate(test_list) if x == 0]
    print 'Check: ' + str(sum(test_list))
    # print len(indices)
    return conversations_list


def find_replays(collection, tweet, tweets_list, conversation, ids_list):
    replays = queries.search_replays(collection, tweet.get_tweet_id())
    # replays_list = set()
    if replays is not None:
        for replay in replays:
            tweet_id = replay['id']
            if tweet_id in ids_list:
                continue
            # if new_tweet in tweets_list:
            #     print 'duplicate'
            #     continue

            else:
                ids_list.append(tweet_id)
                new_tweet = Tweet(tweet_id)
                tweets_list.add(new_tweet)
                # tweet.add_replay(new_tweet)
                # replays_list.add(new_tweet)
                conversation = conversation.add_replay(new_tweet, tweet)
                find_replays(collection, new_tweet, tweets_list, conversation, ids_list)
                # return replays_list
