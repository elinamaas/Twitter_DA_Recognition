__author__ = 'snownettle'

from postgres import postgres_queries, postgres_configuration
from collections import defaultdict
from tabulate import tabulate
from learning.feature import Feature as f
from plots import plots_for_gs


def da_unigrams(taxonomy, cursor):
    results = postgres_queries.find_da_unigrams(taxonomy, cursor)
    for result in results:
        print str(result[0]) + '\t:' + str(result[1])


def length_distribution(taxonomy, cursor):
    da_length_distribution = defaultdict(dict)
    results = postgres_queries.find_da_offset_taxonomy(taxonomy, cursor)
    for result in results:
        da = result[1]
        length = result[3] - result[2] + 1
        if da in da_length_distribution:
            if length in da_length_distribution[da]:
                da_length_distribution[da][length] += 1
            else:
                da_length_distribution[da][length] = 1
        else:
            da_length_distribution[da][length] = 1
    for da, count in da_length_distribution.iteritems():
        lenght_headers = list()
        lenght_headers.append('length')
        tweet_numbers = list()
        tweet_numbers.append('freq')
        for lenght, freq in count.iteritems():
            lenght_headers.append(str(lenght))
            tweet_numbers.append(str(freq))
        data = list()
        data.append(tweet_numbers)
        print 'dialog act: ' + da
        print tabulate(data, lenght_headers)


def overall_segments(cursor):
    results = postgres_queries.find_all_records(postgres_configuration.segmentationTable, cursor)
    print 'There is ' + str(len(results)) + ' segments'


def segments_distribution(cursor):
    tweets = postgres_queries.find_all_records(postgres_configuration.tweetTable, cursor)
    distribution = dict()
    for tweet in tweets:
        number_of_segment_in_tweet = len(postgres_queries.find_segments(tweet[0], cursor))
        if number_of_segment_in_tweet in distribution:
            distribution[number_of_segment_in_tweet] += 1
        else:
            distribution[number_of_segment_in_tweet] = 1
    print 'Segments distribution:'
    print distribution


def da_bigrams(conversations_list, taxonomy, cursor):
    bigrams = defaultdict(dict)
    for conversation in conversations_list:
        previous_da = '<S>'
        root = conversation.root
        previous_da = extract_bigram_info(root, previous_da, bigrams, taxonomy,  cursor)
        previous_da = children_bigrams(root, previous_da, bigrams, taxonomy, cursor)
        add_bigram('<E>', previous_da, bigrams)
    print bigrams


def extract_bigram_info(tweet_id, previous_da, bigrams, taxonomy,  cursor):
    segments = postgres_queries.find_segments(tweet_id, cursor)
    for segment in segments:
        da = extract_da_info(segment, taxonomy)
        add_bigram(da, previous_da, bigrams)
        previous_da = da
    return previous_da


def children_bigrams(parent, previous_da, bigrams, taxonomy, cursor):
    replays = postgres_queries.find_children(parent, cursor)
    for replay in replays:
        previous_da = extract_bigram_info(replay[0], previous_da, bigrams, taxonomy,  cursor)
        children_bigrams(replay[0], previous_da, bigrams, taxonomy, cursor)
    return previous_da


def add_bigram(da, previous_da, bigrams):
    if previous_da in bigrams:
        if da in bigrams[previous_da]:
            bigrams[previous_da][da] += 1
        else:
            bigrams[previous_da][da] = 1
    else:
        bigrams[previous_da][da] = 1


def extract_da_info(segment, taxonomy):
    if taxonomy == 'full':
        da = segment[2]
    elif taxonomy == 'reduced':
        da = segment[3]
    else:
        da = segment[4]
    return da


def conversation_length_amount(conversations_list):
    long_conversations = 0
    short_conversations = 0
    long_conversations_list = list()
    short_conversations_list = list()
    for conversation in conversations_list:
        if conversation.depth() > 4 and len(conversation.nodes) > 20:
            long_conversations += 1
            long_conversations_list.append(conversation)
        else:
            short_conversations += 1
            short_conversations_list.append(conversation)
    print 'long conversation: ' + str(long_conversations)
    print 'short conversation: ' + str(short_conversations)
    return long_conversations_list, short_conversations_list


def deep_distribution(conversation_list):
    distribution = dict()
    for conversation in conversation_list:
        depth = conversation.depth()
        if depth == 0:
            continue
        else:
            if depth in distribution:
                distribution[depth] += 1
            else:
                distribution[depth] = 1
    # plots_for_gs.depth_distribution_plot(distribution)
    print 'Depth distribution'
    print distribution


def feature_distribution(cursor):
    segments = postgres_queries.find_all_records(postgres_configuration.segmentationTable, cursor)
    features_dict = dict()
    features_dict['link'] = 0
    features_dict['hashtag'] = 0
    features_dict['emoticons'] = 0
    for segment in segments:
        utterance = segment[3]
        if f.has_hashtag(utterance):
            features_dict['hashtag'] += 1
        if f.has_link(utterance):
            features_dict['link'] += 1
        if f.has_emoticons(utterance):
            features_dict['emoticons'] += 1
    print 'link has ' + str(features_dict['link']) + ' segments'
    print 'hashtag has ' + str(features_dict['hashtag']) + ' segments'
    print 'emoticons has ' + str(features_dict['emoticons']) + ' segments'


# transition grahp
#how many segments have link, hashtags, etc

