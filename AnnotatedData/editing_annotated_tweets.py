__author__ = 'snownettle'
from mongoDB import queries
from annotatedData.annotated_tweet_class import AnnotatedTweetEdit
import re
from collections import defaultdict
import itertools
from annotation.dialogue_acts_tree import find_common_parent, check_related_tags


def segmentation(collection):
    records = queries.find_all(collection)
    list_of_tweets_with_tags = []
    unigrams_dict = dict()
    for record in records:
        tweet_id = record['tweet_id']
        text_id = record['text_id']
        text = record['text']
        tweet = AnnotatedTweetEdit.check_if_tweet_exists(list_of_tweets_with_tags, tweet_id, text_id, text)
        tokens, word_dictionary, source_tags = find_tokens_segmentation(record)
        tweet = tweet.set_word(word_dictionary)
        previous_tag = ''
        # for token in tokens:
        for offset, name in tokens.iteritems():
            if previous_tag is list:
                if type(name) is list:
                        for n in name:
                            if n not in previous_tag:
                                if n in unigrams_dict:
                                    unigrams_dict[n] += 1
                                else:
                                    unigrams_dict[n] = 1

                else:
                    if name not in previous_tag:
                        if name in unigrams_dict:
                            unigrams_dict[name] += 1
                        else:
                            unigrams_dict[name] = 1

            else:
                if previous_tag != name:
                    if type(name) is list:
                        for n in name:
                            if n in unigrams_dict:
                                unigrams_dict[n] += 1
                            else:
                                unigrams_dict[n] = 1
                    else:
                        if name in unigrams_dict:
                            unigrams_dict[name] += 1
                        else:
                            unigrams_dict[name] = 1
            previous_tag = name

        tweet = tweet.add_tag(tokens)
        # tweet = tweet.add_segmentation(segments)
        tweet.add_source_segments(source_tags) #set segmentation for raw annotated tweets
        # tweet.set_source_segmentation()
        if tweet not in list_of_tweets_with_tags:
            list_of_tweets_with_tags.append(tweet)
    print 'UNIGRAMS FOR RAW ANNOTATION'
    for tag_name, occurancy in unigrams_dict.iteritems():
        print tag_name + '\t ' + str(occurancy)
    return list_of_tweets_with_tags


def find_tokens_segmentation(record):
    word_dictionary = dict()
    text = record['text']
    tokens = text.split(' ')
    tags_dictionary = {}
    previous_tag = ''
    start_offset = 0
    end_offset = 0
    source_tags = defaultdict(list)
    # tags_occuracy = defaultdict(list)
    offsets_list = list()
    for i in range(4, len(tokens)+1):
        tag = str(record[str(i)][1])
        word = record[str(i)][0]
        word_dictionary[i] = word
        if tag != '0' and '|' not in tag:
            source_tags[tag].append(i)
            tag = re.split('-', tag)[1]
            # if tag != '_' and tag != 'Wurst' and tag != 'NEIN' and tag != 'Ironie':
            tags_dictionary[i] = tag
                # tags_occuracy[tag].append(i)
            source_tags[tag].append(i)
            # else:
            #     tags_dictionary[i] = '0'
            #     # tags_occuracy[tag].append(i)
            #     source_tags['0'].append(i)
        elif '|' in tag:
            source_da = tag.split('|')
            # j = 0
            for s in source_da:
                source_tags[s].append(i)

            tags_list = spilt_tags(tag)
            tags_dictionary[i] = tags_list
            # for tag_name in tags_list:
            #     tags_occuracy[tag_name].append(i)
        elif tag == '0':
            tags_dictionary[i] = tag
            source_tags[tag].append(i)



    # offsets_list = make_segmentation_list(tags_occuracy)
    return tags_dictionary, word_dictionary, source_tags


def merge_annotations(tweets_list):
    for tweet in tweets_list:
        tokens_dictionary = tweet.get_tags()
        for offset, tags in tokens_dictionary.iteritems():
            if len(tags) == 2:
                values = tags.values()
                agreed_number_first = values[0]
                agreed_number_second = values[1]
                difference = abs(agreed_number_first - agreed_number_second)
                if difference >= 1:
                    token_to_delete = ''
                    for tag_name, value in tags.iteritems():
                        if agreed_number_first == value:
                            if agreed_number_first > agreed_number_second:
                                tokens_dictionary[offset][tag_name] += agreed_number_second
                            else:
                                token_to_delete = tag_name
                        if agreed_number_second == value:
                            if agreed_number_first < agreed_number_second:
                                tokens_dictionary[offset][tag_name] += agreed_number_first
                            else:
                                token_to_delete = tag_name
                    del tweet.get_tags()[offset][token_to_delete]
            if len(tags) > 2:
                values_list = list()
                for tag_name, count in tags.iteritems():
                    values_list.append(count)
                sum_values = sum(values_list)
                for value in values_list:
                    difference = sum_values - value
                    if difference < value:
                        tags_to_delete = list()
                        for tag_name, count in tags.iteritems():
                            if count == value:
                                tweet.get_tags()[offset][tag_name] = sum_values
                            else:
                                tags_to_delete.append(tag_name)
                        for tag_name in tags_to_delete:
                            del tweet.get_tags()[offset][tag_name]

    return tweets_list


