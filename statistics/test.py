__author__ = 'snownettle'
from postgres import postgres_queries
from treelib import Tree


def types_of_conversation():
    conversation_amount = postgres_queries.find_annotated_conversation_number()
    conversation_list = list()
    depth_dict = dict()
    number_of_tweets_dict = dict()
    for i in range (1, conversation_amount +1, 1):
        conversation_tree = Tree()
        converastion = postgres_queries.find_conversation(i)
        for tweet in converastion:
            if tweet[1] is None:
                conversation_tree.create_node(tweet[0], tweet[0])
                build_conversation(tweet[0], converastion, conversation_tree)
                depth = conversation_tree.depth() + 1
                number_of_tweets = len(conversation_tree.all_nodes())
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


# def conversation_length(conversation_list):
#     depth_dict = dict()
#     i = 0
#     for conversation in conversation_list:
#         depth = conversation.depth()
#         # if depth == 0:
#         #     print 'here'
#         # if depth == 1:
#         #     print 'here'
#         if depth in depth_dict:
#             depth_dict[depth] += 1
#         else:
#             depth_dict[depth] = 1
#         i += 1
#     print depth_dict

conversation_list = types_of_conversation()
# conversation_length(conversation_list)
