__author__ = 'snownettle'
from general import read_file
import csv
from twitter_objects.tweet import AnnotatedTweetFinal
from postgres import insert_to_table
import xlrd

def import_golden_standard_postgres(filename):
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
            tweet_text = cell_value.split('#tweet_text=')[1]
            # text_id = row[0].split('#text_id=')[1].split('#')[0]
            tweet = AnnotatedTweetFinal(tweet_id, tweet_text, in_replay_to, conversation_id)
        elif 'conversation_id' in cell_value:
             conversation_id = cell_value.split('conversation_id=')[1]
        elif cell_value == '':
            tweet.set_segments()
            if tweet_id not in tweets_id:
                tweets_id.add(tweet_id)
                insert_to_table.insert_annotated_tweet(tweet)
        else:
            offset = worksheet.cell_value(curr_row, 0)
            token = worksheet.cell_value(curr_row, 1)
            da = worksheet.cell_value(curr_row, 2)
            tweet.set_tokens(offset, token, da)

# import_golden_standard_postgres('../tokenisierung-tofix.xlsx')
# test = 'jfjudj\''
# print test
# print test.replace('\'', '\'\'')