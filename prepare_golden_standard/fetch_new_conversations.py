__author__ = 'snownettle'
# for another one student prepare conversation trees.
# Write in Excel file.
# He will annotate them.

from twitter_objects import conversation
from mongoDB import mongoDB_configuration, mongoDBQueries
import xlsxwriter
from da_recognition import dialogue_acts_taxonomy


def build_conversation():
    # collection_conversation_tree = mongoDB_configuration.get_collection('DARecognition', 'conversationTree')
    collection_raw = mongoDB_configuration.get_collection('DARecognition', 'rawTwitterData')
    conversation_trees = conversation.build_conversation(collection_raw)
    short = 0
    short_list = list()
    long_name = 0
    long_list = list()
    for twitter_conversation in conversation_trees:
        if short > 200 and long_name > 100:
            break
        if short < 201:
            if 3 < twitter_conversation.find_width() < 6:
                short += 1
                short_list.append(twitter_conversation)
        if long_name < 101:
            if twitter_conversation.find_depth() > 4:
                print twitter_conversation.find_width()
                if twitter_conversation.find_width() > 15:
                    long_name += 1
                    long_list.append(twitter_conversation)
    print 'short ', short
    print 'long ', long_name
    return short_list, long_list


def write_to_file(conversation_list, file_name):
    collection_raw = mongoDB_configuration.get_collection('DARecognition', 'rawTwitterData')

    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()
    row = 1
    col = 0
    worksheet.write(0, 0, 'offset')
    worksheet.write(0, 1, 'token')
    worksheet.write(0, 2, 'dialogue act')
    thread = 0
    for conversation in conversation_list:
        thread += 1
        new_thread = 'New thread=' + str(thread) + ' , depth= ' + str(conversation.find_depth()) +\
                     ' , width= ' + str(conversation.find_width())
        worksheet.write(row, col, new_thread)
        row += 2
        conversation_tree = conversation.get_conversation_tree()
        root_tweet = conversation_tree.root
        tweet = mongoDBQueries.find_by_id_raw(collection_raw, root_tweet)
        list_of_tweets = list()
        list_of_tweets.append(tweet)
        find_children(collection_raw, conversation_tree, tweet, list_of_tweets)
        text_id = 0
        text_id_dict = dict()
        for tweet in list_of_tweets:

            text = tweet['text']
            if tweet['in_reply_to_status_id'] is None:
                text_id_dict[tweet['id']] = text_id
            else:
                text_id = text_id_dict[tweet['in_reply_to_status_id']] + 1
                text_id_dict[tweet['id']] = text_id
            tweet_text_line = '#text= ' + str(text_id) + ' #tweet_id=' + str(tweet['id']) +\
                              ' #in_reply_to=' + str(tweet['in_reply_to_status_id']) + '#text= ' + text
            worksheet.write(row, col, tweet_text_line)
            row += 1
            tokens = text.split(' ')
            i = 4
            for token in tokens:
                worksheet.write(row, col, str(i))
                worksheet.write(row, col+1, token)
                row += 1
                i += 1
            row += 1
    taxonomy = dialogue_acts_taxonomy.build_da_taxonomy_full()
    da_labels = taxonomy.all_nodes()
    row = 1
    col = 20
    root_label = taxonomy.root
    top_labels = taxonomy.all_nodes()
    for label in top_labels:
        worksheet.write(row, col, label.tag)
        row += 1

    workbook.close()
#
#
# def write_da_in_new_column(labels, row, col, worksheet):
#     for da_label in labels:
#         worksheet.write(row, col, da_label.tag)
#         row += 1
#
#
# def find_next_level(labels, row, col, worksheet, taxonomy):
#     # next_level = None
#     for label in labels:
#         next_level = taxonomy.children(label.tag)
#         write_da_in_new_column(next_level, row, col, worksheet)
#         col += 1
#     for label in labels:
#         next_level = taxonomy.children(label.tag)
#         find_next_level(next_level, row, col, worksheet, taxonomy)
#         col += 1
#     col +=1


def find_children(collection, conversation_tree, parent_tweet, list_of_tweets):
    tweet_id = parent_tweet['id']
    children = conversation_tree.children(tweet_id)
    for child in children:
        tweet_id = child.tag
        tweet = mongoDBQueries.find_by_id_raw(collection, tweet_id)
        list_of_tweets.append(tweet)
        find_children(collection, conversation_tree, tweet, list_of_tweets)







# def build_conversation_tree()
short, long = build_conversation()
# conversation_list = short + long
file_name = '../output/short_conversations.xls'
write_to_file(short, file_name)
file_name = '../output/long_conversations.xls'
write_to_file(long, file_name)