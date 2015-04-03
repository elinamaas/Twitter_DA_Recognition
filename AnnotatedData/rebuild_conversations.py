__author__ = 'snownettle'
import glob
import os
from general import read_file
from postgres import insert_to_table
import csv
import re
from collections import defaultdict


def insert_annotated_tweets_postgres(directory_path):
    conversation_number = 0
    tweets_list = set()
    tweets_tuple = ()
    previous_rows = list()
    added_tweets = insert_to_table.select_all_tweets()
    for directory_name in glob.iglob(os.path.join(directory_path,'*.*')):
        for filename in glob.iglob(os.path.join(directory_name, '*.tsv')):
            with open(filename) as f:
                content = csv.reader(f, delimiter='\t')
                previous_rows = list()
                for row in content:
                    if len(row) != 0:
                        if '#text=New Thread' in row[0]:
                            conversation_number += 1
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
                                    tweet_tuple = (tweet_id, in_replay_to, conversation_number, text, True)
                                    if len(tweets_tuple) == 0:
                                        tweets_tuple = (tweet_tuple, )
                                    else:
                                        tweets_tuple = (tweet_tuple, ) + tweets_tuple
                                    tweets_list.add(tweet_id)

    insert_to_table.insert_raw_tweets(tweets_tuple)
    print 'There are ' + str(conversation_number) + ' annotated conversations'
    return tweets_tuple


def find_in_replay_to(previous_rows, tweet_id, text_id):
    in_replay_to = 0
    if text_id == 0:
        return in_replay_to
    else:
        for i in range(0, len(previous_rows), 1):
            previous_text_id = '#text=' + str(text_id-1)
            if previous_text_id in previous_rows[i][0]:
                if tweet_id in previous_rows[i+1][0]:
                    in_replay_to = re.split('id=', previous_rows[i][0])[1]
                    in_replay_to = re.split(' user', in_replay_to)[0]
                    return in_replay_to


# tweets = insert_tweets('../DATA/annotated_tweets_raw.txt')

# tweets = build_conversations_annotated('../DATA/annotated_tweets_raw.txt')
# insert_to_table.insert_annotated_conversations(tweets)
