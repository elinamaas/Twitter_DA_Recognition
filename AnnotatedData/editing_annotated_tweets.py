__author__ = 'snownettle'
from mongoDB import queries
from AnnotatedData.annotated_tweet_class import Annotated_Tweet
import re
from collections import defaultdict


def segmentation(collection):
    records = queries.find_all(collection)
    list_of_tweets_with_tags = []
    for record in records:
        tweet_id = record['tweet_id']
        text_id = record['text_id']
        text = record['text']
        tweet = Annotated_Tweet.check_if_tweet_exists(list_of_tweets_with_tags, tweet_id, text_id, text)
        tokens, segments, word_dictionary = find_tokens_segmentation(record)
        tweet = tweet.set_word(word_dictionary)
        tweet = tweet.add_token(tokens)
        tweet = tweet.add_segmentation(segments)
        if tweet not in list_of_tweets_with_tags:
            list_of_tweets_with_tags.append(tweet)
    return list_of_tweets_with_tags


def find_tokens_segmentation(record):
    word_dictionary = dict()
    text = record['text']
    tokens = text.split(' ')
    tags_dictionary = {}
    previous_tag = ''
    start_offset = 0
    end_offset = 0
    tags_occuracy = defaultdict(list)
    offsets_list = list()
    for i in range(4, len(tokens)+1):
        tag = str(record[str(i)][1])
        word = record[str(i)][0]
        word_dictionary[i] = word
        if tag != '0' and '|' not in tag:
            tag = re.split('-', tag)[1]
        if '|' in tag:
            tags_list = spilt_tags(tag)
            tags_dictionary[i] = tags_list
            for tag_name in tags_list:
                tags_occuracy[tag_name].append(i)
        elif '|' not in tag:
            tags_dictionary[i] = tag
            tags_occuracy[tag].append(i)
    offsets_list = make_segmentation_list(tags_occuracy)
    return tags_dictionary, offsets_list, word_dictionary


def merge_annotations(tweets_list):
    for tweet in tweets_list:
        tokens_dictionary = tweet.get_token()
        for offset, tags in tokens_dictionary.iteritems():
            if len(tags) == 2:
                agreed_number_first = tags[0].values()
                agreed_number_second = tags[1].values()
                if 1 in agreed_number_first and 2 in agreed_number_second:
                    for tag_name, value in tags[1].iteritems():
                        tags[1][tag_name] = 3
                    tags.remove(tags[0])
                elif 2 in agreed_number_first and 1 in agreed_number_second:
                    for tag_name, value in tags[0].iteritems():
                        tags[0][tag_name] = 3
                    tags.remove(tags[1])
    return tweets_list


def spilt_tags(tags):
    tags_name = tags.split('|')
    tags_list = list()
    for i in range(0, len(tags_name)):
        if 'O-' != tags_name[i]:
            tag_name = re.split('-', tags_name[i])[1]
            tags_list.append(tag_name)
    return tags_list


def make_segmentation_list(tags_occurancy_dict):
    start_offset = 0
    end_offset = 0
    previous_offset = 0
    segmentation_list = list()
    for tag_name, offset_list in tags_occurancy_dict.iteritems():
        previous_offset = 0
        for offset in offset_list:
            end_offset = offset
            if previous_offset == 0:
                start_offset = offset
            else:
                if offset - previous_offset != 1:
                    #end_offset = previous_offset
                    segmentation_list.append(str(start_offset) + ':' + str(previous_offset))
                    start_offset = offset
            previous_offset = offset
        segmentation_list.append(str(start_offset) + ':' + str(end_offset))
    return segmentation_list
