__author__ = 'snownettle'
import glob
import os
import csv
import re

from mongoDB import importData


def read_annotated_docs(directory_path, collection_annotated_data):
    conversation_id = 0
    data = {}
    id = 1
    previous_tags = set()
    for directory_name in glob.iglob(os.path.join(directory_path,'*.*')):
        for filename in glob.iglob(os.path.join(directory_name, '*.tsv')):
            with open(filename) as f:
                content = list(csv.reader(f, delimiter='\t'))
                previous_row = ' '
                row_number = 0

                for row in content:
                    if (row_number + 1) != len(content):
                        next_row = content[row_number + 1]
                    elif (row_number + 1) == len(content):
                        next_row = ''
                    if len(row) is 0:
                        if conversation_id is not '1':
                            data['id'] = id
                            id += 1
                            importData.import_record(data, collection_annotated_data)
                        else:
                            row_number += 1
                            continue
                    else:
                        if check_if_new_thread(row) is False:
                            conversation_id = '1'
                        else:
                            if '#id' in row[0]:
                                conversation_id = re.split('id=', row[0])[1]
                                data = {}
                                data['conversation_id'] =conversation_id
                            elif check_if_consistent(row) is False:
                                row_number += 1
                                continue
                            elif conversation_id == '1':
                                row_number += 1
                                continue
                            elif len(previous_row) is not 0 and 'user=' in row[0]:
                                tweet_id = re.split('id=', row[0])[1]
                                tweet_id = re.split(' user', tweet_id)[0]
                                data['tweet_id'] = tweet_id
                                data['text'] = row[0]
                                text_id = re.split('#text=', row[0])[1]
                                text_id = re.split('id=', text_id)[0]
                                data['text_id'] = text_id
                            elif check_tag(row, conversation_id) is True:
                                #here should be a function
                                previous_tags = assign_tags(row, previous_tags, previous_row, data, next_row)

                    previous_row = row
                    row_number += 1

                #print content


def find_in_replay_to_the_status(collection, tweet_id):
    print tweet_id
    tweet = collection.find({'id':tweet_id})
    #print tweet.count()
    return tweet[0]['in_reply_to_status_id']


def find_annotated_tweet_id(row):
    if '#id' in row[0]:
        return re.split('id=', row[0])[1]


def check_if_new_thread(row):
    if 'webanno.custom.DialogActs' in row[0] or '#text=New Thread size=' in row[0]:
        return False
    else:
        return True


def check_if_consistent(row):
    if 'text=' in row[0]:
        if 'user=' in row[0] and 'id=' in row[0]:
            return True
        else:
            return False
    else:
        return True


def disambiguation_tags(tags, next_raw, previous_row, previous_tags):
    #check iif previous row has @ - assign begin label
    new_previous_tags = list()
    tags_list = tags.split('|')
    add_end_label = list()
    new_current_tags = list()

    assign_begin_tag = check_user_mentioned(previous_row, previous_tags)
    for current_tag in tags_list:
        if current_tag != 'O-_':
            current_tag = check_next_tags(current_tag, next_raw)
            if assign_begin_tag is True:
                current_tag = 'B-' + re.split('-', current_tag)[1]

            new_previous_tags.append(current_tag)
            new_current_tags.append(current_tag)
    return new_current_tags, new_previous_tags


def assign_tags(row, previous_tags, previous_row, data, next_raw):
    token = row[1]
    assign_begin_label = check_user_mentioned(previous_row, previous_tags)
    tag = ''
    if '@' in token:
        if row[0].split('-')[1] == '4':
            tag = '0'
        elif '@' in previous_row[1] and '0' in previous_tags:
            tag = '0'
        else:
            if row[2] == 'O':
                tag = '0'
            else:
                if '|' in row[2]:
                    tag, previous_tags = disambiguation_tags(row[2], next_raw, previous_row, previous_tags)
                else:
                    tag = check_next_tags(row[2], next_raw)
                    if tag == 'O-_':
                        tag = '0'
                    if assign_begin_label is True and tag != '0':
                        tag = 'B-' + re.split('-', row[2])[1]
    else:
        if row[2] == 'O':
            tag = '0'
        else:
            if '|' in row[2]:
                tag, previous_tags = disambiguation_tags(row[2], next_raw, previous_row, previous_tags)
            else:
                tag = check_next_tags(row[2], next_raw)
                if tag == 'O-_':
                    tag = '0'
                if assign_begin_label is True and tag != '0':
                    tag = 'B-' + re.split('-', row[2])[1]
    data[re.split('-', row[0])[1]] = [token, tag]
    if isinstance(tag, list) is False:
        previous_tags = list()
        previous_tags.append(tag)
    return previous_tags


def check_tag(row, conversation_id):
    help_list = ['1', '2', '3']
    if conversation_id == re.split('-', row[0])[0] and re.split('-', row[0])[1] not in help_list and len(row) > 3:
        return True
    else:
        return False


def check_user_mentioned(previous_row, previous_tags):
    # assign_begin_tag = False
    token = previous_row[1]
    if '@' in token and '0' in previous_tags:
        return True
    else:
        return False


def check_next_tags(current_tag, next_raw):
    if len(next_raw) == 0:
        new_tag = 'E-' + current_tag.split('-')[1]
    else:
        next_tags = list()
        if '|' in next_raw[2]:
            next_tags = next_raw[2].split('|')
        else:
            next_tags.append(next_raw[2])
        add_end_label = list()
        if len(next_tags) == 0:
            new_tag = 'E-' + current_tag.spilt('-')[1]
        else:
            if compare_tags(current_tag, next_tags) is True:
                new_tag = current_tag
            else:
                new_tag = 'E-' + current_tag.split('-')[1]
    return new_tag


def compare_tags(current_tag, compare_to):
    current_tag = current_tag.split('-')[1]
    if isinstance(compare_to, list):
        for tag in compare_to:
            if tag != 'O':
                tag = tag.split('-')[1]
            if current_tag == tag:
                return True
    else:
        compare_to = compare_to.split('-')[1]
        if current_tag == compare_to:
            return True
        else:
            return False
    return False