def spilt_tags(tags):
    tags_name = tags.split('|')
    tags_list = list()
    for i in range(0, len(tags_name)):
        # if 'O-_' != tags_name[i]: #maybe '0'?
        tag_name = re.split('-', tags_name[i])[1]
            # if tag_name != 'NEIN' and tag_name != 'Wurst' and tag_name != 'Ironie':
        tags_list.append(tag_name)
            # else:
            #     tags_list.append('0')
        # else:
        #     tags_list.append('0')
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
                    segmentation_list.append(str(start_offset) + ':' + str(previous_offset))
                    start_offset = offset
            previous_offset = offset
        segmentation_list.append(str(start_offset) + ':' + str(end_offset))
    return segmentation_list


def rewrite_segmentation(tweets_list):
    for tweet in tweets_list:
        da_dict = defaultdict(list)
        segmentateion_dict = dict()
        token = tweet.get_tags()
        for offset, da_tags in token.iteritems():
            for tag_name, value in da_tags.iteritems():
                da_dict[tag_name].append(offset)
        segmentation_list = make_segmentation_list(da_dict)
        for segment in segmentation_list:
            if segment in segmentateion_dict:
                segmentateion_dict[segment] += 1
            else:
                segmentateion_dict[segment] = 1
        tweet.set_new_segmentation(segmentateion_dict)


def compare_two_tags(da_taxonomy, tag1, tag2, tags_dictionary, tweet, offset, tags_list):
    parent_tag = find_common_parent(da_taxonomy,tag1, tag2)
    related_tag = check_related_tags(da_taxonomy, tag1, tag2)
    if parent_tag is not None:
        count1 = 0
        count2 = 0
        if tag1 in tags_dictionary:
            count1 = tags_dictionary[tag1]
        if tag2 in tags_dictionary:
            count2 = tags_dictionary[tag2]
        count = count1 + count2
        tweet.get_tags()[offset][parent_tag] = count
        if tag1 in tweet.get_tags()[offset]:
            del tweet.get_tags()[offset][tag1]
        if tag2 in tweet.get_tags()[offset]:
            del tweet.get_tags()[offset][tag2]
    else:
        if related_tag is not None:
            count1 = 0
            count2 = 0
            if tag1 in tags_dictionary:
                count1 = tags_dictionary[tag1]
            if tag2 in tags_dictionary:
                count2 = tags_dictionary[tag2]
            count = count1 + count2
            tweet.get_tags()[offset][related_tag] = count
            if tag1 != related_tag:
                if tag1 in tweet.get_tags()[offset]:
                    del tweet.get_tags()[offset][tag1]
            if tag2 != related_tag:
                if tag2 in tweet.get_tags()[offset]:
                    del tweet.get_tags()[offset][tag2]


def check_da_parent(da_taxonomy, tag_list_of_dictionary, tweet, offset):
    tags_list = build_tag_list_for_offset(tag_list_of_dictionary)
    pair_tags = list(itertools.combinations(tags_list, 2))
    for pair in pair_tags:
        compare_two_tags(da_taxonomy, pair[0], pair[1], tag_list_of_dictionary, tweet, offset, tags_list)


def merge_da_children(tweets_list, da_taxonomy):
    for tweet in tweets_list:
        da_tokens = tweet.get_tags()
        for offset, da_tags_list in da_tokens.iteritems():
            variants_of_tags = len(da_tags_list)
            if variants_of_tags > 1:
                check_da_parent(da_taxonomy, da_tags_list, tweet, offset)


def build_tag_list_for_offset(da_tags_list):
    tags_list = list()
    for tag_name, count in da_tags_list.iteritems():
        tags_list.append(tag_name)
    return tags_list


def check_final_segmentation(list_of_tweets):
    for tweet in list_of_tweets:
        source_segmentation = tweet.get_source_segmentation()
        current_segmentation = tweet.get_segmentation()
        if len(current_segmentation) == 1:
            if len(source_segmentation) == 1:
                if list(source_segmentation)[0] in current_segmentation:
                    print 'good'
                else:
                    print 'not good'
        else:
            print 'tweet_id: ', tweet.get_tweet_id(),  ', current_segmentation: ', \
                current_segmentation, ', source_segmentation: ',  source_segmentation
            #what if we have more than one?


def numbers_of_tweets_agreed_by_three(list_of_tweets):
    agreed_with_segmentation = 0
    argeed_with_tags = list()
    tweets_to_edit = list()
    for tweet in list_of_tweets:
        same_dicision = 0
        segmentation_dictionary = tweet.get_segmentation()
        segmentation_values = segmentation_dictionary.values()
        if 2 not in segmentation_values and 1 not in segmentation_values:
            agreed_with_segmentation += 1
            token_dictionary = tweet.get_tags()
            token_number = len(token_dictionary)
            for offset, tags in token_dictionary.iteritems():
                if len(tags) == 1:
                    for tag_name, agreed in tags.iteritems():
                        if agreed == 3:
                            same_dicision += 1
            if same_dicision == token_number:
                argeed_with_tags.append(tweet)
            else:
                tweets_to_edit.append(tweet)
        else:
            tweets_to_edit.append(tweet)
    return agreed_with_segmentation, argeed_with_tags, tweets_to_edit








