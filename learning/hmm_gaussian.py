from __future__ import division
import collections

import numpy as np
from sklearn.datasets.samples_generator import make_spd_matrix
from hmmlearn.hmm import GaussianHMM

from hmm_general import start_transition_probability_extraction
from learning.hmm_general import find_da_id
from postgres import update_table

__author__ = 'snownettle'
#hidden markov model


def calculate_hmm_g(training_set, test_set, taxonomy, cursor, connection):
    da_id_taxonomy = find_da_id(taxonomy, cursor)
    states, start_probability, transition_probability = start_transition_probability_extraction(training_set, taxonomy)
    n_states = len(states)

    feature_list = extract_features_training_set_gaus(training_set, taxonomy)
    n_features = len(feature_list[states[0]][0])
    mean = calculate_means(states, feature_list, n_features)
    covariance = calculate_covariance(states, feature_list, n_features)

    model = GaussianHMM(n_components=n_states, covariance_type='full')
    model.startprob_ = start_probability
    model.transmat_ = transition_probability
    model.means_ = mean
    model.covars_ = covariance
    # model._set_startprob(start_probability)
    # model._set_transmat(transition_probability)
    # model._set_means(mean)
    # model._set_covars(covariance)

    test_seq, con_pathes = extract_features_test_set_gaus(test_set, taxonomy)
    recognized_segmments_da = ()
    for i in range(0, len(test_seq), 1): # conversation level
        for j in range(0, len(test_seq[i]), 1): # branch level
            brach_features = test_seq[i][j]
            logprob, alice_hears = model.decode(brach_features, algorithm="viterbi")
            path_observation = con_pathes[i][j]
            recognized_segmments_da = recognized_da_segments(recognized_segmments_da, alice_hears, states, da_id_taxonomy,  path_observation)
    update_table.update_da_prediction_bulk(recognized_segmments_da, taxonomy, cursor, connection)


def recognized_da_segments(recognized_segmments_da, da_list, states, da_id_taxonomy, path_observation):
    for i in range(0, len(da_list), 1):
        da = da_list[i]
        dialog_act_name = states[da]
        path = path_observation[i]
        da_id = da_id_taxonomy[dialog_act_name]
        tuple_da_segment = (da_id, path[0], path[1], path[2])
        recognized_segmments_da = recognized_segmments_da + (tuple_da_segment,)
    return recognized_segmments_da


def calculate_means(states, means_list, n_feature):
    l = 0
    for state in states:
        da_mean = [0]*n_feature
        x = list()
        features_list = means_list[state]
        for feature in features_list:
            for j in range(0, n_feature, 1):
                value = feature[j] + da_mean[j]
                x.append(value)
            da_mean = x
            x = list()
        np_mean = np.array(da_mean)
        da_mean = np_mean/float(len(features_list))
        if l == 0:
            mean = np.array(da_mean)
        else:
            mean = np.vstack((mean, np.array(da_mean)))
        l = 1
    return mean


def calculate_covariance(states, feature_list, n_features):
    # should be cheched. rewrite. no it doesnt work, that's why we return random
    random = np.array([make_spd_matrix(n_features, random_state=0) + np.eye(n_features) for x in range(len(states))])

    # covariance = list()
    # for i in range(0, len(states), 1):
    #     state = states[i]
    #     f_list_da = feature_list[state]
    #     feat_transpose = np.transpose(f_list_da)
    #     a = np.cov(feat_transpose)
    #     if np.isnan(a).all():
    #         a = random[i]
    #     covariance.append(a)
    # covariance = np.array(covariance)
    # return covariance

    return random


def extract_features_training_set_gaus(training_set, taxonomy):
    means = collections.defaultdict(list)
    for conversation in training_set:
        for branch in conversation:
            segments = branch.get_segments()
            for i in range(0, len(segments), 1):
                segment = segments[i]
                da = segment.get_da_by_taxonomy(taxonomy)
                feature = segment.features
                feature_set = convert_features(feature, taxonomy)
                means[da].append(feature_set)

    return means


def convert_features(feature, taxonomy):
    feature_set = list()
    feature_set.append(feature.features['length'])
    feature_set.append(convert_values(feature.features['root_user']))
    feature_set.append(feature.features['pos'])
    feature_set.append(convert_values(feature.features['link']))
    feature_set.append(convert_values(feature.features['question_mark']))
    feature_set.append(convert_values(feature.features['exclamation_mark']))
    feature_set.append(convert_values(feature.features['hashtag']))
    feature_set.append(convert_values(feature.features['emoticons']))
    feature_set.append(convert_values(feature.features['question_words']))
    feature_set.append(convert_values(feature.features['first_verb']))
    feature_set.append(convert_values(feature.features['imperative']))

    # for v in feature.word2vec:
    #     feature_set.append(v)
    # if taxonomy == 'full':
    #     language_features = feature.language_features_full
    # elif taxonomy == 'reduced':
    #     language_features = feature.language_features_reduced
    # else:
    #     language_features = feature.language_features_minimal
    # for token in language_features:
    #     feature_set.append(convert_values(token))

    return feature_set


def extract_features_test_set_gaus(data_set, taxonomy):
    feature_list_conversations = list()
    conversations_pathes = list()
    for conversation in data_set:
        features_list = list()
        conversation_coordinate = list()
        for branch in conversation:
            segments = branch.get_segments()
            feature_branch = list()
            coordinate_branch = list()
            for i in range(0, len(segments), 1):
                segment = segments[i]
                tweet_id = segment.tweet_id
                start_offset = segment.start_offset
                end_offset = segment.end_offset
                feature = segment.features
                feature_set = convert_features(feature, taxonomy)
                segment_coordinate = (tweet_id, start_offset, end_offset)
                feature_branch.append(feature_set)
                coordinate_branch.append(segment_coordinate)
            features_list.append(feature_branch)
            conversation_coordinate.append(coordinate_branch)
        feature_list_conversations.append(features_list)
        conversations_pathes.append(conversation_coordinate)

    return feature_list_conversations, conversations_pathes


def convert_values(value):
    if value is True:
        return 1
    else:
        return -1
