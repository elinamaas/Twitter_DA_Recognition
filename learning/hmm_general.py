import collections
import numpy as np
from postgres import postgres_queries, update_table

__author__ = 'snownettle'


def start_transition_probability_extraction(training_set, taxonomy):
    unigrams, start_probability, bigrams = extract_da_features(training_set, taxonomy)
    states = find_states(unigrams) # da labels
    start_probability = calculate_start_probability(start_probability, states)
    transition_probability = calculate_transition_probability(bigrams, states)
    return states, start_probability, transition_probability


def extract_da_features(training_set, taxonomy):
    unigrams = dict()
    bigram_dict = collections.defaultdict(dict)
    start_probability = dict()
    for conversation in training_set:
        for branch in conversation:
            previous_da = None
            start_segment = branch.start_segment()
            da_start = start_segment.get_da_by_taxonomy(taxonomy)
            if da_start in start_probability:
                start_probability[da_start] += 1
            else:
                start_probability[da_start] = 1
            segments = branch.get_segments()
            for segment in segments:
                da = segment.get_da_by_taxonomy(taxonomy)
                if da in unigrams:
                    unigrams[da] += 1
                else:
                    unigrams[da] = 1
                if previous_da is None:
                    previous_da = da
                else:
                    if previous_da in bigram_dict:
                        if da in bigram_dict[previous_da]:
                            bigram_dict[previous_da][da] += 1
                        else:
                           bigram_dict[previous_da][da] = 1
                    else:
                        bigram_dict[previous_da][da] = 1
    starts = sum(start_probability.values())
    for da, val in start_probability.iteritems():
        start_probability[da] = val/float(starts)
    return unigrams, start_probability, bigram_dict


def calculate_start_probability(start_prob, states):
    start_probability_list = list()
    for i in range(0, len(states), 1):
        state = states[i]
        if state in start_prob:
            start_probability_list.append(start_prob[state])
        else:
            start_probability_list.append(0)
    start_probability = np.array(start_probability_list)
    return start_probability


def calculate_transition_probability(bigrams, states):
    transitions = collections.defaultdict(list)
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
            if end_state in transition_probabilities_dict:
                transition_probabilitiese_list.append(transition_probabilities_dict[end_state])
            else:
                transition_probabilitiese_list.append(0)
        if i == 0:
            tr_pr = np.array(transition_probabilitiese_list)
        else:
            tr_pr = np.vstack((tr_pr, np.array(transition_probabilitiese_list)))
    return tr_pr


def find_states(unigrams):
    # delete DIT++, root
    states = set()
    for da, count in unigrams.iteritems():
        if da != 'DIT++ Taxonomy':
            states.add(da)
    return list(states)


def find_da_id(taxonomy, cursor):
    results = postgres_queries.get_all_da(taxonomy, cursor)
    da_id_dict = dict()
    for result in results:
        da_id_dict[result[1]] = result[0]
    return da_id_dict


def recognized_da_segments(recognized_segmments_da, da_list, states, da_id_taxonomy, path_observation):
    for i in range(0, len(da_list), 1):
        da = da_list[i]
        dialog_act_name = states[da]
        path = path_observation[i]
        da_id = da_id_taxonomy[dialog_act_name]
        tuple_da_segment = (da_id, path[0], path[1], path[2])
        recognized_segmments_da = recognized_segmments_da + (tuple_da_segment,)
    return recognized_segmments_da


def da_predictions(test_seq, model, con_pathes, states, da_id_taxonomy, taxonomy, cursor, connection):
    recognized_segmments_da = ()
    for i in range(0, len(test_seq), 1): # conversation level
        for j in range(0, len(test_seq[i]), 1): # branch level
            brach_features = test_seq[i][j]
            logprob, alice_hears = model.decode(brach_features, algorithm="viterbi")
            path_observation = con_pathes[i][j]
            recognized_segmments_da = recognized_da_segments(recognized_segmments_da, alice_hears, states, da_id_taxonomy,  path_observation)
    update_table.update_da_prediction_bulk(recognized_segmments_da, taxonomy, cursor, connection)