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
        self.tweets_id = list()
        self.tweets_id.append(tweet)

    def add_replay(self, tweet, parent_tweet):
        self.conversation_tree.create_node(tweet, tweet, parent=parent_tweet)
        self.tweets_id.append(tweet)

    def set_depth(self):
        self.depth = self.conversation_tree.depth()

    def find_depth(self):
        return self.depth

    def get_tweets_id(self):
        return self.tweets_id


def build_conversation(collection):
    root_tweets = queries.search_root_tweets(collection)
    conversations_list = list()
    tweets_list = set()
    test_list = list()
    count = 0
    # ids_list = list()
    number_of_root_tweets = root_tweets.count()
    for root_tweet in collection.find({'in_reply_to_status_id': None}).batch_size(500):
        count += 1
        tweet_id = root_tweet['id']
        if tweet_id in tweets_list:
            continue
        # tweet = root_tweet['id']
        # if tweet in tweets_list:
        #     print 'duplicate'
        #     continue

        else:
            # ids_list.append(tweet_id)
            # tweet = Tweet(tweet_id)
            tweets_list.add(tweet_id)
            conversation = Conversation(tweet_id)
            find_replays(collection, tweet_id, tweets_list, conversation)
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


def find_replays(collection, tweet, tweets_list, conversation):
    replays = queries.search_replays(collection, tweet)
    # replays_list = set()
    if replays is not None:
        for replay in replays:
            tweet_id = replay['id']
            if tweet_id in tweets_list:
                continue
            # if new_tweet in tweets_list:
            #     print 'duplicate'
            #     continue

            else:
                # ids_list.append(tweet_id)
                new_tweet = tweet_id
                tweets_list.add(new_tweet)
                # tweet.add_replay(new_tweet)
                # replays_list.add(new_tweet)
                conversation.add_replay(new_tweet, tweet)
                find_replays(collection, new_tweet, tweets_list, conversation)
                # return replays_list


def build_conversation2(collection):
    collection.ensure_index([('created_at', 11)])
    records = queries.find_all(collection)
    #records.sort('created_at', 1)
    tweets_list = list()
    conversations_list = list()
    root_tweets = list()
    added = False
    i = records.count()
    count = 0
    conversation_dictionary = dict()
    for record in records:
        count += 1
        if count % 10000 == 0:
                print('in progress...' + '%.2f' % (count*100/float(i)) + '%')
        tweet_id = record['id']
        in_replay_to = record['in_reply_to_status_id']
        if tweet_id in tweets_list:
            continue
        if in_replay_to is None:
            # if tweet_id not in root_tweets:
            root_tweets.append(tweet_id)
            conversation = Conversation(tweet_id)
            conversations_list.append(conversation)
            tweets_list.append(tweet_id)
            conversation_dictionary[tweet_id] = conversation

        else:
            # if in_replay_to in tweets_list:
            try:
            # if in_replay_to in conversation_dictionary:
                conversation = conversation_dictionary[in_replay_to]
                conversation.add_replay(tweet_id, in_replay_to)
                tweets_list.append(tweet_id)
                conversation_dictionary[tweet_id] = conversation
                # for discussion in conversations_list:
                #     if in_replay_to in discussion.get_tweets_id():
                #         discussion.add_replay(tweet_id, in_replay_to)
                #         tweets_list.append(tweet_id)
            except KeyError:
                conversation = Conversation(in_replay_to)
                conversation.add_replay(tweet_id, in_replay_to)
                conversations_list.append(conversation)
                tweets_list.append(tweet_id)
                conversation_dictionary[tweet_id] = conversation

    for con in conversations_list:
        con.set_depth()
    return conversations_list





