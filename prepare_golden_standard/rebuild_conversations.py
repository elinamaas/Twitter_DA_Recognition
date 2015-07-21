__author__ = 'snownettle'
from postgres import postgres_queries
from treelib import Tree
from mongoDB import mongoDBQueries


def conversation_list_regarding_language():
    twitter_id, conversation_list = conversation_regarding_language()
    return conversation_list


def build_conversation_tree(parent_tweet, converasation_raw, conversation_tree):
    number_of_tweets = len(converasation_raw)
    i = 0
    while i < number_of_tweets:
        tweet = converasation_raw[i]
        if tweet[1] == parent_tweet:
            conversation_tree.create_node(tweet[0], tweet[0], parent=parent_tweet)
            build_conversation_tree(tweet[0], converasation_raw, conversation_tree)
        i += 1


def build_conversation_lang(parent_tweet, converasation_raw, conversation_tree):
    number_of_tweets = len(converasation_raw)
    i = 0
    while i < number_of_tweets:
        tweet = converasation_raw[i]
        if tweet[1] == parent_tweet and tweet[5] is True:
            conversation_tree.create_node(tweet[0], tweet[0], parent=parent_tweet)
            build_conversation_tree(tweet[0], converasation_raw, conversation_tree)
        i += 1

#rebuilf conversation, take in account german tweets,with width and depth
def conversation_regarding_language():
    conversation_amount = postgres_queries.find_annotated_conversation_number()
    conversation_list = list()
    depth_dict = dict()
    depth_dict_long = dict()
    depth_dict_short = dict()
    number_of_tweets_dict = dict()
    test_i = 0
    for i in range(0, conversation_amount + 1, 1):
        conversation_tree = Tree()
        converastion = postgres_queries.find_conversation(i)
        test_i += len(converastion)
        for tweet in converastion:
            if tweet[1] is None and tweet[5] is True:
                conversation_tree.create_node(tweet[0], tweet[0])
                build_conversation_lang(tweet[0], converastion, conversation_tree)
                depth = conversation_tree.depth() + 1
                number_of_tweets = len(conversation_tree.all_nodes())
                #short/long
                if number_of_tweets >=20:
                    if depth in depth_dict_long:
                        depth_dict_long[depth] += 1
                    else:
                        depth_dict_long[depth] = 1
                else:
                    if depth in depth_dict_short:
                        depth_dict_short[depth] += 1
                    else:
                        depth_dict_short[depth] = 1

                if number_of_tweets in number_of_tweets_dict:
                    number_of_tweets_dict[number_of_tweets] += 1
                else:
                     number_of_tweets_dict[number_of_tweets] = 1
                if depth in depth_dict:
                    depth_dict[depth] += 1
                else:
                    depth_dict[depth] = 1
        conversation_list.append(conversation_tree)
    number = 0
    new_tweet_list_id = list()
    for con in conversation_list:
        nodes = con.all_nodes()
        for node in nodes:
            new_tweet_list_id.append(node.tag)
        number += len(con.all_nodes())
    # print len(new_tweet_list_id)
    # for tweet_id in new_tweet_list_id:
    #     print tweet_id
    return new_tweet_list_id, conversation_list


def delete_non_german_tweets_from_conversation(old_tweets, tweet_german):
    new_list_tweet_only_german = list()
    for tweet in old_tweets:
        tweet_id = long(tweet.get_tweet_id())
        if tweet_id in tweet_german:
            new_list_tweet_only_german.append(tweet)
    return new_list_tweet_only_german


def build_conversation_from_mongo(collection_name):
    tweet_ids_list = list()
    conversation_list = list()
    records = mongoDBQueries.find_all_conversation_id(collection_name)
    for conversation_id in records:
        conversation_tree = Tree()
        help_dictionary = dict()
        conversation_id = int(conversation_id)
        tweets = mongoDBQueries.find_by_conversation_id(collection_name, conversation_id)
        for tweet in tweets:
            tweet_id = str(tweet['tweet_id']).replace(' ', '')
            if tweet_id not in tweet_ids_list:
                tweet_ids_list.append(tweet_id)
                text_id = tweet['text_id']
                if text_id == 0:
                    conversation_tree.create_node(tweet_id, tweet_id)
                    help_dictionary[text_id] = tweet_id
                else:
                    # text_id = tweet['text_id']
                    parent_tweet = help_dictionary[text_id-1]
                    help_dictionary[text_id] = tweet_id
                    conversation_tree.create_node(tweet_id, tweet_id, parent=parent_tweet)
        conversation_list.append(conversation_tree)
    return conversation_list


# conversation_regarding_language()