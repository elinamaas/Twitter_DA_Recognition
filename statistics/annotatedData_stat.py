__author__ = 'snownettle'
from mongoDB import queries
from readData import convertCharacters
import sys
from collections import defaultdict
import operator


def if_tag(tag_name, list_of_tag):
    for tag in list_of_tag:
        for key, value in tag.iteritems():
            if tag_name == key:
                return True
    return False


class Segmentation:
    def __init__(self, tweet_id):
        self.tweet_id = tweet_id
        self.segmentation = {}
        self.tags = {}

    def get_tags(self):
        return self.tags

    def get_segments(self):
        return self.segmentation

    def get_id(self):
        return self.tweet_id

    def set_segmentation(self, segmentation):
        self.segmentation = segmentation

    def sef_tags(self, tags):
        self.tags

    @staticmethod
    def add_information(tweet, offset_list):
        # value = {}
        for offset, tag in offset_list.iteritems():
            tag = str(tag)
            if offset in tweet.segmentation:
                tweet.segmentation[offset] += 1
                list_of_tag = tweet.tags[offset]
                if if_tag(tag, list_of_tag) == True:
                # if tag in tweet.tags[offset]:
                    for tag_occurance in list_of_tag:
                        for key, vl in tag_occurance.iteritems():
                            if tag == key:
                                tag_occurance[tag] += 1
                        # value = tweet.tags[offset]
                        # value[tag] += 1
                        # tweet.tags[offset] = value
                else:
                    value = dict()
                    value[tag] = 1
                    # list_of_tag = tweet.tags[offset]
                    list_of_tag.append(value)
            else:
                tweet.segmentation[offset] = 1
                value = dict()
                value[tag] = 1
                new_list = [value]
                tweet.tags[offset] = new_list
        return tweet

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
            # else:
            #     continue
        return Segmentation(tweet_id)


def segmentation(collection):
    records = queries.find_all(collection)
    previous_tag = ' '
    list_of_tweets_with_tags = []
    for record in records:
        dict_tag = set_tag_dictionary(record)
        if len(dict_tag) != 0:
            offset_list = set_offset(dict_tag, record)
            tweet = Segmentation.find_tweet_by_id(record['tweet_id'], list_of_tweets_with_tags)
            tweet = tweet.add_information(tweet, offset_list)
            #check if exists
            if tweet not in list_of_tweets_with_tags:
                list_of_tweets_with_tags.append(tweet)
    print len(list_of_tweets_with_tags)
    # list_of_tweets_with_tags = delete_duplicates(list_of_tweets_with_tags)

    two_agreed_list, segm_1, tag_1 = calculate_stat_segmentation_tags(list_of_tweets_with_tags)
    tag_frequency(list_of_tweets_with_tags)
    two_agreed_list = delete_duplicates(two_agreed_list)
    print 'After merging:'
    # find_two_agreements_tags(list_of_tweets_with_tags)

    new_list = merge_two_lists(list_of_tweets_with_tags, two_agreed_list)
    print_ids(new_list)
    merged_list_of_two_agreed = merge_two_aggreements_for_tag(new_list)
    two_agreed_list, segm_1, tag_1 = calculate_stat_segmentation_tags(merged_list_of_two_agreed)
    tag_frequency(merged_list_of_two_agreed)
    segm_1 = delete_duplicates(segm_1)
    tag_1 = delete_duplicates(tag_1)
    question_list = merge_two_lists(segm_1, tag_1)
    question_list = delete_duplicates(question_list)
    print 'There are ', len(question_list), 'tweets to edit'
    #print_ids(question_list)


