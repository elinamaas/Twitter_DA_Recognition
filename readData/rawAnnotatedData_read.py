import da_taxonomy.matching_schema

__author__ = 'snownettle'
import glob
import os
import csv
import xlrd
import re
from prepare_gold_standard import annotated_tweet_class, write_to
from postgres import insert_to_table, postgres_queries, postgres_configuration
from mongoDB import importData
from da_taxonomy import matching_schema
from statistics import annotatedData_stat
import copy


#read original annotated data, import to mongoDB
def import_annotated_docs(directory_path, collection_annotated_data):
    merged_ontologies = da_taxonomy.matching_schema.merge_ontologies()
    conversation_id = 0
    save_conversation = False
    data = {}
    id = 1
    previous_tag = ''
    tag = ''
    conversation_tweet_id_dict = dict()
    for directory_name in glob.iglob(os.path.join(directory_path,'*.*')):
        for filename in glob.iglob(os.path.join(directory_name, '*.tsv')):
            with open(filename) as f:
                content = csv.reader(f, delimiter='\t')
                previous_row = ' '
                for row in content:
                    if continue_reading(row, previous_row):
                        previous_row = row
                        continue
                    if len(row) is 0 and 'max_depth=' not in previous_row[1]:
                        # import tweet in mongo
                        if tweet_id not in conversation_tweet_id_dict:
                            importData.import_record(data, collection_annotated_data)
                            conversation_tweet_id_dict[tweet_id] = conversation_id
                            continue
                        else:
                            data['conversation_id'] = conversation_tweet_id_dict[tweet_id]
                            importData.import_record(data, collection_annotated_data)
                            continue
                    elif len(row) is 0:
                        continue
                    if '#text=New Thread size' in row[0]:
                        conversation_id += 1
                        data = {}

                    elif '#id' in previous_row[0] and '#text=New Thread' not in row[0] and 'id=' in row[0]:
                        print row
                        tweet_id = re.split('id=', row[0])[1]
                        tweet_id = re.split(' user', tweet_id)[0]
                        data = {}
                        data['conversation_id'] = conversation_id
                        data['tweet_id'] = tweet_id
                        data['text'] = row[0]
                        text_id = re.split('#text=', row[0])[1]
                        text_id = re.split('id=', text_id)[0]
                        data['text_id'] = int(text_id)
                    elif len(row) >= 3:
                        if re.split('-', row[0])[1] not in ['1', '2', '3']:
                            token = row[1]
                            if '@' in token:
                                if row[0].split('-')[1] == '4':
                                    tag = '0'
                                elif '@' in previous_row[1] and previous_tag == '0':
                                    tag = '0'
                                else:
                                    tag = splitting_tag(row, previous_tag)

                            else:
                                tag = splitting_tag(row, previous_tag)

                            tag_reduced, tag_minimal = set_reduced_minimal_tags(tag, merged_ontologies)
                            data[re.split('-', row[0])[1]] = [token, tag, tag_reduced, tag_minimal]
                        previous_tag = tag
                    # elif len(row) < 3:
                    #     conversation_id = 1
                    previous_row = row


def continue_reading(row, previous_row):
    if len(row) == 1:
        if '# webanno.custom.DialogActs' in row[0]:
            # previous_row = row
            return True
        if '#id' in row[0] and '# webanno.custom.DialogActs' in previous_row[0]:
            # previous_row = row
            return True
    elif len(row) > 1:
        if row[1] == 'New' or 'size=' in row[1] or 'max_depth=' in row[1] or row[1] == 'Thread':
            # previous_row = row
            return True

    return False


def set_reduced_minimal_tags(da_full, merged_ontologies):
    if da_full != '0':
        if '|' in da_full:
            das_full = da_full.split('|')
            da_reduced_label = ''
            da_minimal_label = ''
            for da in das_full:
                label = da.split('-')[0]
                da_full_no_label = da.split('-')[1]
                da_reduced = merged_ontologies[da_full_no_label][0]
                da_minimal = merged_ontologies[da_full_no_label][1]
                da_reduced_label_part = label + '-' + da_reduced
                da_reduced_label += da_reduced_label_part + '|'
                da_minimal_label_part = label + '-' + da_minimal
                da_minimal_label += da_minimal_label_part + '|'
            da_reduced_label = da_reduced_label[:-1]
            da_minimal_label = da_minimal_label[:-1]

        else:
            label = da_full.split('-')[0]
            da_full_no_label = da_full.split('-')[1]
            da_reduced = merged_ontologies[da_full_no_label][0]
            da_minimal = merged_ontologies[da_full_no_label][1]
            da_reduced_label = label + '-' + da_reduced
            da_minimal_label = label + '-' + da_minimal

    else:
        da_reduced_label = '0'
        da_minimal_label = '0'
    return da_reduced_label, da_minimal_label


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


def concatenate_done_tweets(cursor, connection):
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
            tweets_list, tweets_id_list = read_done_tweets_file(filename, None, None, tweets_list,
                                                                tweets_id_list, cursor, connection)
        if filename == 'DATA/goldenStandard/erb-tweet_to_edit.xlsx':
            tweets_list, tweets_id_list = read_done_tweets_file(filename, None, 3820,
                                                                tweets_list, tweets_id_list, cursor, connection)
        if filename == 'DATA/goldenStandard/tweet_to_edit-TS.xlsx':
            tweets_list, tweets_id_list = read_done_tweets_file(filename, 6161, None,
                                                                tweets_list, tweets_id_list, cursor, connection)
        if filename == 'DATA/goldenStandard/tweet_to_edit_part2.xlsx':
            tweets_list, tweets_id_list = read_done_tweets_file(filename, 3820, 6161,
                                                                tweets_list, tweets_id_list, cursor, connection)
    difference_list = set()
    for tweet_id in tweet_id_list_db:
        if tweet_id not in tweets_id_list:
            difference_list.add(tweet_id)
    # find additional tweets
    print 'There are ', len(difference_list), ' tweets to be reviewed.'
    # rebuild conversations + write original annotations
    write_to.write_to_xlsx_file_final(tweets_list, 'DATA/goldenStandard/final_tweets_done.xlsx')
    # write_to.write_to_xls_pure_annotation('DATA/goldenStandard/test.xlsx')
    # insert_to_table.insert_annotated_tweets_to_segment_table(tweets_list)
    return tweets_list, difference_list


def read_done_tweets_file(filename, start, stop, tweets_list, tweets_id_list, cursor, connection):
    tweets_list_db = postgres_queries.find_all_tweets_id(cursor)
    tweet = None
    # new_tweets = set()
    # read_data = True
    workbook = xlrd.open_workbook(filename)
    worksheet = workbook.sheet_by_name('Sheet1')
    # previous_tweet = annotated_tweet_class.AnnotatedTweet('', '')
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
                    # if int(tweet_id) not in tweets_list_db:
                    #     # print tweet_id
                    #     new_tweets.add(tweet_id)
                    #     if len(previous_tweet.get_tweet_id()) != 0:
                    #         insert_to_table.insert_missing_tweet(tweet, previous_tweet, cursor, connection)
                    # previous_tweet = copy(tweet)
        if curr_row == num_rows:
            if tweet is not None:
                tweet.set_segments()
                if tweet.get_tweet_id() not in tweets_id_list:
                    tweets_list.append(tweet)
                    tweets_id_list.add(tweet.get_tweet_id())

    return tweets_list, tweets_id_list

