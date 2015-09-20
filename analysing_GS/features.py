import collections
import re
import math
import operator
import copy

import numpy as np
import nltk


# from learning.feature import has_link
from postgres import postgres_queries
from pattern.de import conjugate
from pattern.de import parse, split, INFINITIVE

__author__ = 'snownettle'

# import snowballstemmer


def calculate_da_bigrams(taxonomy): #overall
    conversation_list = postgres_queries.find_conversations_root()
    bigrams = dict() #<S> for the start of the conversation
    for root in conversation_list: #query only for roots!
        start_symbol = '<S>'
        segments = postgres_queries.find_segments(root[0])
        # segments_da = sort_segments(segments)
        for segment in segments:
            da = fetch_da_taxonomy(segment, taxonomy)
        # for start_offset, da in segments_da.iteritems():
            if da != '0':
                bigram = start_symbol + ', ' + da
                start_symbol = da
                if bigram in bigrams:
                    bigrams[bigram] += 1
                else:
                    bigrams[bigram] = 1
        find_children_bigrams(root[0], start_symbol, bigrams, taxonomy)
    return bigrams


def find_children_bigrams(tweet_id, previous_da, bigrams, taxonomy, cursor):
    children = postgres_queries.find_children(tweet_id, cursor)
    previous_tweet_da = previous_da
    if len(children) == 1:
        tweet_id_child = int(children[0][0])
        segments = postgres_queries.find_segments(tweet_id_child, cursor)
        # segments_da = sort_segments(segments, 'full')
        for segment in segments:
            da = fetch_da_taxonomy(segment, taxonomy)
        # for start_offset, da in segments_da.iteritems():
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
        find_children_bigrams(tweet_id_child, previous_da, bigrams, taxonomy, cursor)
    elif len(children) > 1:
        for child in children:
            segments = postgres_queries.find_segments(int(child[0]), cursor)
            # segments_da = sort_segments(segments, 'full')
            # for start_offset, da in segments_da.iteritems():
            for segment in segments:
                da = fetch_da_taxonomy(segment, taxonomy)
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
            find_children_bigrams(int(child[0]), previous_da, bigrams, taxonomy, cursor)
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


def calculate_da_bigram_short_long(taxonomy):
    conversation_list = postgres_queries.find_conversations_root()
    # bigrams = dict() #<S> for the start of the conversation
    bigrams_short = dict()
    bigrams_long = dict()
    for root in conversation_list: #query only for roots!
        start_symbol = '<S>'
        conversation_number = root[2]
        conversation = postgres_queries.find_conversation(conversation_number)
        segments = postgres_queries.find_segments(root[0])
        # segments_da = sort_segments(segments)
        if len(conversation) >= 20:
            for segment in segments:
            # for start_offset, da in segments_da.iteritems():
                da = fetch_da_taxonomy(segment, taxonomy)
                if da != '0':
                    bigram = start_symbol + ', ' + da
                    start_symbol = da
                    if bigram in bigrams_long:
                        bigrams_long[bigram] += 1
                    else:
                        bigrams_long[bigram] = 1
            find_children_bigrams(root[0], start_symbol, bigrams_long)
        else:
            for segment in segments:
                da = fetch_da_taxonomy(segment, taxonomy)
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


# def calculate_da_lang_model_bigrams(taxonomy):
#     da_lang_model = collections.defaultdict()
#     return da_lang_model


# def bigram_test_set(training_set, taxonomy, cursor):
#     bigram_count = 0
#     bigram_dict = collections.defaultdict(list)
#     conversation_start = '<S>'
#     for conversation in training_set:
#         root = conversation.root
#         if root is not None:
#             segments = postgres_queries.find_segments(root, cursor)
#             # sorted_segments = sort_segments(s_egments, 'full')
#             previous_da = conversation_start
#             for segment in segments:
#                 da = fetch_da_taxonomy(segment, taxonomy)
#             # for offset, da in segments.iteritems():
#                 if previous_da in bigram_dict:
#                     end_da = bigram_dict[previous_da]
#                     if da in end_da:
#                         bigram_dict[previous_da][da] += 1
#                     else:
#                         bigram_dict[previous_da][da] = 1
#
#                 else:
#                     bigram_dict[previous_da] = {}
#                     bigram_dict[previous_da][da] = 1
#                 previous_da = da
#             find_children_bigrams(root, previous_da, bigram_dict, taxonomy, cursor)
#     # bigram_count = sum(bigram_dict.values())
#     return bigram_dict


