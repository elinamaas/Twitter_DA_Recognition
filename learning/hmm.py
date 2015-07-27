from __future__ import division
import numpy as np
# from sklearn import hmm
from analysing_GS import features
import analysing_GS.features
import collections
from hmmlearn.hmm import MultinomialHMM

__author__ = 'snownettle'
#hidden markov model

def calculate_hmm(training_set, test_set):
    # unigrams = features.calculate_da_unigrams('full')
    taxonomy = 'full'
    unigrams = features.unigrams_training_set(training_set)

    states = find_states(unigrams) # da labels
    n_states = len(states)
    start_probability = calculate_start_probability(unigrams, states)
    transition_probability = calculate_transition_probability(training_set, states)

    # observations_length, emissions_lenght = analysing_GS.features.extract_features(training_set, taxonomy)
    # observations_root_username, emissions_username = features.extract_root_username(training_set, taxonomy)
    #
    # emission_probability_length = calculate_emission_probability_feature(emissions_lenght, states, observations_length)
    # emission_probability_root_user_name = calculate_emission_probability_feature(emissions_username,
    #                                                                              states, observations_root_username)
    #
    # emission_probability_sets = [emission_probability_length, emission_probability_root_user_name]
    # observation_all = [observations_length, observations_root_username]
    # observation_sets = itertools.product(observations_length, observations_root_username)
    # observation_sets = list(observation_sets)

    observations, emissions, observations_product = analysing_GS.features.extract_features(training_set, taxonomy, states)
    emission_probability = calculate_emission_probability(states, observations_product,
                                                          observations, emissions)

    model = MultinomialHMM(n_components=n_states)
    model._set_startprob(start_probability)
    model._set_transmat(transition_probability)
    model._set_emissionprob(emission_probability)
    test_seq = features.extract_features_test_set(test_set)
    for path_observation in test_seq:
    # bob_says = [0, 2, 4, 6, 4, 7, 3, 2]
        dialog = decode_test_observations(path_observation, observations_product)
        logprob, alice_hears = model.decode(dialog, algorithm="viterbi")
    # print "Bob says:", ", ".join(map(lambda x: str(observations[x]), bob_says))
        print "Alice hears:", ", ".join(map(lambda x: states[x], alice_hears))


def decode_test_observations(path_observation, observations_product):
    decode_observations = list()
    for observation in path_observation:
        obs = tuple(observation)
        index = observations_product.index(obs)
        decode_observations.append(index)
    return decode_observations

# def calculate_observations(training_set):
#     for conversation in training_set:
#         all_nodes = conversation.all_nodes()
#         for node in all_nodes:
#             tweet_id = node.tag
#             segment_utterance = find_segments(tweet_id)
#             segment_count += len(segments)



def find_states(unigrams):
    states = set()
    for da, count in unigrams.iteritems():
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

def calculate_transition_probability(training_set, states):
    bigrams = features.bigram_test_set(training_set)
    transitions = collections.defaultdict(list)
    # checking = 0
    for start_da, end_da_count in bigrams.iteritems():
        bigram_count = sum(end_da_count.values())
        for end_da, count in end_da_count.iteritems():
            probablity = count/float(bigram_count)
            if start_da not in transitions:
                transitions[start_da] = {}
            transitions[start_da][end_da] = probablity
        # checking += probablity
        # start_da = start_da.split(',')[0].replace(' ', '')
        # end_da = start_da.split(',')[1].replace(' ', '')
    ######
    ######  End symbol to what status?????
    ######
    # transitions['<E>'] = {}
    # print 'ch: ', checking
    # the problem is here
    # there is no <E>
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
        # h = np.array(transition_probabilitiese_list)
        # print i
        # print sum(transition_probabilitiese_list)
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
