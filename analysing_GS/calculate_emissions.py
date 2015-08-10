import numpy as np
from analysing_GS.extract_features import is_link

__author__ = 'snownettle'


def build_hashtag_emissions(segment, hashtag_emissions):
    utterance = segment[2]
    da = segment[3]
    if '#' in utterance:
        question_mark = True
    else:
        question_mark = False
    if da in hashtag_emissions:
        if question_mark in hashtag_emissions[da]:
            hashtag_emissions[da][question_mark] += 1
        else:
            hashtag_emissions[da][question_mark] = 1
    else:
        hashtag_emissions[da][question_mark] = 1


def build_length_utterance_emissions(segment, observations_length, emissions_length):
    start_offset = segment[0]
    end_offset = segment[1]
    segment_len = end_offset - start_offset + 1
    # if '@' in segment[0]:
    #     segment_len = len(WhitespaceTokenizer().tokenize(segment[0]))
    observations_length.add(segment_len)
    da = segment[3]
    if da in emissions_length:
        da_utterance_len = emissions_length[da]
        if segment_len in da_utterance_len:
            da_utterance_len[segment_len] += 1
        else:
            da_utterance_len[segment_len] = 1
            # emissions[segment[1]] = {segment_len:1}
    else:
        da_utterance_len = dict()
        da_utterance_len[segment_len] = 1
        emissions_length[da] = da_utterance_len


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


def build_segment_position_emissions(segment_position_first, segment, segment_position_first_emissions):
    da = segment[3]
    if da in segment_position_first_emissions:
        segment_position_counter = segment_position_first_emissions[da]
        if segment_position_first in segment_position_counter:
            segment_position_counter[segment_position_first] += 1
        else:
            segment_position_counter[segment_position_first] = 1
    else:
        segment_position_first_emissions[da][segment_position_first] = 1


def build_explanation_mark_emissions(segment, explanation_mark_emissions):
    utterance = segment[2]
    da = segment[3]
    if '!' in utterance:
        question_mark = True
    else:
        question_mark = False
    if da in explanation_mark_emissions:
        if question_mark in explanation_mark_emissions[da]:
            explanation_mark_emissions[da][question_mark] += 1
        else:
            explanation_mark_emissions[da][question_mark] = 1
    else:
        explanation_mark_emissions[da][question_mark] = 1


def build_question_mark_emissions(segment, question_mark_emissions):
    utterance = segment[2]
    da = segment[3]
    if '?' in utterance:
        question_mark = True
    else:
        question_mark = False
    if da in question_mark_emissions:
        if question_mark in question_mark_emissions[da]:
            question_mark_emissions[da][question_mark] += 1
        else:
            question_mark_emissions[da][question_mark] = 1
    else:
        question_mark_emissions[da][question_mark] = 1


def build_root_usersname_emissions(root_username, current_username, segment, da_root_username_emissions):
    """

    :type da_root_username_emissions: collections.defaultdict(dict)
    """
    same_username = (root_username == current_username)
    if same_username is True:
        same_username = 1
    else:
        same_username = 0
    da = segment[3]
    if da in da_root_username_emissions:
        if same_username in da_root_username_emissions[da]:
            da_root_username_emissions[da][same_username] += 1
        else:
            da_root_username_emissions[da][same_username] = 1
    else:
        da_root_username_emissions[da][same_username] = 1


def has_link(utterance):
    if 'http:' in utterance:
        return True
    else:
        return False


def build_link_emissions(segment, link_emissions):
    da = segment[3]
    utterance = segment[2]
    link = is_link(utterance)
    if da in link_emissions:
        if link in link_emissions[da]:
            link_emissions[da][link] += 1
        else:
            link_emissions[da][link] = 1
    else:
        link_emissions[da][link] = 1