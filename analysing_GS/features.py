import collections
import itertools
import re

import numpy as np
import nltk

from analysing_GS.calculate_emissions import build_hashtag_emissions, build_length_utterance_emissions, \
    calculate_emission_probability_feature, build_segment_position_emissions, build_explanation_mark_emissions, \
    build_question_mark_emissions, build_root_usersname_emissions, has_link, build_link_emissions
from analysing_GS.extract_features import is_link, has_numbers, has_explanation_mark, has_hashtag, has_question_mark
from postgres.postgres_queries import count_start_conversation, count_end_conversation
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


def unigrams_training_set(training_set, taxonomy, cursor):
    number_start_symbol = len(training_set)
    unigrams = dict()
    unigrams['<S>'] = number_start_symbol
    end_symbol = '<E>'
    number_end_symbols = postgres_queries.count_end_conversation(cursor)
    unigrams[end_symbol] = number_end_symbols
    for conversation in training_set:
        all_nodes = conversation.all_nodes()
        for node in all_nodes:
            tweet_id = node.tag
            segments = postgres_queries.find_segments(tweet_id, cursor)
            for segment in segments:
                if taxonomy == 'full':
                    if segment[2] in unigrams:
                        unigrams[segment[2]] += 1
                    else:
                        unigrams[segment[2]] = 1
                elif taxonomy == 'reduced':
                    if segment[3] in unigrams:
                        unigrams[segment[3]] += 1
                    else:
                        unigrams[segment[3]] = 1
                else:
                    if segment[4] in unigrams:
                        unigrams[segment[4]] += 1
                    else:
                        unigrams[segment[4]] = 1

    return unigrams


def bigram_test_set(training_set, taxonomy, cursor):
    bigram_count = 0
    bigram_dict = collections.defaultdict(list)
    conversation_start = '<S>'
    for conversation in training_set:
        root = conversation.root
        if root is not None:
            segments = postgres_queries.find_segments(root, cursor)
            # sorted_segments = sort_segments(s_egments, 'full')
            previous_da = conversation_start
            for segment in segments:
                da = fetch_da_taxonomy(segment, taxonomy)
            # for offset, da in segments.iteritems():
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
            find_children_bigrams(root, previous_da, bigram_dict, taxonomy, cursor)
    # bigram_count = sum(bigram_dict.values())
    return bigram_dict


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


def extract_features_test_set(data_set, cursor):
    taxonomy = 'full' #it doesn_t matter which taxonomy, we make here predictions
    features_list = list()
    conversation_pathes_tweet_id = list()
    for conversation in data_set:
        root_id = conversation.root
        root_username = postgres_queries.find_username_by_tweet_id(root_id, cursor)
        all_conversation_branches = conversation.paths_to_leaves()
        # conversation_path_tweet_id.append(all_conversation_branches)
        for branch in all_conversation_branches:
            conversation_path_tweet_id = list()
            feature_branch = list()
            # t = 0
            for tweet_id in branch:
                segments = postgres_queries.find_segments_utterance(tweet_id, taxonomy, cursor)
                # t += len(segments)
                current_username = postgres_queries.find_username_by_tweet_id(tweet_id, cursor)
                same_username = (root_username == current_username)
                # segment_position_first = 0
                if same_username is True:
                    same_username = 1
                else:
                    same_username = 0
                # segments = sort_segments(segments, taxonomy)
                # for segment in segments:
                for i in range(0, len(segments), 1):
                    segment = segments[i]
                    if i == 0:
                        segment_position_first = 1
                    else:
                        segment_position_first = 0
                # for start_offset, end_offset_utterance in segments.iteritems():
                    start_offset = segment[0]
                    end_offset = segment[1]
                    link = is_link(segment[2])
                    question_mark = has_question_mark(segment[2])
                    explanation_mark = has_explanation_mark(segment[2])
                    hashtag = has_hashtag(segment[2])
                    conversation_path_tweet_id.append([tweet_id, start_offset, end_offset])
                    segment_len = end_offset - start_offset + 1
                    # add feature token - check if we have them, make as a list
                    feature_branch.append([segment_len, same_username, segment_position_first, link, question_mark, explanation_mark, hashtag])
            features_list.append(feature_branch)
            conversation_pathes_tweet_id.append(conversation_path_tweet_id)
    return features_list, conversation_pathes_tweet_id


