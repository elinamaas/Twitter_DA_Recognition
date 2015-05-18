__author__ = 'snownettle'
import glob
import os
import csv
import xlrd
import re
from prepare_golden_standard import annotated_tweet_class, write_to
from postgres import insert_to_table
from mongoDB import importData
from statistics import annotatedData_stat


#read original annotated data, import to mongoDB
def read_annotated_docs(directory_path, collection_annotated_data):
    conversation_id = 0
    data = {}
    id = 1
    previous_tag = ''
    tag = ''
    for directory_name in glob.iglob(os.path.join(directory_path,'*.*')):
        for filename in glob.iglob(os.path.join(directory_name, '*.tsv')):
            with open(filename) as f:
                content = csv.reader(f, delimiter='\t')
                previous_row = ' '
                for row in content:
                    if len(row) is 0:
                        if conversation_id is not '1':
                            data['id'] = id
                            id += 1
                            importData.import_record(data, collection_annotated_data)
                        else:
                            continue
                    else:
                        if check_if_new_thread(row) is True:
                            conversation_id = '1'
                        if '#id' in row[0]:
                            conversation_id = re.split('id=', row[0])[1]
                            data = {}
                            data['conversation_id'] =conversation_id
                        elif check_if_consistent(row) is False:
                            conversation_id = '1'
                        elif conversation_id == '1':
                            continue
                        elif len(previous_row) is not 0 and '#id' in previous_row[0]:
                            tweet_id = re.split('id=', row[0])[1]
                            tweet_id = re.split(' user', tweet_id)[0]
                            data['tweet_id'] = tweet_id
                            data['text'] = row[0]
                            text_id = re.split('#text=', row[0])[1]
                            text_id = re.split('id=', text_id)[0]
                            data['text_id'] = text_id
                        elif conversation_id == re.split('-', row[0])[0]  \
                                and re.split('-', row[0])[1] not in ['1', '2', '3'] and len(row) > 3:
                            token = row[1]
                            if '@' in token:
                                if row[0].split('-')[1] == '4':
                                    tag = '0'
                                elif '@' in previous_row[1] and previous_tag == '0':
                                    tag = '0'
                                else:
                                    tag = splitting_tag(row, previous_tag)
                                    # if row[2] == 'O' or row[2] == '0':
                                    #     tag = '0'
                                    # else:
                                    #     if previous_tag == '0':
                                    #         tag = ''
                                    #         if '|' in row[2]:
                                    #             new_tags = re.split('|', row[2])
                                    #             for new_tag in new_tags:
                                    #                 if tag == '':
                                    #                     tag += 'B-' + re.split('-', new_tag)[1]
                                    #                 else:
                                    #                     tag += '|' + 'B-' + re.split('-', new_tag)[1]
                                    #         else:
                                    #             tag = 'B-' + re.split('-', row[2])[1]
                                    #     else:
                                    #         tag = row[2]
                            else:
                                tag = splitting_tag(row, previous_tag)
                                # if row[2] == 'O' or row[2] == '0':
                                #     tag = '0'
                                # else:
                                #     if previous_tag == '0':
                                #         tag = ''
                                #         if '|' in row[2]:
                                #             new_tags = row[2].split('|')
                                #             for new_tag in new_tags:
                                #                 if tag == '':
                                #                     tag += 'B-' + re.split('-', new_tag)[1]
                                #                 else:
                                #                     tag += '|' + 'B-' + re.split('-', new_tag)[1]
                                #         else:
                                #             tag = 'B-' + re.split('-', row[2])[1]
                                #     else:
                                #         tag = row[2]
                            data[re.split('-', row[0])[1]] = [token, tag]
                            previous_tag = tag
                        elif len(row) < 3:
                            conversation_id = 1
                    previous_row = row


def splitting_tag(row, previous_tag):
    if row[2] == 'O' or row[2] == '0':
        tag = '0'
    else:
        if previous_tag == '0':
            tag = ''
            if '|' in row[2]:
                new_tags = row[2].split('|')
                for new_tag in new_tags:
                    if tag == '':
                        tag += 'B-' + re.split('-', new_tag)[1]
                    else:
                        tag += '|' + 'B-' + re.split('-', new_tag)[1]
            else:
                tag = 'B-' + re.split('-', row[2])[1]
        else:
            tag = row[2]
    return tag

