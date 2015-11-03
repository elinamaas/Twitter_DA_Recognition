from __future__ import division
import collections
import numpy as np
from sklearn.datasets.samples_generator import make_spd_matrix
from hmmlearn.hmm import GaussianHMM
from hmm_general import start_transition_probability_extraction
from learning.hmm_general import find_da_id, da_predictions
from math import pow

__author__ = 'snownettle'
#hidden markov model


def calculate_hmm_g(training_set, test_set, taxonomy, cursor, connection, settings):
    da_id_taxonomy = find_da_id(taxonomy, cursor)
    states, start_probability, transition_probability = start_transition_probability_extraction(training_set, taxonomy)
    n_states = len(states)

    feature_list = extract_features_training_set_gaus(training_set, taxonomy, settings)
    n_features = len(feature_list[states[0]][0])
    mean = calculate_means(states, feature_list, n_features)
    covariance = calculate_covariance(states, feature_list, n_features)
    # covariance = diag_cov(states, feature_list, n_features, mean)

    model = GaussianHMM(n_components=n_states, covariance_type='full')
    model.startprob_ = start_probability
    model.transmat_ = transition_probability
    model.means_ = mean
    model.covars_ = covariance

    test_seq, con_pathes = extract_features_test_set_gaus(test_set, taxonomy, settings)
    da_predictions(test_seq, model, con_pathes, states, da_id_taxonomy, taxonomy, cursor, connection)


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
    # due to shortage of data we can't calculate the covariance matrix, that's why we return random

    np.set_printoptions(threshold='nan')
    random = np.array([make_spd_matrix(n_features, random_state=0) + np.eye(n_features) for x in range(len(states))])
    # covariance = list()
    # for i in range(0, len(states), 1):
    #     state = states[i]
    #     f_list_da = feature_list[state]
    #     # feat_transpose = np.transpose(f_list_da)
    #     arr = np.cov(np.array(f_list_da), rowvar=0)
    #     # adjusted_cov = arr + 0.2*np.identity(arr.shape[0])
    #     if np.isnan(arr).all():
    #         arr = random[i]
    #     # arr_tr = np.transpose(arr)
    #     # new_arr = np.multiply(arr, arr_tr)
    #
    #     # arr[arr == 0.] = 0.00001
    #     # covariance.append(new_arr)

    #     # diagonal = arr.diagonal()
    #     # print (arr.transpose() == arr).all()
    #     a = 0
    #     while not is_pos_def(arr):
    #         arr += 0.2
    #         a += 1
    #         if a == 10:
    #             arr = random[i]
    #     if not (arr.transpose() == arr).all():
    #         arr = make_summetric(arr)

    #     # np.linalg.cholesky(arr)
    #     covariance.append(arr)
    #     # t = np.linalg.cholesky(adjusted_cov)
    # covariance = np.array(covariance)

    #
    # np.linalg.cholesky(covariance)
    # # covariance_tr = np.transpose(covariance)
    # # cov = np.multiply(covariance, covariance_tr)
    # return covariance

    return random


def diag_cov(states, feature_list, n_features, means):
    diag_covariance = list()
    for i in range(0, len(states), 1):
        da_valus_feature = list()
        state = states[i]
        f_list_da = feature_list[state]
        # feat_transpose = np.transpose(f_list_da)
        # arr = np.cov(np.array(f_list_da), rowvar=0)
        for j in range(0, n_features, 1):
            sigma = 0
            for k in range(0, len(f_list_da), 1):
                sigma += pow((f_list_da[k][j] - means[i][j]), 2)
            value = sigma/float(len(f_list_da))
            if value == 0:
                value = 0.001
            da_valus_feature.append(value)
        diag_covariance.append(da_valus_feature)
    diag_covariance = np.array(diag_covariance)
    # print diag_covariance
    return diag_covariance


def make_summetric(array):
    return array + array.T
    # for i in range(0, array.shape[0], 1):
    #     for j in range(0, array.shape[0], 1):
    #         array[j][i] = array[i][j]
    #     i +=1
    # return array


def is_pos_def(x):
    return np.all(np.linalg.eigvals(x) > 0)


def extract_features_training_set_gaus(training_set, taxonomy, settings):
    means = collections.defaultdict(list)
    for conversation in training_set:
        for branch in conversation:
            segments = branch.get_segments()
            for i in range(0, len(segments), 1):
                segment = segments[i]
                da = segment.get_da_by_taxonomy(taxonomy)
                feature = segment.features
                feature_set = convert_features(feature, taxonomy, settings)
                means[da].append(feature_set)

    return means


def convert_features(feature, taxonomy, settings):
    # convert bolleans to +1 (True) and -1 (False)

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
    feature_set.append(convert_values(feature.features['oder']))

    if settings[2] == 2 or settings[2] == 4:
        ###############################
        # language features form tf-idf
        ##############################
        if taxonomy == 'full':
            language_features = feature.language_features_full
        elif taxonomy == 'reduced':
            language_features = feature.language_features_reduced
        else:
            language_features = feature.language_features_minimal
        for token in language_features:
            feature_set.append(convert_values(token))
    elif settings[2] == 3:
        ###########################
        # words embeddings
        ##########################
        for v in feature.word2vec:
            feature_set.append(v)

    return feature_set


def extract_features_test_set_gaus(data_set, taxonomy, settings):
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
                feature_set = convert_features(feature, taxonomy, settings)
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
