import collections
from analysing_GS.calculate_emissions import build_emissions, calculate_emission_probability_feature_new
from postgres import postgres_queries
from learning.feature import Feature
import features


__author__ = 'snownettle'


def extract_features_test_set(data_set, embeddings, word_id):
    features_list = list()
    conversation_pathes_tweet_id = list()
    for conversation in data_set:
        for branch in conversation:
            start_segment = branch.start_segment()
            root_username = start_segment.get_username()
            segments = branch.get_segments()
            for i in range(0, len(segments), 1):
                segment = segments[i]
                tweet_id = segment.tweet_id
                start_offset = segment.start_offset
                end_offset = segment.end_offset
                utterance = segment.segment
                conversation_path_tweet_id = list()
                feature_branch = list()
                current_username = segment.user

                feature = Feature(utterance, start_offset, end_offset, root_username, current_username, i, embeddings, word_id)
                conversation_path_tweet_id.append([tweet_id, start_offset, end_offset])

                feature_branch.append(feature)
                features_list.append(feature_branch)
                conversation_pathes_tweet_id.append(conversation_path_tweet_id)
    return features_list, conversation_pathes_tweet_id


def extract_features_training_set(training_set, taxonomy, states, cursor, embeddings, word_id):

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
                pos = i

                start_offset = segment[0]
                end_offset = segment[1]
                utterance = segment[2]
                da = segment[3]
                feature = Feature(utterance, start_offset, end_offset, root_username, current_username, pos, language_features, embeddings, word_id)
                feature_index = feature.add_new_feature(feature_list)
                # feature_index = feature.find_index_in_feature_list(feature_list)
                build_emissions(feature_index, da, emissions)

    emissions_probability = calculate_emission_probability_feature_new(emissions, states, feature_list)

    return language_features, feature_list, emissions_probability


def extract_language_features(training_set, taxonomy, cursor):
    tf_features = collections.defaultdict(dict)
    observation_tokens = set()
    idf_features = collections.defaultdict(dict)
    utterance_list = ''
    for conversation in training_set:
        all_nodes = conversation.all_nodes()
        for node in all_nodes:
            tweet_id = node.tag
            segments = postgres_queries.find_segments_utterance(tweet_id, taxonomy, cursor)
            for i in range(0, len(segments), 1):
                segment = segments[i]
                utterance = segments[i][2]
                if '@' in utterance:
                    utterance = Feature.delete_username(utterance)
                if Feature.has_link(utterance):
                    utterance = Feature.delete_link(utterance)
                if Feature.has_link(utterance):
                    utterance = Feature.delete_hashtag(utterance)
                utterance = Feature.delete_non_alphabetic_symbols(utterance)
                if len(utterance) != 0:
                    utterance_list += utterance + '. '
                features.term_frequency_inversce_doc(segment, tf_features, idf_features, observation_tokens)
                # features.inverse_document_frequency(segment, idf_features)

    tfidf = features.calculate_tfidf(tf_features, idf_features)
    observation_tokens = features.choose_word_features(tfidf)
    return observation_tokens


def extract_features_training_set_gaus(training_set, taxonomy, embeddings, word_id):
    # feature_list = list()
    # emissions = collections.defaultdict(dict)
    means = collections.defaultdict(list)
    for conversation in training_set:
        for branch in conversation:
            start_segment = branch.start_segment()
            root_username = start_segment.get_username()
            segments = branch.get_segments()
            for i in range(0, len(segments), 1):
                segment = segments[i]
                tweet_id = segment.tweet_id
                start_offset = segment.start_offset
                end_offset = segment.end_offset
                utterance = segment.segment
                current_username = segment.user
                da = segment.get_da_by_taxonomy(taxonomy)
                pos = segment.segment_in_tweet
                feature = Feature(utterance, start_offset, end_offset, root_username, current_username, pos, embeddings, word_id)
                feature_set = convert_features(feature)
                # feature_index = feature.add_new_feature_hmm(feature_list)
                # build_emissions(feature_index, da, emissions)
                # if da in means:
                means[da].append(feature_set)

    return means


def convert_features(feature):
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
    for v in feature.word2vec:
        feature_set.append(v)
    return feature_set


def convert_values(value):
    if value is True:
        return 1
    else:
        return -1


def extract_features_test_set_gaus(data_set, embeddings, word_id):
    feature_list_conversations = list()
    conversations_pathes = list()
    for conversation in data_set:
        features_list = list()
        conversation_coordinate = list()
        for branch in conversation:
            start_segment = branch.start_segment()
            root_username = start_segment.get_username()
            segments = branch.get_segments()
            feature_branch = list()
            coordinate_branch = list()
            for i in range(0, len(segments), 1):
                segment = segments[i]
                tweet_id = segment.tweet_id
                start_offset = segment.start_offset
                end_offset = segment.end_offset
                utterance = segment.segment
                current_username = segment.user
                pos = segment.segment_in_tweet
                feature = Feature(utterance, start_offset, end_offset, root_username, current_username, pos, embeddings, word_id)
                feature_set = convert_features(feature)
                segment_coordinate = (tweet_id, start_offset, end_offset)
                feature_branch.append(feature_set)
                coordinate_branch.append(segment_coordinate)
            features_list.append(feature_branch)
            conversation_coordinate.append(coordinate_branch)
        feature_list_conversations.append(features_list)
        conversations_pathes.append(conversation_coordinate)

    return feature_list_conversations, conversations_pathes
