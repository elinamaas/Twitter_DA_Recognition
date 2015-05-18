__author__ = 'snownettle'
from postgres import postgres_queries
from treelib import Tree


def build_conversation(parent_tweet, converastion_raw, conversation_tree):
    number_of_tweets = len(converastion_raw)
    i = 0
    while i < number_of_tweets:
        tweet = converastion_raw[i]
        if tweet[1] == parent_tweet:
            conversation_tree.create_node(tweet[0], tweet[0], parent=parent_tweet)
            build_conversation(tweet[0], converastion_raw, conversation_tree)
        i += 1


def build_conversation_lang(parent_tweet, converastion_raw, conversation_tree):
    number_of_tweets = len(converastion_raw)
    i = 0
    while i < number_of_tweets:
        tweet = converastion_raw[i]
        if tweet[1] == parent_tweet and tweet[5] is True:
            conversation_tree.create_node(tweet[0], tweet[0], parent=parent_tweet)
            build_conversation(tweet[0], converastion_raw, conversation_tree)
        i += 1


def conversation_regarding_language(): # with width and depth
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

    return new_tweet_list_id, conversation_list