def check_if_new_thread(row):
    if 'webanno.custom.DialogActs' in row[0] or '#text=New Thread size=' in row[0]:
        return True
    else:
        return False


def check_if_consistent(row):
    if 'text=' in row[0]:
        if 'user=' in row[0] and 'id=' in row[0]:
            return True
        else:
            return False
    else:
        return True

# second round of annotation, annotated missing twwets from merging.
#insert to postgres
def concatenate_done_tweets():
    #last step- read and write to one file
    # 1st till id=406517232433233920
    # 2nd from id=406555888607322112
    filenames = ('DATA/goldenStandard/done_tweet.csv',
                 'DATA/goldenStandard/erb-tweet_to_edit.xlsx',
                 'DATA/goldenStandard/tweet_to_edit_part2.xlsx',
                 'DATA/goldenStandard/tweet_to_edit-TS.xlsx')
    tweets_list = list()
    tweets_id_list = set()
    tweet_id_list_db = insert_to_table.select_all_tweets()
    for filename in filenames:
        if filename == 'DATA/goldenStandard/done_tweet.csv':
            tweets_list, tweets_id_list = read_done_tweets_file(filename, None, None, tweets_list, tweets_id_list)
        if filename == 'DATA/goldenStandard/erb-tweet_to_edit.xlsx':
            tweets_list, tweets_id_list = read_done_tweets_file(filename, None, 3820,
                                                                tweets_list, tweets_id_list)
        if filename == 'DATA/goldenStandard/tweet_to_edit-TS.xlsx':
            tweets_list, tweets_id_list = read_done_tweets_file(filename, 6161, None,
                                                                tweets_list, tweets_id_list)
        if filename == 'DATA/goldenStandard/tweet_to_edit_part2.xlsx':
            tweets_list, tweets_id_list = read_done_tweets_file(filename, 3820, 6161,
                                                                tweets_list, tweets_id_list)
    difference_list = set()
    for tweet_id in tweet_id_list_db:
        if tweet_id not in tweets_id_list:
            difference_list.add(tweet_id)
    print 'There are ', len(difference_list), ' tweets to be reviewed.'
    # annotatedData_stat.segments_in_tweet(tweets_list)
    # write_to.write_to_xlsx_file_final(tweets_list, 'DATA/goldenStandard/final_tweets_done.xlsx')
    insert_to_table.insert_annotated_tweets(tweets_list)
    return tweets_list, difference_list


def read_done_tweets_file(filename, start, stop, tweets_list, tweets_id_list):
    tweet = None
    # read_data = True
    workbook = xlrd.open_workbook(filename)
    worksheet = workbook.sheet_by_name('Sheet1')
    if stop is None:
        num_rows = worksheet.nrows - 1
    else:
        num_rows = stop
    if start is None:
        curr_row = 0
    else:
        curr_row = start - 1
    while curr_row < num_rows:
        curr_row += 1
        if worksheet.cell_value(curr_row, 0) != '':
            if type(worksheet.cell_value(curr_row, 0)) is float:
                cell_value = str(int(worksheet.cell_value(curr_row, 0)))
            else:
                cell_value = worksheet.cell_value(curr_row, 0)
            if '#text=' in cell_value and 'id=' in cell_value:

                if tweet is not None:
                    tweet.set_segments()
                    if tweet.get_tweet_id() not in tweets_id_list:
                        tweets_list.append(tweet)
                        tweets_id_list.add(tweet.get_tweet_id())

                tweet_id = re.split('id=', cell_value)[1]
                tweet_id = re.split(' user', tweet_id)[0]
                tweet_id = str(tweet_id)
                text = cell_value
                tweet = annotated_tweet_class.AnnotatedTweet(tweet_id, text)
            else:
                if tweet is not None:
                    offset = str(int(worksheet.cell_value(curr_row, 0)))
                    token = worksheet.cell_value(curr_row, 1)
                    da = str(worksheet.cell_value(curr_row, 6))
                    tweet.set_token(offset, token, da)
        if curr_row == num_rows:
            if tweet is not None:
                tweet.set_segments()
                if tweet.get_tweet_id() not in tweets_id_list:
                    tweets_list.append(tweet)
                    tweets_id_list.add(tweet.get_tweet_id())

    return tweets_list, tweets_id_list

