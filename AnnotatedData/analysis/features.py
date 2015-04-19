__author__ = 'snownettle'
from postgres import postgres_queries
import collections


def calculate_da_bigrams():
    conversation_list = postgres_queries.find_conversations_root()
    bigrams = dict() #<S> for the start of the conversation
    for root in conversation_list: #query only for roots!
        start_symbol = '<S>'
        segments = postgres_queries.find_segments(root[0])
        segments_da = sort_segments(segments)
        for start_offset, da in segments_da.iteritems():
            bigram = start_symbol + ', ' + da
            start_symbol = da
            if bigram in bigrams:
                bigrams[bigram] += 1
            else:
                bigrams[bigram] = 1
        find_children(root[0], start_symbol, bigrams)

    for bigram, count in bigrams.iteritems():
        print bigram + '\t ' + str(count)
    return bigrams

def sort_segments(db_segments):
    segments_dict = dict()
    for segment in db_segments:
        offset = segment[0]
        da = segment[1]
        start_offset = int(offset.split(':')[0])
        segments_dict[start_offset] = da
    new_segments_dict = collections.OrderedDict(sorted(segments_dict.items()))
    return new_segments_dict


def find_children(tweet_id, start_symbol, bigrams):
    children = postgres_queries.find_children(tweet_id)
    previous_tweet_da = start_symbol
    if len(children) == 1:
        tweet_id_child = int(children[0][0])
        segments = postgres_queries.find_segments(tweet_id_child)
        segments_da = sort_segments(segments)
        for start_offset, da in segments_da.iteritems():
            bigram = start_symbol + ', ' + da
            start_symbol = da
            if bigram in bigrams:
                bigrams[bigram] += 1
            else:
                bigrams[bigram] = 1
        find_children(tweet_id_child, start_symbol, bigrams)
    else:
        for child in children:
            start_symbol = previous_tweet_da
            segments = postgres_queries.find_segments(int(child[0]))
            segments_da = sort_segments(segments)
            for start_offset, da in segments_da.iteritems():
                bigram = start_symbol + ', ' + da
                start_symbol = da
                if bigram in bigrams:
                    bigrams[bigram] += 1
                else:
                    bigrams[bigram] = 1
            find_children(int(child[0]), start_symbol, bigrams)

calculate_da_bigrams()