# def sort_segments(segments, taxonomy):
#     #place taxonomy
#     # taxonomy = 'full'
#     unsorted_segments = dict()
#     for segment in segments:
#         start_offset = int(segment[0].split(':')[0])
#         end_offset = int(segment[0].split(':')[1])
#         if taxonomy == 'full':
#             unsorted_segments[start_offset] = (end_offset, segment[1])
#         elif taxonomy == 'reduced':
#             unsorted_segments[start_offset] = (end_offset,segment[2])
#         else:
#             unsorted_segments[start_offset] = (end_offset,segment[3])
#     sorted_segments = collections.OrderedDict(sorted(unsorted_segments.items()))
#     return sorted_segments


def fetch_da_taxonomy(segment, taxonomy):
    if taxonomy == 'full':
        da = segment[2]
    elif taxonomy == 'reduced':
        da = segment[3]
    else:
        da = segment[4]
    return da


def term_frequency_inversce_doc(segment, tf_features, idf_features, observation_tokens):
    da = segment[3]
    utterance = segment[2]
    if '@' in utterance:
        utterance = delete_username(utterance)
    if has_link(utterance):
        utterance = delete_link(utterance)
    utterance = delete_non_alphabetic_symbols(utterance)
    sentences = parse(utterance, relations=True, lemmata=True).split()
    # tokens = utterance.split(' ')
    for sentence in sentences:
        for token in sentence:
            lemma = token[5]
            if len(lemma) > 2:
                observation_tokens.add(lemma)
                if da in tf_features:
                    tf = tf_features[da]
                    idf_features[da].add(lemma)
                    if lemma in tf:
                        tf[lemma] += 1
                    else:
                        tf[lemma] = 1
                else:
                    tf_features[da][lemma] = 1
                    t = set()
                    t.add(lemma)
                    idf_features[da] = t


def calculate_tf(tf_features):
    tf_values = collections.defaultdict(dict)
    for da, tf in tf_features.iteritems():
        number_of_tokens = sum(tf.values())
        for token, freq in tf.iteritems():
            tf_values[da][token] = math.log10(1 + freq/float(number_of_tokens))
            # tf_values[da][token] = freq/float(number_of_tokens)
    return tf_values


def inverse_document_frequency(segment, idf_features):
    utterance = segment[2]
    da = segment[3]
    if '@' in utterance:
        utterance = delete_username(utterance)
    utterance = delete_non_alphabetic_symbols(utterance)
    sentences = parse(utterance, relations=True, lemmata=True).split()
    # tokens = utterance.split(' ')
    for sentence in sentences:
        for token in sentence:
            lemma = token[5]
            if len(lemma) > 2:
                if da in idf_features:
                    idf_features[da].add(lemma)
                else:
                    t = set()
                    t.add(lemma)
                    idf_features[da] = t


def calculate_tfidf(tf_features, idf_features):
    tfidf = collections.defaultdict(dict)
    idf_keys = idf_features.values()
    das_list = idf_features.keys()
    for da, term_freq in tf_features.iteritems():
        for token, freq in term_freq.iteritems():
            nt = 0
            for idf in idf_keys:
                if token in idf:
                    nt += 1
            tfidf[da][token] = freq * math.log10(len(das_list)/float(nt))
    return tfidf


def delete_non_alphabetic_symbols(token):
    if has_numbers(token):
        token = re.sub('\d', '', token)
    chars_to_remove = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '[', ']', '{', '}', ';', ':', ',', '.',
                       '/', '<', '>', '?', '`', '\\', '~', '-', '=', '_', '+''|', u'\xe2', u'\x80', u'\xa6']
    rx = '[' + re.escape(''.join(chars_to_remove)) + ']'
    return re.sub(rx, ' ', token).lower()
    # pattern = re.compile('[!@#$%^&*()[]{};:,./<>?\|`~-=_+]')
    # return pattern.sub('', token).lower()


def lemmatize(token):
    l = parse(token)
    k = split(l)
    print conjugate(token, INFINITIVE)


def delete_username(utterance):
    new_utterance = ''
    tokens = utterance.split(' ')
    for token in tokens:
        if '@' not in token:
            new_utterance += token + ' '
    return new_utterance[:-1]


