from __future__ import division
import numpy as np
# from sklearn import hmm
from analysing_GS import features
import analysing_GS.extract_features
import analysing_GS.features
import collections
from hmmlearn.hmm import MultinomialHMM
from postgres import postgres_queries
__author__ = 'snownettle'
#hidden markov model

def calculate_hmm(training_set, test_set, taxonomy, cursor, connection):
    # unigrams = features.calculate_da_unigrams('full')
    # taxonomy = 'full'
    unigrams = analysing_GS.features.unigrams_training_set(training_set, taxonomy, cursor)

    states = find_states(unigrams) # da labels
    n_states = len(states)
    start_probability = calculate_start_probability(unigrams, states)
    transition_probability = calculate_transition_probability(training_set, states, taxonomy, cursor)

    language_features, feature_list, emissions = analysing_GS.extract_features.extract_features_training_set(
        training_set, taxonomy, states, cursor)

    # emission_probability = calculate_emission_probability(states, observations_product,
    #                                                       observations, emissions)

    model = MultinomialHMM(n_components=n_states)
    model._set_startprob(start_probability)
    model._set_transmat(transition_probability)
    test_seq, branches = analysing_GS.extract_features.extract_features_test_set(test_set, language_features, cursor)
    extracted_feature_test_set = list()
    for i in range(0, len(test_seq), 1):
        path_observation = test_seq[i]
        extraction, emissions = decode_test_observations(path_observation, feature_list, emissions)
        extracted_feature_test_set.append(extraction)

    model._set_emissionprob(emissions)
    for i in range(0, len(extracted_feature_test_set), 1):
        path_observation = extracted_feature_test_set[i]
        # dialog = decode_test_observations(path_observation, feature_list, emissions)
        logprob, alice_hears = model.decode(path_observation, algorithm="viterbi")
        # i = 0
        for j in range(0, len(alice_hears), 1):
            dialog_act_id = alice_hears[j]
        # for dialog_act_id in alice_hears:
            dialog_act_name = states[dialog_act_id]
            # print dialog_act_name
            segment = branches[i][j]
            tweet_id = str(segment[0])
            postgres_queries.update_da_prediction(dialog_act_name, tweet_id, segment[1], segment[2],
                                                  taxonomy, cursor, connection)


            # i += 1
        #print "Alice hears:", ", ".join(map(lambda x: states[x], alice_hears))
    # print "Bob says:", ", ".join(map(lambda x: str(observations[x]), bob_says))


def decode_test_observations(path_observation, feature_list, emissions):
    #check if smth doenst exixst!
    decode_observations = list()
    for observation in path_observation:
        feature_index = observation.contains_in_list(feature_list)
        if feature_index is None:
            emissions = update_emissions(emissions)
            feature_list.append(observation)
            decode_observations.append(len(feature_list) - 1)
        else:
            decode_observations.append(feature_index)
    return decode_observations, emissions


def update_emissions(emissions):
    new_emissions = np.hstack((emissions, np.zeros((emissions.shape[0], 1), dtype=emissions.dtype)))
    return new_emissions

def find_states(unigrams):
    # delete DIT++, root
    states = set()
    for da, count in unigrams.iteritems():
        if da != 'DIT++ Taxonomy':
            states.add(da)
    return list(states)


def calculate_start_probability(unigrams,states):
    start_pobability_dict = dict()
    segments_count = sum(unigrams.values())
    for da, count in unigrams.iteritems():
        probability = count/float(segments_count)
        start_pobability_dict[da] = probability
    start_pobability_list = list()
    for i in range(0, len(states), 1):
        state = states[i]
        state_prob = start_pobability_dict[state]
        start_pobability_list.append(state_prob)
    start_pobability = np.array(start_pobability_list)
    return start_pobability


def calculate_transition_probability(training_set, states, taxonomy, cursor):
    bigrams = features.bigram_test_set(training_set, taxonomy, cursor)
    transitions = collections.defaultdict(list)
    # checking = 0
    for start_da, end_da_count in bigrams.iteritems():
        bigram_count = sum(end_da_count.values())
        for end_da, count in end_da_count.iteritems():
            probablity = count/float(bigram_count)
            if start_da not in transitions:
                transitions[start_da] = {}
            transitions[start_da][end_da] = probablity
    for i in range(0, len(states), 1):
        start_state = states[i]
        transition_probabilities_dict = transitions[start_state]
        transition_probabilitiese_list = list()
        for j in range(0, len(states), 1):
            end_state = states[j]
            if start_state == '<E>':
                transition_probabilitiese_list = [0]*len(states)
                transition_probabilitiese_list[i] = 1.0
                break
            else:
                if end_state in transition_probabilities_dict:
                    transition_probabilitiese_list.append(transition_probabilities_dict[end_state])
                else:
                    transition_probabilitiese_list.append(0)
        if i == 0:
            tr_pr = np.array(transition_probabilitiese_list)
        else:
            tr_pr = np.vstack((tr_pr, np.array(transition_probabilitiese_list)))
    return tr_pr


def calculate_emission_probability(states, observation_sets, observation_all, emission_probability_sets):
    emission_probability = list()
    for i in range(0, len(states)):
        da = states[i]
        emission_probability_row = list()
        for observation_set in observation_sets:
            prob = 1
            j = 0
            for observation in observation_set:
                observation_index = observation_all[j].index(observation)
                prob *= emission_probability_sets[j][i][observation_index]
                j += 1
            # print prob
            emission_probability_row.append(prob)
        emission_probability.append(emission_probability_row)
    return emission_probability


# states = ["Rainy", "Sunny"]
# n_states = len(states)
#
# observations = ["walk", "shop", "clean"]
# n_observations = len(observations)
#
# start_probability = np.array([0.6, 0.4])
#
# transition_probability = np.array([
#   [0.7, 0.3],
#   [0.4, 0.6]
# ])
#
# emission_probability = np.array([
#   [0.1, 0.4, 0.5],
#   [0.6, 0.3, 0.1]
# ])
#
# model = hmm.MultinomialHMM(n_components=n_states)
# model._set_startprob(start_probability)
# model._set_transmat(transition_probability)
# model._set_emissionprob(emission_probability)
#
# # predict a sequence of hidden states based on visible states
# bob_says = [0, 2, 1, 1, 2, 0]
# logprob, alice_hears = model.decode(bob_says, algorithm="viterbi")
# print "Bob says:", ", ".join(map(lambda x: observations[x], bob_says))
# print "Alice hears:", ", ".join(map(lambda x: states[x], alice_hears))
#
