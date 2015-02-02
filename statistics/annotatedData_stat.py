__author__ = 'snownettle'
from mongoDB import queries
from readData import convertCharacters
import sys


class Segmentation:
    def __init__(self, tweet_id):
        self.tweet_id = tweet_id
        self.segmentation = {}
        self.tags = {}

    @staticmethod
    def add_offset(tweet, offset):
        if offset in tweet.segmentation:
            #tweet.segmentation[0] = offset
            tweet.segmentation[offset] += 1
        else:
            #tweet.segmentation[0] = offset
            tweet.segmentation[offset] = 1

    @staticmethod
    def add_tags(tweet, offset, tag):
        value = {}
        if offset in tweet.tags:
            value = tweet.tags[offset]
            if tag in value:
                value[tag] += 1
            else:
                value[tag] = 1
        else:
            value[tag] = 1
            tweet.tags[offset] = value

    @staticmethod
    def find_tweet_by_id(tweet_id, list_of_tweets):
        for tweet in list_of_tweets:
            if tweet_id == tweet.tweet_id:
                return tweet
            else:
                continue
        return Segmentation(tweet_id)


def segmentation(collection):
    records = queries.find_all(collection)
    previous_tag = ' '
    list_of_segmentations = []
    for record in records:
        tweets_segmentation = Segmentation.find_tweet_by_id(record['tweet_id'], list_of_segmentations)
        list_of_offsets = search_offsets(record)
        for offset in list_of_offsets:
            Segmentation.add_offset(tweets_segmentation, offset)
            tag = search_tag(record, offset)
            Segmentation.add_tags(tweets_segmentation, offset, tag)
        if len(list_of_segmentations) == 0:
            list_of_segmentations.append(tweets_segmentation)
        else:
            if tweets_segmentation not in list_of_segmentations:
                list_of_segmentations.append(tweets_segmentation)
    #print len(list_of_segmentations)
    calculate_stat_segment(list_of_segmentations)
    calculate_stat_tag(list_of_segmentations)


def calculate_stat_tag(list_of_segmentations):
    i = 0
    j = 0
    k = 0
    for tweet in list_of_segmentations:
        tags = tweet.tags.values()
        for tag in tags:
            values = tag.values()
            for value in values:
                if value == 3:
                    i += 1
                elif value == 2:
                    j += 1
                elif value == 1:
                    k += 1
    print 'tags'
    print '3 students: ', i
    print '2 students: ', j
    print '1 student: ', k





def calculate_stat_segment(list_of_segmentations):
    i = 0
    j = 0
    k = 0
    for tweet in list_of_segmentations:
        values = tweet.segmentation.values()
        for value in values:
            if value == 3:
                i += 1
            elif value == 2:
                j += 1
            elif value == 1:
                k += 1
    print 'segmenatation:'
    print '3 students: ', i
    print '2 student: ', j
    print '1 student: ', k

def search_offsets(record):
    previous_tag = ' '
    text = record['text']
    tokens = text.split(' ')
    list_of_offsets = []
    for i in range(4, len(tokens)):
        token = tokens[i].encode('utf-8')
        token = convertCharacters.replace_german_letters(token)
        #print token
        if previous_tag is ' ':
            start_offset = i
            previous_tag = record[str(i)][1]
        else:
            try:
                current_tag = record[str(i)][1]
                if previous_tag != current_tag:
                    end_offset = i-1
                    offset = str(start_offset) + ':' + str(end_offset)
                    start_offset = i
                    list_of_offsets.append(offset)
            except KeyError:
                print record
                print sys.exc_info()[0]
            previous_tag = record[str(i)][1]
    return list_of_offsets


def search_tag(record, offset):
    key_value = offset.split(':')[0]
    tag = record[key_value][1].encode('utf-8')
    return tag