def calculate_stat_segmentation_tags(list_of_segmentations):
    segments_3_agree = 0
    segment_2_agree = 0
    segment_3_different = 0
    tag_3_agree = 0
    tag_2_agree = 0
    tag_1_agree = 0
    segments_3 = []
    segments_2 = []
    segments_1 = []
    tags_2 = []
    tags_1 = []
    for tweet in list_of_segmentations:
        offsets = tweet.segmentation.keys()
        for offset in offsets:
            offset_agree = tweet.segmentation[offset]
            if offset_agree == 2:
                segments_2.append(tweet)
                segment_2_agree += 1
                tags_with_count = tweet.tags[offset]
                for tag_dict in tags_with_count:
                    for key, value in tag_dict.iteritems():
                        #tag_count = tags_with_count[tag_dict]
                        # if value == 2 and tag_dict != '0':
                        if value == 2:
                            tag_2_agree += 1
                            tags_2.append(tweet)
                        if value == 3:
                            tag_3_agree += 1
                        if value == 1:
                            tags_1.append(tweet)
                            tag_1_agree += 1
            elif offset_agree == 3:
                segments_3.append(tweet)
                segments_3_agree += 1
                tags_with_count = tweet.tags[offset]
                for tag_dict in tags_with_count:
                    for key, value in tag_dict.iteritems():
                    #tag_count = tags_with_count[tag_dict]
                        if value == 3:
                            tag_3_agree += 1
                        if value == 2:
                            tag_2_agree += 1
                            tags_2.append(tweet)
                        if value == 1:
                            tags_1.append(tweet)
                            tag_1_agree += 1
            elif offset_agree == 1:
                segments_1.append(tweet)
                segment_3_different += 1

    print 'There are ', len(list_of_segmentations), ' of annotated tweets'
    print 'Segmenatation:'
    print '3 students: ', segments_3_agree
    print '2 student: ', segment_2_agree
    print 'single segments: ', segment_3_different
    print 'Tags:'
    print '3 students: ', tag_3_agree
    print '2 student: ', tag_2_agree
    print '1 student: ', tag_1_agree
    return tags_2, segments_1, tags_1


def search_offsets(record):
    previous_tag = ' '
    text = record['text']
    tokens = text.split(' ')
    list_of_offsets = []
    for i in range(4, len(tokens)):
        if previous_tag is ' ':
            start_offset = i
            previous_tag = str(record[str(i)][1])
            if previous_tag != '0' and previous_tag != '':
                previous_tag = previous_tag.split('-')[1]
        if previous_tag is '':
            previous_tag = str(record[str(i)][1])
            if previous_tag != '0' and previous_tag != '':
                previous_tag = previous_tag.split('-')[1]
        else:
            try:
                current_tag = str(record[str(i)][1])
                if current_tag != '0' and current_tag != '':
                    current_tag = current_tag.split('-')[1]
                if previous_tag != current_tag:
                    end_offset = i-1
                    offset = str(start_offset) + ':' + str(end_offset)
                    start_offset = i
                    list_of_offsets.append(offset)
            except KeyError:
                print record
                print sys.exc_info()[0]
            previous_tag = str(record[str(i)][1])
            if previous_tag != '0' and previous_tag != '':
                previous_tag = previous_tag.split('-')[1]
    return list_of_offsets


def search_tag(record, offset):
    key_value = offset.split(':')[0]
    tag = record[key_value][1].encode('utf-8')
    tag = str(tag)
    if tag != '0' and tag != '':
        tag = tag.split('-')[1]
    return tag


def tag_frequency(list_of_segmentations):
    tags_dictionary = {}
    for tweet in list_of_segmentations:
        tags_list = tweet.get_tags()
        # for hh in tags_list:
        for tags, tags_occurancy in tags_list.iteritems():
            for tag_occurancy in tags_occurancy:
                for key, value in tag_occurancy.iteritems():
                    if key in tags_dictionary:
                        tags_dictionary[key] += tag_occurancy[key]
                    else:
                        tags_dictionary[key] = tag_occurancy[key]
    sorted_x = sorted(tags_dictionary.items(), key=operator.itemgetter(1), reverse=True)
    print sorted_x


def set_tag_dictionary(record):
    text = record['text']
    tokens = text.split(' ')
    tags_dict = {}
    # previous_tag = str(record[str(i)][1])
    if len(record) > 5:
        for i in range(4, len(tokens)):
            # if record['tweet_id'] == '404367107431096321':
            #     print 'here'
            tags_value = str(record[str(i)][1])
            if '|' in tags_value:
                tags = tags_value.split('|')
                new_tag_list = []
                for tag in tags:
                    if tag == 'O-_' and len(tags) == 2:
                        tags_dict[i] = str(tags[1]).split('-')[1]
                        break
                    else:
                        tag = tag.split('-')[1]
                        new_tag_list.append(tag)
                    tags_dict[i] = new_tag_list
            elif tags_value == '':
                tags_dict[i] = tags_value
            elif tags_value == '0':
                tags_dict[i] = tags_value
            else:
                tag = tags_value.split('-')[1]
                tags_dict[i] = tag
    return tags_dict


