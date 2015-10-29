from __future__ import division
import collections

import numpy as np
from hmmlearn.hmm import MultinomialHMM
from learning.calculate_emissions import build_emissions, calculate_emission_probability_features
from hmm_general import start_transition_probability_extraction, find_da_id, recognized_da_segments, da_predictions

__author__ = 'snownettle'
#hidden markov model


def calculate_hmm_m(training_set, test_set, taxonomy, cursor, connection, settings):
    da_id_taxonomy = find_da_id(taxonomy, cursor)
    states, start_probability, transition_probability = start_transition_probability_extraction(training_set, taxonomy)
    n_states = len(states)

    feature_list, emissions = extract_features_training_set(training_set, taxonomy, states, settings)

    # print model.transmat_
    con_pathes, test_obs, emissions = extract_features_test_set(test_set, taxonomy, feature_list, emissions, settings)

    model = MultinomialHMM(n_components=n_states)
    model._set_startprob(start_probability)
    model._set_transmat(transition_probability)
    model._set_emissionprob(emissions)
    da_predictions(test_obs, model, con_pathes, states, da_id_taxonomy, taxonomy, cursor, connection)


def update_emissions(emissions):
    new_emissions = np.hstack((emissions, np.zeros((emissions.shape[0], 1), dtype=emissions.dtype)))
    return new_emissions


def extract_features_training_set(training_set, taxonomy, states, settings):
    feature_list = list()
    emissions = collections.defaultdict(dict)
    for conversation in training_set:
        for branch in conversation:
            segments = branch.get_segments()
            for i in range(0, len(segments), 1):
                segment = segments[i]
                da = segment.get_da_by_taxonomy(taxonomy)
                feature = segment.features
                feature = convert_feature_to_list(feature, taxonomy, settings)
                feature_index = find_feature_index(feature, feature_list)
                if feature_index is None:
                    feature_list.append(feature)
                    feature_index = len(feature_list) - 1
                build_emissions(feature_index, da, emissions)
    emissions_probability = calculate_emission_probability_features(emissions, states, feature_list)

    return feature_list, emissions_probability


def extract_features_test_set(data_set, taxonomy, feature_list, emissions, settings):
    features_list = list()
    conversation_pathes_tweet_id = list()
    observations = list()
    for conversation in data_set:
        conversation_observations = list()
        conversation_path = list()
        for branch in conversation:
            branch_observations = list()
            branch_path = list()
            segments = branch.get_segments()
            for i in range(0, len(segments), 1):
                feature_branch = list()
                segment = segments[i]
                tweet_id = segment.tweet_id
                start_offset = segment.start_offset
                end_offset = segment.end_offset
                feature = segment.features
                feature = convert_feature_to_list(feature, taxonomy, settings)
                feature_index = find_feature_index(feature, feature_list)
                if feature_index is None:
                    feature_list.append(feature)
                    feature_index = len(feature_list) - 1
                    emissions = update_emissions(emissions)
                branch_path.append([tweet_id, start_offset, end_offset])
                feature_branch.append(feature)
                features_list.append(feature_branch)
                branch_observations.append(feature_index)
            conversation_observations.append(branch_observations)
            conversation_path.append(branch_path)
        conversation_pathes_tweet_id.append(conversation_path)
        observations.append(conversation_observations)

    return conversation_pathes_tweet_id, observations, emissions


def find_feature_index(feature, feature_list):
    if feature in feature_list:
        return feature_list.index(feature)
    return None


def convert_feature_to_list(feature, taxonomy, settings):
    feature_set = list()
    feature_set.append(feature.features['length'])
    feature_set.append(feature.features['root_user'])
    feature_set.append(feature.features['pos'])
    feature_set.append(feature.features['link'])
    feature_set.append(feature.features['question_mark'])
    feature_set.append(feature.features['exclamation_mark'])
    feature_set.append(feature.features['hashtag'])
    feature_set.append(feature.features['emoticons'])
    feature_set.append(feature.features['question_words'])
    feature_set.append(feature.features['first_verb'])
    feature_set.append(feature.features['imperative'])
    feature_set.append(feature.features['oder'])

    ###############################
    # language features from tf-idf
    ##############################
    if settings[2] == 2 or settings[2] == 4:
        if taxonomy == 'full':
            language_features = feature.language_features_full
        elif taxonomy == 'reduced':
            language_features = feature.language_features_reduced
        else:
            language_features = feature.language_features_minimal
        for token in language_features:
            feature_set.append(token)

    return feature_set
