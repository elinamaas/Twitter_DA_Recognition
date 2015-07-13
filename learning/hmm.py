from __future__ import division
import numpy as np
# from sklearn import hmm
from analysing_GS import features
from postgres import postgres_queries
from da_recognition import dialogue_acts_taxonomy
import collections
from hmmlearn.hmm import MultinomialHMM
__author__ = 'snownettle'
#hidden markov model

def calculate_hmm(training_set, test_set):
    # unigrams = features.calculate_da_unigrams('full')
    taxonomy = 'full'
    unigrams = features.unigrams_training_set(training_set)

    states = find_states(unigrams)
    n_states = len(states)
    start_probability = calculate_start_probability(unigrams, states)
    transition_probability = calculate_transition_probability(training_set, states)
    observations, emissions = postgres_queries.lenght_feature_segments_utterance(training_set, taxonomy)
    emission_probability = calculate_emission_probability(emissions, states, observations)

    model = MultinomialHMM(n_components=n_states)
    model._set_startprob(start_probability)
    model._set_transmat(transition_probability)
    model._set_emissionprob(emission_probability)
    test_seq = features.extract_length_feature(test_set)
    for dialog in test_seq:
    # bob_says = [0, 2, 4, 6, 4, 7, 3, 2]
        logprob, alice_hears = model.decode(dialog, algorithm="viterbi")
    # print "Bob says:", ", ".join(map(lambda x: str(observations[x]), bob_says))
        print "Alice hears:", ", ".join(map(lambda x: states[x], alice_hears))

def calculate_emission_probability(emissions, states, observations):
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

    # for da, len_freq in emissions.iteritems():
    #     occurancy = sum(len_freq.values())
    #     for len, freq in len_freq.iteritems():
    #         freq = freq/float(occurancy)
    #         emissions[da][len] = freq
    return emission_probability

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
