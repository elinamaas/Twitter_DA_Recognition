import numpy as np

__author__ = 'snownettle'
from nltk import WhitespaceTokenizer
from postgres.postgres_queries import find_utterance_tweet, count_start_conversation, count_end_conversation

from postgres import postgres_queries
import collections
import nltk
import itertools


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
        find_children_bigrams(root[0], start_symbol, bigrams)
    return bigrams


def find_children_bigrams(tweet_id, previous_da, bigrams):
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
        find_children_bigrams(tweet_id_child, previous_da, bigrams)
    elif len(children) > 1:
        for child in children:
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
            find_children_bigrams(int(child[0]), previous_da, bigrams)
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
            find_children_bigrams(root[0], start_symbol, bigrams_long)
        else:
            for start_offset, da in segments_da.iteritems():
                if da != '0':
                    bigram = start_symbol + ', ' + da
                    start_symbol = da
                    if bigram in bigrams_short:
                        bigrams_short[bigram] += 1
                    else:
                        bigrams_short[bigram] = 1
            find_children_bigrams(root[0], start_symbol, bigrams_short)

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


def unigrams_training_set(training_set, taxonomy):
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
                if taxonomy == 'full':
                    if segment[1] in unigrams:
                        unigrams[segment[1]] += 1
                    else:
                        unigrams[segment[1]] = 1
                elif taxonomy=='reduced':
                    if segment[2] in unigrams:
                        unigrams[segment[2]] += 1
                    else:
                        unigrams[segment[2]] = 1
                else:
                    if segment[3] in unigrams:
                        unigrams[segment[3]] += 1
                    else:
                        unigrams[segment[3]] = 1

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
            find_children_bigrams(root, previous_da, bigram_dict)
    # bigram_count = sum(bigram_dict.values())
    return bigram_dict


def sort_segments(segments, taxonomy):
    #place taxonomy
    # taxonomy = 'full'
    unsorted_segments = dict()
    for segment in segments:
        start_offset = int(segment[0].split(':')[0])
        end_offset = int(segment[0].split(':')[1])
        if taxonomy == 'full':
            unsorted_segments[start_offset] = (end_offset, segment[1])
        elif taxonomy == 'reduced':
            unsorted_segments[start_offset] = (end_offset,segment[2])
        else:
            unsorted_segments[start_offset] = (end_offset,segment[3])
    sorted_segments = collections.OrderedDict(sorted(unsorted_segments.items()))
    return sorted_segments


def extract_features_test_set(data_set):
    taxonomy = 'full' #it doesn_t matter which taxonomy, we make here predictions
    features_list = list()
    conversation_pathes_tweet_id = list()
    for conversation in data_set:
        root_id = conversation.root
        root_username = postgres_queries.find_username_by_tweet_id(root_id)
        all_conversation_branches = conversation.paths_to_leaves()
        # conversation_path_tweet_id.append(all_conversation_branches)
        for branch in all_conversation_branches:
            conversation_path_tweet_id = list()
            feature_branch = list()
            # t = 0
            for tweet_id in branch:
                segments = postgres_queries.find_segments_utterance(tweet_id, taxonomy)
                # t += len(segments)
                current_username = postgres_queries.find_username_by_tweet_id(tweet_id)
                same_username = (root_username == current_username)
                if same_username is True:
                    same_username = 1
                else:
                    same_username = 0
                segments = sort_segments(segments, taxonomy)
                for start_offset, end_offset_utterance in segments.iteritems():
                    end_offset = end_offset_utterance[0]
                    conversation_path_tweet_id.append([tweet_id, str(str(start_offset) + ':' + str(end_offset))])
                    segment_len = end_offset - start_offset + 1
                    if segment_len > 24:
                        print tweet_id
                        print 'there'
                    # segment_len = len(nltk.word_tokenize(utterance))
                    # if '@' in utterance:
                    #     segment_len = len(WhitespaceTokenizer().tokenize(utterance))
                    feature_branch.append([segment_len, same_username])
            features_list.append(feature_branch)
            conversation_pathes_tweet_id.append(conversation_path_tweet_id)
    return features_list, conversation_pathes_tweet_id


def extract_features(training_set, taxonomy, states): #check if in the training set is only german tweets
    observations_length = set()
    emissions_length = collections.defaultdict()
    da_root_username_emissions = collections.defaultdict(dict)
    observation_root_username = [0, 1] # root, not_root
    for conversation in training_set:
        root = conversation.root
        root_username = postgres_queries.find_username_by_tweet_id(root)
        all_nodes = conversation.all_nodes()
        for node in all_nodes:
            tweet_id = node.tag
            current_username = postgres_queries.find_username_by_tweet_id(tweet_id)
            # here!!!

            segments = postgres_queries.find_segments_utterance(tweet_id, taxonomy)
            for segment in segments:
                build_root_usersname_emissions(root_username, current_username, segment, da_root_username_emissions)
                build_length_utterance_emissions(segment, observations_length, emissions_length)

    observations_length = list(observations_length)
    s_count = count_start_conversation()
    emissions_length['<S>'] = {0:s_count}
    e_count = count_end_conversation()
    emissions_length['<E>'] = {0:e_count}
    emissions_probability_length = calculate_emission_probability_feature(emissions_length, states, observations_length)
    emissions_probability_root_username = calculate_emission_probability_feature(da_root_username_emissions,
                                                                                 states, observation_root_username)
    observation = [observations_length, observation_root_username]
    emission = [emissions_probability_length, emissions_probability_root_username]
    observation_product = itertools.product(observations_length, observation_root_username)
    observation_product = list(observation_product)
    return observation, emission, observation_product


def build_root_usersname_emissions(root_username, current_username, segment, da_root_username_emissions):
    """

    :type da_root_username_emissions: collections.defaultdict(dict)
    """
    same_username = (root_username == current_username)
    if same_username is True:
        same_username = 1
    else:
        same_username = 0
    da = segment[2]
    if da in da_root_username_emissions:
        if same_username in da_root_username_emissions[da]:
            da_root_username_emissions[da][same_username] += 1
        else:
            da_root_username_emissions[da][same_username] = 1
    else:
        da_root_username_emissions[da][same_username] = 1


def build_length_utterance_emissions(segment, observations_length, emissions_length):
    start_offset = int(segment[0].split(':')[0])
    end_offset = int(segment[0].split(':')[1])
    segment_len = end_offset - start_offset + 1
    # if '@' in segment[0]:
    #     segment_len = len(WhitespaceTokenizer().tokenize(segment[0]))
    observations_length.add(segment_len)
    if segment[2] in emissions_length:
        da_utterance_len = emissions_length[segment[2]]
        if segment_len in da_utterance_len:
            da_utterance_len[segment_len] += 1
        else:
            da_utterance_len[segment_len] = 1
            # emissions[segment[1]] = {segment_len:1}
    else:
        da_utterance_len = dict()
        da_utterance_len[segment_len] = 1
        emissions_length[segment[2]] = da_utterance_len


def calculate_emission_probability_feature(emissions, states, observations):
    for i in range(0, len(states), 1):
        occurancy = emissions[states[i]]
        total_number = sum(occurancy.values())
        probabilities = list()
        for j in range(0, len(observations), 1):
            if observations[j] in occurancy:
                pr = occurancy[observations[j]]/float(total_number)
                probabilities.append(pr)
            else:
                probabilities.append(0)
        if i == 0:
            emission_probability = np.array(probabilities)
        else:
            emission_probability = np.vstack((emission_probability, probabilities))
    return emission_probability