def extract_features(training_set, taxonomy, states, cursor): #check if in the training set is only german tweets
    observations_length = set()
    emissions_length = collections.defaultdict()
    da_root_username_emissions = collections.defaultdict(dict)
    link_emissions = collections.defaultdict(dict)
    segment_position_first_emissions = collections.defaultdict(dict)
    tf_features = collections.defaultdict(dict)
    question_mark_emissions = collections.defaultdict(dict)
    explanation_mark_emissions = collections.defaultdict(dict)
    hashtag_emissions = collections.defaultdict(dict)
    observation_root_username = [0, 1] # root, not_root
    observation_segment_position = [0, 1] # first segment, not first segment
    observation_link = [0, 1] # segment has link or not
    observation_question_mark = [True, False]
    observation_explanation_mark = [True, False]
    observation_hashtags = [True, False]
    # observation_tokens = set()
    number_of_segments = 0
    idf_features = dict()
    for conversation in training_set:
        root = conversation.root
        root_username = postgres_queries.find_username_by_tweet_id(root, cursor)
        all_nodes = conversation.all_nodes()
        for node in all_nodes:
            tweet_id = node.tag
            current_username = postgres_queries.find_username_by_tweet_id(tweet_id, cursor)
            # here!!!
            segment_position_first = 0 # aka False
            segments = postgres_queries.find_segments_utterance(tweet_id, taxonomy, cursor)
            number_of_segments += len(segments)
            for i in range(0, len(segments), 1):
                segment = segments[i]
                if i == 0:
                    segment_position_first = 1 # aka true
                else:
                    segment_position_first = 0
                build_root_usersname_emissions(root_username, current_username, segment, da_root_username_emissions)
                build_length_utterance_emissions(segment, observations_length, emissions_length)
                build_segment_position_emissions(segment_position_first, segment, segment_position_first_emissions)
                build_link_emissions(segment, link_emissions)
                build_question_mark_emissions(segment, question_mark_emissions)
                build_explanation_mark_emissions(segment, explanation_mark_emissions )
                build_hashtag_emissions(segment, hashtag_emissions)

                # build_emoticons_emissions(segment, emoticons_emissions)

                # term_frequency(segment, tf_features, observation_tokens)
                # inverse_document_frequency(segment, idf_features)

    # tfidf = calculate_tfidf(tf_features)
    # for a, b in tfidf.iteritems():
    #     print sum(b.values())
    # tf = calculate_tf(tf_features)
    # idf = calculate_idf(number_of_segments, idf_features)
    # sorted_x = sorted(idf_features.items(), key=operator.itemgetter(1))
    # sorted_x.reverse()
    # delete not frequent words
    # tf_norm = tf_normalization(tf_features)
    # idf_norm = idf_normalization(tf_features, observation_tokens)
    # calculate_emission_probability_tfidf(tf_norm, idf_norm, observation_tokens, states)
    observations_length = list(observations_length)
    # observation_tokens = list(observation_tokens)
    s_count = count_start_conversation(cursor)
    emissions_length['<S>'] = {0: s_count}
    e_count = count_end_conversation(cursor)
    emissions_length['<E>'] = {0: e_count}


    # emissions_probability_tf = calculate_emission_probability_feature(tf_norm, states, observation_tokens)
    # token_observations_boolean = token_observations(observation_tokens)
    emissions_probability_length = calculate_emission_probability_feature(emissions_length, states, observations_length)
    # emission_probability_tf = calculate_emissions_unigrams(observation_tokens, token_observations_boolean, tf_norm, states)
    emissions_probability_root_username = calculate_emission_probability_feature(da_root_username_emissions,
                                                                                 states, observation_root_username)
    emissions_probability_segment_position = calculate_emission_probability_feature(segment_position_first_emissions,
                                                                                    states, observation_segment_position)
    emissions_probability_link = calculate_emission_probability_feature(link_emissions, states, observation_link)

    emissions_probability_questoin_mark = calculate_emission_probability_feature(question_mark_emissions, states, observation_question_mark)
    emissions_probability_explanation_mark = calculate_emission_probability_feature(explanation_mark_emissions, states, observation_explanation_mark)
    emissions_probability_hashtag = calculate_emission_probability_feature(hashtag_emissions, states, observation_hashtags)

    # emissionn_probability_tf = calculate_emission_probability_feature(tf_features, states, observation_tokens)

    observation = [observations_length, observation_root_username, observation_segment_position,
                   observation_link, observation_question_mark, observation_explanation_mark, observation_hashtags]
             # \
             #      + token_observations_boolean
    # arrays = [observations_length, observation_root_username, observation_segment_position, observation_link]\
             # \
             #  + token_observations_boolean
    observation_product = itertools.product(*observation)
    observation_product = list(observation_product)

    emission = [emissions_probability_length, emissions_probability_root_username,
                emissions_probability_segment_position, emissions_probability_link, emissions_probability_questoin_mark,
                emissions_probability_explanation_mark, emissions_probability_hashtag]
               # + emission_probability_tf

    # observation_product = itertools.product(observations_length, observation_root_username,
    #                                         observation_segment_position, observation_link, token_observations_boolean)
    return observation, emission, observation_product


