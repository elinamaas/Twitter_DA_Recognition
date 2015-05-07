__author__ = 'snownettle'
from postgres import postgres_queries
from treelib import Tree


def types_of_conversation():
    conversation_amount = postgres_queries.find_annotated_conversation_number()
    conversation_list = list()
    depth_dict = dict()
    depth_dict_long = dict()
    depth_dict_short = dict()
    number_of_tweets_dict = dict()
    for i in range (0, conversation_amount + 1, 1):
        conversation_tree = Tree()
        converastion = postgres_queries.find_conversation(i)
        for tweet in converastion:
            if tweet[1] is None:
                conversation_tree.create_node(tweet[0], tweet[0])
                build_conversation(tweet[0], converastion, conversation_tree)
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
    #print depth_dict
    print 'Depth of a conversation'
    for depth, count in depth_dict.iteritems():
        print depth, '\t', count
    print 'Number of tweets in a conversation'
    for number, count in number_of_tweets_dict.iteritems():
        print number, '\t', count
    print 'Depth of a long conversation'
    for depth, count in depth_dict_long.iteritems():
        print depth, '\t', count
    print 'Depth of a short conversation'
    for depth, count in depth_dict_short.iteritems():
        print depth, '\t', count

    return conversation_list


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
    #print depth_dict
    number = 0
    new_tweet_list_id = list()
    for con in conversation_list:
        nodes = con.all_nodes()
        for node in nodes:
            new_tweet_list_id.append(node.tag)
        number += len(con.all_nodes())
    # print 'Depth of a conversation'
    # for depth, count in depth_dict.iteritems():
    #     print depth, '\t', count
    # print 'Number of tweets in a conversation'
    # for number, count in number_of_tweets_dict.iteritems():
    #     print number, '\t', count
    # print 'Depth of a long conversation'
    # for depth, count in depth_dict_long.iteritems():
    #     print depth, '\t', count
    # print 'Depth of a short conversation'
    # for depth, count in depth_dict_short.iteritems():
    #     print depth, '\t', count

    return new_tweet_list_id


def make_new_list(old_tweets, tweet_german):
    new_list_tweet_only_german = list()
    for tweet in old_tweets:
        tweet_id = long(tweet.get_tweet_id())
        if tweet_id in tweet_german:
            new_list_tweet_only_german.append(tweet)
    return new_list_tweet_only_german

# conversation_list = types_of_conversation()
# conversation_length(conversation_list)
# conversation_regarding_language()

list_of_tweets = conversation_regarding_language()
da_instatnses = 0
segments_count = dict()
for tweet_id in list_of_tweets:
    results = postgres_queries.find_segments(tweet_id)
    da_instatnses += len(results)
    if len(results) == 0:
        print 'uu'
    if len(results) in segments_count:
        segments_count[len(results)] += 1
    else:
        segments_count[len(results)] = 1
print da_instatnses
for segment, count in segments_count.iteritems():
    print segment, '\t', count
