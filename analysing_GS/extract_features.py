import collections
import itertools

from analysing_GS.calculate_emissions import build_root_usersname_emissions, build_length_utterance_emissions, \
    build_segment_position_emissions, build_link_emissions, build_question_mark_emissions, \
    build_exclamation_mark_emissions, build_hashtag_emissions, calculate_emission_probability_feature, \
    build_emoticons_emissions, build_question_words_emissions, build_first_verb_emissions, build_emissions, calculate_emission_probability_feature_new
# from analysing_GS.features import is_link, has_question_mark, has_explanation_mark, has_hashtag, has_emoticons, \
#     has_question_word
from postgres import postgres_queries
from postgres.postgres_queries import count_start_conversation, count_end_conversation
from learning.feature import Feature
import features
import gc
from pattern.de import parse, split, INFINITIVE

__author__ = 'snownettle'


def extract_features_test_set(data_set, language_features, cursor):
    taxonomy = 'full' #it doesn_t matter which taxonomy, we make here predictions
    features_list = list()
    conversation_pathes_tweet_id = list()
    for conversation in data_set:
        root_id = conversation.root
        root_username = postgres_queries.find_username_by_tweet_id(root_id, cursor)
        all_conversation_branches = conversation.paths_to_leaves()
        for branch in all_conversation_branches:
            conversation_path_tweet_id = list()
            feature_branch = list()
            for tweet_id in branch:
                segments = postgres_queries.find_segments_utterance(tweet_id, taxonomy, cursor)
                current_username = postgres_queries.find_username_by_tweet_id(tweet_id, cursor)
                for i in range(0, len(segments), 1):
                    segment = segments[i]
                    if i == 0:
                        pos = True
                    else:
                        pos = False
                    start_offset = segment[0]
                    end_offset = segment[1]
                    utterance = segment[2]
                    feature = Feature(utterance, start_offset, end_offset, root_username, current_username, pos, language_features)
                    conversation_path_tweet_id.append([tweet_id, start_offset, end_offset])

                    feature_branch.append(feature)
            features_list.append(feature_branch)
            conversation_pathes_tweet_id.append(conversation_path_tweet_id)
    return features_list, conversation_pathes_tweet_id


def extract_features_training_set(training_set, taxonomy, states, cursor):

    language_features = extract_language_features(training_set, taxonomy, cursor)
    # language_features = list()
    number_of_segments = 0
    feature_list = list()
    emissions = collections.defaultdict(dict)
    for conversation in training_set:
        root = conversation.root
        root_username = postgres_queries.find_username_by_tweet_id(root, cursor)
        all_nodes = conversation.all_nodes()
        for node in all_nodes:
            tweet_id = node.tag
            current_username = postgres_queries.find_username_by_tweet_id(tweet_id, cursor)
            segments = postgres_queries.find_segments_utterance(tweet_id, taxonomy, cursor)
            number_of_segments += len(segments)
            for i in range(0, len(segments), 1):
                segment = segments[i]
                if i == 0:
                    pos = True
                else:
                    pos = False
                start_offset = segment[0]
                end_offset = segment[1]
                utterance = segment[2]
                da = segment[3]
                feature = Feature(utterance, start_offset, end_offset, root_username, current_username, pos, language_features)
                feature.add_new_feature(feature_list)
                feature_index = feature.find_index_in_feature_list(feature_list)
                build_emissions(feature_index, da, emissions)

    emissions_probability = calculate_emission_probability_feature_new(emissions, states, feature_list)

    return language_features, feature_list, emissions_probability


def extract_language_features(training_set, taxonomy, cursor):
    tf_features = collections.defaultdict(dict)
    observation_tokens = set()
    idf_features = collections.defaultdict(dict)
    for conversation in training_set:
        all_nodes = conversation.all_nodes()
        for node in all_nodes:
            tweet_id = node.tag
            segments = postgres_queries.find_segments_utterance(tweet_id, taxonomy, cursor)
            for i in range(0, len(segments), 1):
                segment = segments[i]
                features.term_frequency_inversce_doc(segment, tf_features, idf_features, observation_tokens)
                # features.inverse_document_frequency(segment, idf_features)

    tfidf = features.calculate_tfidf(tf_features, idf_features)
    observation_tokens = features.choose_word_features(tfidf)
    return observation_tokens

# def extract_language_features(training_set, taxonomy, cursor):
#     list_of_word = set()
#     utterance_list = ''
#     for conversation in training_set:
#         all_nodes = conversation.all_nodes()
#         for node in all_nodes:
#             tweet_id = node.tag
#             segments = postgres_queries.find_segments_utterance(tweet_id, taxonomy, cursor)
#             for i in range(0, len(segments), 1):
#                 utterance = segments[i][2]
#                 if '@' in utterance:
#                     utterance = Feature.delete_username(utterance)
#                 if Feature.has_link(utterance):
#                     utterance = Feature.delete_link(utterance)
#                 if Feature.has_link(utterance):
#                     utterance = Feature.delete_hashtag(utterance)
#                 utterance = Feature.delete_non_alphabetic_symbols(utterance)
#                 if len(utterance) != 0:
#                     utterance_list += utterance + '. '
#     sentences = parse(utterance_list, relations=True, lemmata=True).split()
#     for sentence in sentences:
#         for token in sentence:
#             if len(token[0]) > 1:
#                 list_of_word.add(token[0])
#     list_of_word = list(list_of_word)
#     return list_of_word
