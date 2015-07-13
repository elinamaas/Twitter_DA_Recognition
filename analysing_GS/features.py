__author__ = 'snownettle'
from postgres import postgres_queries
import collections
import nltk


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


# def sort_segments(db_segments):
#     segments_dict = dict()
#     for segment in db_segments:
#         offset = segment[0]
#         da = segment[1]
#         start_offset = int(offset.split(':')[0])
#         segments_dict[start_offset] = da
#     new_segments_dict = collections.OrderedDict(sorted(segments_dict.items()))
#     return new_segments_dict


def find_children(tweet_id, previous_da, bigrams ):
    children = postgres_queries.find_children(tweet_id)
    previous_tweet_da = previous_da
    if len(children) == 1:
        tweet_id_child = int(children[0][0])
        segments = postgres_queries.find_segments(tweet_id_child)
        segments_da = sort_segments(segments, 'full')
        for start_offset, da in segments_da.iteritems():
            if previous_da in bigrams:
                end_da = bigrams[previous_da]
                if da in end_da:
                    bigrams[previous_da][da] += 1
                else:
                    bigrams[previous_da][da] = 1
            else:
                bigrams[previous_da] = {}
                bigrams[previous_da][da] = 1
            previous_da = da
            # # if da != '0':
            # bigram = previous_da + ', ' + da
            # # bigram_count += 1
            # if bigram in bigrams:
            #     bigrams[bigram] += 1
            # else:
            #     bigrams[bigram] = 1
        find_children(tweet_id_child, previous_da, bigrams)
    elif len(children) > 1:
        for child in children:
            # start_symbol = previous_tweet_da
            segments = postgres_queries.find_segments(int(child[0]))
            segments_da = sort_segments(segments, 'full')
            for start_offset, da in segments_da.iteritems():
                if previous_da in bigrams:
                    end_da = bigrams[previous_da]
                    if da in end_da:
                        bigrams[previous_da][da] += 1
                    else:
                        bigrams[previous_da][da] = 1
                else:
                    bigrams[previous_da] = {}
                    bigrams[previous_da][da] = 1
                previous_da = da
                # # if da != '0':
                # bigram = start_symbol + ', ' + da
                # # bigram_count += 1
                # start_symbol = da
                # if bigram in bigrams:
                #     bigrams[bigram] += 1
                # else:
                #     bigrams[bigram] = 1
            find_children(int(child[0]), previous_da, bigrams)
    else:
        end_symbol = '<E>'
        if previous_da in bigrams:
            end_da = bigrams[previous_da]
            if end_symbol in end_da:
                bigrams[previous_da][end_symbol] += 1
            else:
                bigrams[previous_da][end_symbol] = 1
        else:
            bigrams[previous_da] = {}
            bigrams[previous_da][end_symbol] = 1
        # bigram = previous_da + ', ' + end_symbol
        # if bigram in bigrams:
        #     bigrams[bigram] += 1
        # else:
        #     bigrams[bigram] = 1


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


def calculate_da_unigrams(taxonomy):
    unigrams = dict()
    pg_unigrams = postgres_queries.find_da_unigrams(taxonomy)
    for unigram in pg_unigrams:
        if unigram[1] in unigrams:
            unigrams[unigram[1]] += unigram[0]
        else:
            unigrams[unigram[1]] = unigram[0]
    unigrams['<S>'] = 172 # the number of conversation in golden statdard
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


def calculate_da_lang_model_unigrams(taxonomy):
    results = postgres_queries.find_utterance(taxonomy)
    da_lang_model = collections.defaultdict()
    for result in results:
        tokens = nltk.word_tokenize(result[0])
        if result[1] in da_lang_model:
            token_freq = da_lang_model[result[1]]
            for token in tokens:
                if token in token_freq:
                    token_freq[token] += 1
                else:
                    token_freq[token] = 1
        else:
            token_freq = dict()
            for token in tokens:
                token_freq[token] = 1
                da_lang_model[result[1]] = token_freq
    return da_lang_model


def calculate_da_lang_model_bigrams(taxonomy):
    da_lang_model = collections.defaultdict()
    return da_lang_model

def unigrams_training_set(training_set):
    number_start_symbol = len(training_set)
    unigrams = dict()
    unigrams['<S>'] = number_start_symbol
    end_symbol = '<E>'
    number_end_symbols = postgres_queries.count_end_conversation()
    unigrams[end_symbol] = number_end_symbols
    for conversation in training_set:
        all_nodes = conversation.all_nodes()
        for node in all_nodes:
            tweet_id = node.tag
            segments = postgres_queries.find_segments(tweet_id)
            # which taxonomy?
            #full taxonomy
            for segment in segments:
                if segment[1] in unigrams:
                    unigrams[segment[1]] += 1
                else:
                    unigrams[segment[1]] = 1
    return unigrams

def bigram_test_set(training_set):
    bigram_count = 0
    bigram_dict = collections.defaultdict(list)
    conversation_start = '<S>'
    for conversation in training_set:
        root = conversation.root
        if root is not None:
            segments = postgres_queries.find_segments(root)
            sorted_segments = sort_segments(segments, 'full')
            previous_da = conversation_start
            for offset, da in sorted_segments.iteritems():
                if previous_da in bigram_dict:
                    end_da = bigram_dict[previous_da]
                    if da in end_da:
                        bigram_dict[previous_da][da] += 1
                    else:
                        bigram_dict[previous_da][da] = 1

                else:
                    bigram_dict[previous_da] = {}
                    bigram_dict[previous_da][da] = 1
                previous_da = da
            find_children(root, previous_da, bigram_dict)
    # bigram_count = sum(bigram_dict.values())
    return bigram_dict

def sort_segments(segments, taxonomy):
    #place taxonomy
    taxonomy = 'full'
    unsorted_segments = dict()
    for segment in segments:
        start_offset = int(segment[0].split(':')[0])
        if taxonomy == 'full':
            unsorted_segments[start_offset] = segment[1]
        elif taxonomy == 'reduced':
            unsorted_segments[start_offset] = segment[2]
        else:
            unsorted_segments[start_offset] = segment[3]
    sorted_segments = collections.OrderedDict(sorted(unsorted_segments.items()))
    return sorted_segments


def extract_length_feature(data_set):
    utterance_length_conversations_list = list()
    for conversation in data_set:
        utterance_length_in_one_conversation = list()
        root = conversation.root
        if root is not None:
            segments = postgres_queries.find_segments_utterance(root)
            sorted_segments = sort_segments(segments, 'full')
            for segment, utterance in sorted_segments.iteritems():
                length = len(nltk.word_tokenize(utterance))
                utterance_length_in_one_conversation.append(length)
        if len(utterance_length_in_one_conversation) != 0:
            utterance_length_conversations_list.append(utterance_length_in_one_conversation)
    return utterance_length_conversations_list


# calculate_da_lang_model_unigrams('full')
# calculate_da_unigrams('full')
# print 'Bigrams'
# bigrams = calculate_da_bigrams()
# unigrams = calculate_da_unigrams()
# bigram_probability(bigrams, unigrams)
# print 'Unigrams short and long'
# calculate_da_unigrams_short_long()
# print 'Bigrmas short and long'
# calculate_da_bigram_short_long()