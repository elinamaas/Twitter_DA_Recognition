__author__ = 'snownettle'
import glob
import os
import csv
import re
import convertCharacters
from json import JSONEncoder
from mongoDB import importAnnotatedData


def read_annotated_docs(directory_path, collection_annotated_data):
    conversation_id = 0
    data = {}
    id = 1
    previous_tag = ''
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
                            importAnnotatedData.importAnnotatedData(data, collection_annotated_data)
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
                            if '@' in row[1]:
                                test = row[0].split('-')[1]
                                if row[0].split('-')[1] == '4':
                                    tag = '0'
                                    data[re.split('-', row[0])[1]] = [token, tag]
                                elif '@' in previous_row[1] and previous_tag == '0':
                                    tag = '0'
                                    data[re.split('-', row[0])[1]] = [token, tag]
                                else:
                                    tag = row[2]
                                    data[re.split('-', row[0])[1]] = [token, tag]
                            else:
                                token = row[1]
                                # token = row[1].replace('.', '_')
                                # token = convertCharacters.replace_german_letters(row[1])
                                if row[2] == 'O':
                                    tag = '0'
                                else:
                                    tag = row[2]
                                data[re.split('-', row[0])[1]] = [token, tag]
                            previous_tag = tag
                        elif len(row) < 3:
                            conversation_id = 1

                    previous_row = row
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