def delete_link(utterance):
    new_utterance = ''
    tokens = utterance.split(' ')
    for token in tokens:
        if 'http:' not in token:
            new_utterance += token + ' '
    return new_utterance[:-1]


def tf_normalization(terms_frequency):
    tf_norm = collections.defaultdict(dict)
    for da, term_freq in terms_frequency.iteritems():
        total_number_of_terms = sum(term_freq.values())
        for token, freq in term_freq.iteritems():
            tf_norm[da][token] = freq/float(total_number_of_terms)
    return tf_norm


# def idf_normalization(terms_frequency, observation_tokens):
#     idf_norm = dict()
#     total_numbers_of_documents = len(terms_frequency)
#     dialog_acts = terms_frequency.keys()
#     for token in observation_tokens:
#         number_doc_with_term = 0
#         for da in dialog_acts:
#             term_freq = terms_frequency[da]
#             if token in term_freq:
#                 number_doc_with_term += 1
#         idf_norm[token] = 1 + math.log(total_numbers_of_documents/float(number_doc_with_term))
#     return idf_norm


# def calculate_emission_probability_tfidf(tf_norm, idf_norm, observations, states):
#     for i in range(0, len(states),1):
#         state = states[i]
#         terms_freq = tf_norm[state]
#         tfidf_for_one_state = list()
#         for observation in observations:
#             if observation in terms_freq:
#                 tfidf = terms_freq[observation]*idf_norm[observation]
#             else:
#                 tfidf = 0
#             tfidf_for_one_state.append(tfidf)
#         if i == 0:
#             print sum(tfidf_for_one_state)
#             emission_probability = np.array(tfidf_for_one_state)
#         else:
#             print sum(tfidf_for_one_state)
#             emission_probability = np.vstack((emission_probability, tfidf_for_one_state))
#     return emission_probability


# def token_observations(observations):
#     token_obs = list()
#     for token in observations:
#         obs = [False, True]
#         token_obs.append(obs)
#     return token_obs


def calculate_emissions_unigrams(token_observations, token_observations_boolean, tf, states):
    new_tf_dict = dict()
    for i in range(0, len(states), 1):
        state = states[i]
        bool_tokens_emissions = list()
        for j in range(0, len(token_observations), 1):
            token = token_observations[j]
            if state in tf:
                tf_norm = tf[state]
                if token in tf_norm:
                    value = tf_norm[token]
                    emission = [1-value, value]
                    bool_tokens_emissions.append(emission)
                else:
                    emission = [1, 0]
                    bool_tokens_emissions.append(emission)
            else:
                emission = [0, 0]
                bool_tokens_emissions.append(emission)

        new_tf_dict[state] = bool_tokens_emissions
    emissions_list = list()
    for j in range(0, len(token_observations), 1):
        for i in range(0, len(states), 1):
            state = states[i]
            if i == 0:
                emission_probability = np.array(new_tf_dict[state][j])
            else:
                emission_probability = np.vstack((emission_probability, new_tf_dict[state][j]))
        emissions_list.append(emission_probability)
    return emissions_list


def is_username(token):
    if '@' in token:
        return 1
    else:
        return 0


def has_numbers(input_string):
    return bool(re.search(r'\d', input_string))


def delete_conjuction(utterance):
    conjuction_list = ['und', 'oder', 'aber']
    utterance = utterance.lower()
    tokens = utterance.split(' ')
    if tokens[0] in conjuction_list:
        return utterance.split(' ', 1)[1]
    else:
        return utterance


def choose_word_features(tfidf):
    words_set = set()
    for da, tfidf_value in tfidf.iteritems():
        sorted_x = sorted(tfidf_value.items(), key=operator.itemgetter(1))
        sorted_x.reverse()
        # leave top 5
        i = 0
        for tf in sorted_x:
            if i == 100:
                break
            else:
                words_set.add(tf[0])
            i += 1
    words_list = list(words_set)
    return words_list


def delete_tokens(tf_features, observation_tokens):
    new_tf_features = copy.deepcopy(tf_features)
    for da, tf_value in tf_features.iteritems():
        for token, value in tf_value.iteritems():
            if token not in observation_tokens:
                del new_tf_features[da][token]
    return new_tf_features


def is_link(utterance):
    if 'http:' in utterance:
        return 1
    else:
        return 0


def has_link(utterance):
    if 'http:' in utterance:
        return True
    else:
        return False