def set_offset(tags_dict, record):
    help_dict = defaultdict(list)
    offset_list = {}
    for i in range(4 + len(tags_dict.keys())):
        if i > 3:
            tags_value = tags_dict[i]
            if isinstance(tags_value, str) is True:
                help_dict[tags_value].append(i)
            else:
                for tag in tags_value:
                    help_dict[tag].append(i)
    ###build offset
    for tag, list_of_occurance in help_dict.iteritems():
        start_offset = list_of_occurance[0]
        previous_offset = start_offset
        last_symbol = list_of_occurance[len(list_of_occurance)-1]
        for i in list_of_occurance:
            if i-previous_offset > 1:
                end_offset = previous_offset
                offset_list[str(start_offset)+':'+str(end_offset)] = tag
                start_offset = previous_offset
                previous_offset = i
            elif i == last_symbol:
                offset_list[str(start_offset)+':'+str(i)] = tag
            else:
                previous_offset = i
    return offset_list


# def merge_two_aggreements_for_tag(tweet_list):
#     help_tweet_list = tweet_list
#     new_tweet_list = []
#     for tweet in tweet_list:
#         help_tweet = tweet
#         new_tweet = Segmentation(tweet.get_id())
#         tags_dict = tweet.get_tags()
#         for offset, tags_occurancy in tags_dict.iteritems():
#             number_of_tags = len(tags_occurancy)
#             if number_of_tags > 1:
#                 for tag_occurancy in tags_occurancy:
#                     for tag_name, occurancy in tag_occurancy.iteritems():
#                         if occurancy == 2:
#                             start_offset, end_offset = offset.split(':')
#                             start_offset = int(start_offset)
#                             end_offset = int(end_offset)
#                             offset_list = get_offset_list(start_offset, end_offset)
#
#
#                             help_tags_dict = help_tweet.get_tags()
#                             help_segmentation_dict = help_tweet.get_segments()
#                             for key, value in help_tags_dict.iteritems():
#                                 if key != offset:
#                                     start, end = key.split(':')
#                                     start = int(start)
#                                     end = int(end)
#                                     if start not in offset_list and end not in offset_list and tweet.segmentation[key] != 2:
#                                         new_tweet.segmentation[key] = tweet.segmentation[key]
#                                         new_tweet.tags[key] = tweet.tags[key]
#                                         #new_tweet.set_tags(help_tags_dict[key])
#                                         #new_tweet.set_segmentation(help_segmentation_dict[key])
#                                 else:
#                                     new_tweet.segmentation[offset] = 3
#                                     new_tag_info = dict()
#                                     #tag_value = value[0]
#                                     # for t, v in tag_value:
#                                     new_tag_info[tag_name] = 3
#                                     new_list = [new_tag_info]
#                                     new_tweet.tags[offset] = new_list
#         new_tweet_list.append(new_tweet)
#     return new_tweet_list


def get_offset_list(start, end):
    offset_list = []
    i = start
    end += 1
    while i < end:
        offset_list.append(i)
        i += 1
    return offset_list


def delete_duplicates(tweets_list):
    new_tweets_list = []
    help_list = []
    for tweet in tweets_list:
        if len(new_tweets_list) == 0:
            help_list.append(tweet.tweet_id)
            new_tweets_list.append(tweet)
            continue
        else:
            if tweet.tweet_id not in help_list:
                help_list.append(tweet.tweet_id)
                new_tweets_list.append(tweet)
    return new_tweets_list


def merge_two_lists(tweets_list, two_agreed_list):
    new_list = two_agreed_list
    help_list = []
    for i in two_agreed_list:
        help_list.append(i.tweet_id)
    for j in tweets_list:
        if j.tweet_id not in help_list:
            new_list.append(j)
    return new_list


def print_ids(tweet_list):
    for tweet in tweet_list:
        print 'tweet_id: ', tweet.tweet_id, ' : ', 'segmentation: ', tweet.segmentation, 'tags: ', tweet.tags


def merge_two_aggreements_for_tag(tweet_list):
    for tweet in tweet_list:
        help_tweet = tweet
        new_tweet = Segmentation(tweet.get_id())
        tags_dict = tweet.get_tags()
        for offset, tags_occurancy in tags_dict.iteritems():
            number_of_tags = len(tags_occurancy)
            if number_of_tags > 1:
                for tag_occurancy in tags_occurancy:
                    for tag_name, occurancy in tag_occurancy.iteritems():
                        if occurancy == 2:
                            tag_occurancy[tag_name] = 3
                            new_list_of_tags = [tag_occurancy]
                            tags_dict[offset] = new_list_of_tags
    return tweet_list
