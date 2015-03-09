__author__ = 'snownettle'
# from __future__ import division
from twitter import conversation
from mongoDB import mongoDB_configuration


def number_of_conversation(conversation_list):
    return len(conversation_list)


def number_of_conversation_with_replays(conversation_list):
    conversation_with_replays = 0
    for discussion in conversation_list:
        depth = discussion.find_depth()
        if depth != 0:
            conversation_with_replays += 1
        else:
            continue
    print 'There are: ' + str(conversation_with_replays) + ' conversations with replays'


def depth_of_conversation(conversation_list):
    depth_dict = dict()
    for discussion in conversation_list:
        depth = discussion.find_depth()
        if depth in depth_dict:
            depth_dict[depth] += 1
        else:
            depth_dict[depth] = 1
    for conversation_depth, value in depth_dict.iteritems():
        print 'conversation depth:' + str(conversation_depth) + ' number of conversations: ' + str(value)


def longest_conversation(conversation_list):
    longest_depth = 0
    for discussion in conversation_list:
        if discussion.find_depth() > longest_depth:
            longest_depth = discussion.find_depth()
    print 'The longest conversation has depth: ' + str(longest_depth)

# print 'start'
# collectionRawTwitterData = mongoDB_configuration.get_collection('DARecognition', 'rawTwitterData')
# indexes = collectionRawTwitterData.index_information()
# print indexes
# collectionRawTwitterData.ensure_index('id')
# collectionRawTwitterData.ensure_index('in_reply_to_status_id')
# conversation_list = conversation.build_conversation(collectionRawTwitterData)
# number_of_conversation_with_replays(conversation_list)
# depth_of_conversation(conversation)
# longest_conversation(conversation_list)