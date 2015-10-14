import numpy as np

__author__ = 'snownettle'


def calculate_emission_probability_features(emissions, states, feature_list):
    for i in range(0, len(states), 1):
        occurancy = emissions[states[i]]
        total_number = sum(occurancy.values())
        probabilities = list()
        for j in range(0, len(feature_list), 1):
            if j in occurancy:
                pr = occurancy[j]/float(total_number)
                probabilities.append(pr)
            else:
                probabilities.append(0)
        if i == 0:
            emission_probability = np.array(probabilities)
        else:
            emission_probability = np.vstack((emission_probability, probabilities))
    return emission_probability


def build_emissions(feature_index, da, emissions):
    if da in emissions:
        if feature_index in emissions[da]:
            emissions[da][feature_index] += 1
        else:
            emissions[da][feature_index] = 1
    else:
        emissions[da][feature_index] = 1
