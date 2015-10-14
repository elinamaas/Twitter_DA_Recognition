__author__ = 'snownettle'
import glob
import os
from postgres import postgres_queries
from postgres import insert_to_table
import csv
import re
from general import check_lang
from collections import defaultdict


def insert_annotated_tweets_postgres(directory_path):
    conversation_number = 0
    tweets_list = set()
    tweets_tuple = ()
    previous_rows = list()
    added_tweets = insert_to_table.select_all_tweets()
    last_added_conversation_number = -1
    for directory_name in glob.iglob(os.path.join(directory_path,'*.*')):
        for filename in glob.iglob(os.path.join(directory_name, '*.tsv')):
            with open(filename) as f:
                content = csv.reader(f, delimiter='\t')
                previous_rows = list()
                for row in content:
                    if len(row) != 0:
                        if '#text=New Thread' in row[0]:
                            if last_added_conversation_number == conversation_number:
                                conversation_number += 1
                            else:
                                conversation_number = last_added_conversation_number + 1
                            # previous_rows.append(row)
                        if '#text=' in row[0] and 'id=' in row[0]:
                            previous_rows.append(row)
                            tweet_id = re.split('id=', row[0])[1]
                            tweet_id = re.split(' user', tweet_id)[0]
                            if tweet_id not in tweets_list and tweet_id not in added_tweets:
                                text_id = re.split('#text=', row[0])[1]
                                text_id = int(re.split('id=', text_id)[0])
                                text = re.split('user=', row[0])[1]
                                text = text.partition(' ')[2]
                                if text != '':
                                    in_replay_to = find_in_replay_to(previous_rows, tweet_id, text_id)
                                    german_language = check_lang.check_german(text)
                                    if german_language is True:
                                        tweet_tuple = (tweet_id, in_replay_to, conversation_number, text, True, True)
                                    if german_language is False:
                                        tweet_tuple = (tweet_id, in_replay_to, conversation_number, text, True, False)
                                    if len(tweets_tuple) == 0:
                                        tweets_tuple = (tweet_tuple, )
                                        last_added_conversation_number =conversation_number
                                    else:
                                        tweets_tuple = (tweet_tuple, ) + tweets_tuple
                                        last_added_conversation_number =conversation_number
                                    tweets_list.add(tweet_id)

    if len(tweets_tuple) != 0:
        insert_to_table.insert_raw_tweets(tweets_tuple)
        print 'There are ' + str(conversation_number) + ' annotated conversations'
    else:
        #number of annotated conversation
        conversation_number = postgres_queries.find_conversation_number()
        print 'There are ' + str(conversation_number) + ' annotated conversations'
    # return tweets_tuple


def find_in_replay_to(previous_rows, tweet_id, text_id):
    in_replay_to = None
    if text_id == 0:
        return in_replay_to
    else:
        previous_text_id = '#text=' + str(text_id-1)
        for i in range(len(previous_rows)-1, -1, -1):
            previous_text = previous_rows[i][0]
            if previous_text_id in previous_text:
                in_replay_to = re.split('id=', previous_rows[i][0])[1]
                in_replay_to = re.split(' user', in_replay_to)[0]
                return in_replay_to



# def build_conversation_tree(): # attention language
#     conversations_list = postgres_queries.find_conversations()
#     for conversation in conversations_list:
#         print conversation

# build_conversation_tree()
# tweets = insert_tweets('../DATA/annotated_tweets_raw.txt')

# tweets = build_conversations_annotated('../DATA/annotated_tweets_raw.txt')
# insert_to_table.insert_annotated_conversations(tweets)
