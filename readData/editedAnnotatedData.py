__author__ = 'snownettle'
from general import read_file
import csv
from twitter_objects.tweet import AnnotatedTweetFinal
from postgres import insert_to_table
import xlrd


def import_golden_standard_postgres(filename, cursor, connection):
    list_of_tweets_to_be_inserted = list()
    tweets_id = set()
    workbook = xlrd.open_workbook(filename)
    worksheet = workbook.sheet_by_name('Sheet1')
    num_rows = worksheet.nrows - 1
    curr_row = -1
    while curr_row < num_rows:
        curr_row += 1
        cell_value = worksheet.cell_value(curr_row, 0)
        if 'offset' == cell_value:
            continue
        elif '#tweet' in cell_value:
            tweet_id = cell_value.split('#tweet_id=')[1].split('#')[0]
            in_replay_to = cell_value.split('#in_replay_to=')[1].split('#')[0]
            username = cell_value.split('#user=')[1].split('#')[0]
            tweet_text = cell_value.split('#tweet_text=')[1]
            # text_id = row[0].split('#text_id=')[1].split('#')[0]
            tweet = AnnotatedTweetFinal(tweet_id, tweet_text, in_replay_to, conversation_id, username)
        elif 'conversation_id' in cell_value:
             conversation_id = cell_value.split('conversation_id=')[1]
        elif cell_value == '':
            tweet.set_segments()
            if tweet_id not in tweets_id:
                tweets_id.add(tweet_id)
                # insert_to_table.insert_annotated_tweet(tweet)
                list_of_tweets_to_be_inserted.append(tweet)
        else:
            offset = worksheet.cell_value(curr_row, 0)
            token = worksheet.cell_value(curr_row, 1)
            da = worksheet.cell_value(curr_row, 2)
            tweet.set_tokens(offset, token, da)
    insert_to_table.multiple_tweets_insert(list_of_tweets_to_be_inserted, cursor, connection)
    return list_of_tweets_to_be_inserted
