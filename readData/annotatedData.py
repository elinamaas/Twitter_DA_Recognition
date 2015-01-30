__author__ = 'snownettle'
import glob
import os
import csv
import re
import nltk


def read_annotated_docs(directory_path):
    conversation_id = 0
    tweet_id = 0
    token = ''
    tag = ''

    for directory_name in glob.iglob(os.path.join(directory_path,'*.*')):
        for filename in glob.iglob(os.path.join(directory_name, '*.tsv')):
            with open(filename) as f:
                content = csv.reader(f, delimiter='\t')
                previous_row = ' '
                for row in content:
                    if len(row) is 0:
                        if conversation_id is not '1':
                            print 'conversation id: ', conversation_id, 'tweet id: ', tweet_id, '\n token: ',
                            token, 'tag: ', tag
                        else:
                            continue
                    else:
                        if '#id' in row[0]:
                            conversation_id = re.split('id=', row[0])[1]
                        if len(previous_row) is not 0 and '#id' in previous_row[0] and conversation_id is not '1':
                            #find tweet id
                            tweet_id = re.split('id=', row[0])[1]
                            tweet_id = re.split(' user', tweet_id)[0]
                        if conversation_id is re.split('-', row[0])[0] and conversation_id is not '1':
                            #######SPLIT NUMBERS!
                            token = row[1]
                            tag = row[2]


                    previous_row = row
                #print content


def find_in_replay_to_the_status (collection, tweet_id):
    tweet = collection.find({'id':tweet_id})
    return tweet['in_reply_to_status_id']


def find_annotated_tweet_id(row):
    if '#id' in row[0]:
        return re.split('id=', row[0])[1]
        # if 'user' not in t:
        #     return t
        #     #print re.split(' user', t)[0]
        # else:
        #     print t
        #print 'yes'


#def find_tweet_id(row):