def fetch_da_taxonomy(segment, taxonomy):
    if taxonomy == 'full':
        da = segment[2]
    elif taxonomy == 'reduced':
        da = segment[3]
    else:
        da = segment[4]
    return da


def term_frequency(segment, tf_features, observation_tokens):
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
                    if lemma in tf:
                        tf[lemma] += 1
                    else:
                        tf[lemma] = 1
                else:
                    tf_features[da][lemma] = 1


# def calculate_tf(tf_features):
#     tf_values = collections.defaultdict(dict)
#     for da, tf in tf_features.iteritems():
#         number_of_tokens = sum(tf.values())
#         for token, freq in tf.iteritems():
#             tf_values[da][token] = math.log10(1 + freq/float(number_of_tokens))
#             # tf_values[da][token] = freq/float(number_of_tokens)
#     return tf_values


# def inverse_document_frequency(segment, idf_features):
#     utterance = segment[2]
#     da = segment[3]
#     if '@' in utterance:
#         utterance = delete_username(utterance)
#     utterance = delete_non_alphabetic_symbols(utterance)
#     sentences = parse(utterance, relations=True, lemmata=True).split()
#     # tokens = utterance.split(' ')
#     for sentence in sentences:
#         for token in sentence:
#             lemma = token[5]
#             if len(lemma) > 2:
#                 if da in idf_features:
#                     idf_features[da].add(lemma)
#                 else:
#                     t = set()
#                     t.add(lemma)
#                     idf_features[da] = t


# def calculate_tfidf(tf):
#     tfidf = collections.defaultdict(dict)
#     idf = tf.copy()
#     das_list = idf.keys()
#     for da, tf_value in tf.iteritems():
#         number_of_terms = sum(tf_value.values())
#         for token, value in tf_value.iteritems():
#             nt = 0
#             for key in das_list:
#                 token_list = idf[key]
#                 if token in token_list:
#                     nt += 1
#             tfidf[da][token] = value/float(number_of_terms)*math.log10(len(das_list)/float(nt))
#     return tfidf



# def calculate_idf(number_of_segments, idf_features):
#     idf = dict()
#     for token, freq in idf_features.iteritems():
#         idf[token] = math.log10(number_of_segments/float(freq))
#     return idf


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


def token_observations(observations):
    token_obs = list()
    for token in observations:
        obs = [False, True]
        token_obs.append(obs)
    return token_obs


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



