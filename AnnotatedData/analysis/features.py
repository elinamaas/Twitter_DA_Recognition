__author__ = 'snownettle'
from postgres import postgres_queries
import collections


def calculate_da_bigrams(): #overall
    conversation_list = postgres_queries.find_conversations_root()
    bigrams = dict() #<S> for the start of the conversation
    for root in conversation_list: #query only for roots!
        start_symbol = '<S>'
        segments = postgres_queries.find_segments(root[0])
        segments_da = sort_segments(segments)
        for start_offset, da in segments_da.iteritems():
            if da != '0':
                bigram = start_symbol + ', ' + da
                start_symbol = da
                if bigram in bigrams:
                    bigrams[bigram] += 1
                else:
                    bigrams[bigram] = 1
        find_children(root[0], start_symbol, bigrams)

    # for bigram, count in bigrams.iteritems():
    #     print bigram + '\t ' + str(count)
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
            if da != '0':
                bigram = start_symbol + ', ' + da
                start_symbol = da
                if bigram in bigrams:
                    bigrams[bigram] += 1
                else:
                    bigrams[bigram] = 1
        find_children(tweet_id_child, start_symbol, bigrams)
    elif len(children) > 1:
        for child in children:
            start_symbol = previous_tweet_da
            segments = postgres_queries.find_segments(int(child[0]))
            segments_da = sort_segments(segments)
            for start_offset, da in segments_da.iteritems():
                if da != '0':
                    bigram = start_symbol + ', ' + da
                    start_symbol = da
                    if bigram in bigrams:
                        bigrams[bigram] += 1
                    else:
                        bigrams[bigram] = 1
            find_children(int(child[0]), start_symbol, bigrams)
    else:
        end_symbol = '<E>'
        bigram = start_symbol + ', ' + end_symbol
        if bigram in bigrams:
            bigrams[bigram] += 1
        else:
            bigrams[bigram] = 1


def calculate_da_unigrams_short_long(): #pro segment
    unigram_long = dict()
    unigram_short = dict()
    conversation_list = postgres_queries.find_conversations()
    for conversation in conversation_list:
        if len(conversation) >= 20: #long conversation
            for tweet in conversation:
                tweet_id = tweet[0]
                tags = postgres_queries.find_das_for_tweet(tweet_id)
                for tag in tags:
                    if tag[0] in unigram_long:
                        unigram_long[tag[0]] += 1
                    else:
                        unigram_long[tag[0]] = 1
        else: #short conversation
            for tweet in conversation:
                tweet_id = tweet[0]
                tags = postgres_queries.find_das_for_tweet(tweet_id)
                for tag in tags:
                    if tag[0] in unigram_short:
                        unigram_short[tag[0]] += 1
                    else:
                        unigram_short[tag[0]] = 1
    print 'Unirgrams for short tweets:'
    for tag, count in unigram_short.iteritems():
        print tag + '\t' + str(count)
    print '\n Unirgrams for long tweets:'
    for tag, count in unigram_long.iteritems():
        print tag + '\t' + str(count)


def calculate_da_bigram_short_long():
    conversation_list = postgres_queries.find_conversations_root()
    # bigrams = dict() #<S> for the start of the conversation
    bigrams_short = dict()
    bigrams_long = dict()
    for root in conversation_list: #query only for roots!
        start_symbol = '<S>'
        conversation_number = root[2]
        conversation = postgres_queries.find_conversation(conversation_number)
        segments = postgres_queries.find_segments(root[0])
        segments_da = sort_segments(segments)
        if len(conversation) >= 20:
            for start_offset, da in segments_da.iteritems():
                if da != '0':
                    bigram = start_symbol + ', ' + da
                    start_symbol = da
                    if bigram in bigrams_long:
                        bigrams_long[bigram] += 1
                    else:
                        bigrams_long[bigram] = 1
            find_children(root[0], start_symbol, bigrams_long)
        else:
            for start_offset, da in segments_da.iteritems():
                if da != '0':
                    bigram = start_symbol + ', ' + da
                    start_symbol = da
                    if bigram in bigrams_short:
                        bigrams_short[bigram] += 1
                    else:
                        bigrams_short[bigram] = 1
            find_children(root[0], start_symbol, bigrams_short)

    print 'Bigram for short conversations:'
    for bigram, count in bigrams_short.iteritems():
        print bigram + '\t ' + str(count)
    print '\n\n\nBigram for long conversations:'
    for bigram, count in bigrams_long.iteritems():
        print bigram + '\t ' + str(count)
    # return bigrams


def calculate_unigrams():
    unigrams = dict()
    pg_unigrams = postgres_queries.find_da_unigrams()
    for unigram in pg_unigrams:
        if unigram[1] in unigrams:
            unigrams[unigram[1]] += unigram[0]
        else:
            unigrams[unigram[1]] = unigram[0]
    unigrams['<S>'] = 172
    return unigrams


def bigram_probability(bigrams, unigrams):
    bigram_prob = dict()
    for bigram, count in bigrams.iteritems():
        first_tag = bigram.split(',')[0]
        unigram_count = unigrams[first_tag]
        bigram_prob[bigram] = count/float(unigram_count)
    for bigram, probability in bigram_prob.iteritems():
        print bigram, '\t', probability
    return bigram_prob


print 'Bigrams'
bigrams = calculate_da_bigrams()
unigrams = calculate_unigrams()
bigram_probability(bigrams, unigrams)
# print 'Unigrams short and long'
# calculate_da_unigrams_short_long()
# print 'Bigrmas short and long'
# calculate_da_bigram_short_long()