import collections
import itertools

from analysing_GS.calculate_emissions import build_root_usersname_emissions, build_length_utterance_emissions, \
    build_segment_position_emissions, build_link_emissions, build_question_mark_emissions, \
    build_explanation_mark_emissions, build_hashtag_emissions, calculate_emission_probability_feature, \
    build_emoticons_emissions, build_question_words_emissions, build_first_verb_emissions
from analysing_GS.features import is_link, has_question_mark, has_explanation_mark, has_hashtag, has_emoticons, \
    has_question_word, is_first_verb
    # term_frequency, inverse_document_frequency, calculate_tfidf, choose_word_features, tf_normalization, delete_tokens, \
    # token_observations, calculate_emissions_unigrams
from postgres import postgres_queries
from postgres.postgres_queries import count_start_conversation, count_end_conversation
import gc

__author__ = 'snownettle'


def extract_features_test_set(data_set, cursor):
    taxonomy = 'full' #it doesn_t matter which taxonomy, we make here predictions
    features_list = list()
    conversation_pathes_tweet_id = list()
    for conversation in data_set:
        root_id = conversation.root
        root_username = postgres_queries.find_username_by_tweet_id(root_id, cursor)
        all_conversation_branches = conversation.paths_to_leaves()
        # conversation_path_tweet_id.append(all_conversation_branches)
        for branch in all_conversation_branches:
            conversation_path_tweet_id = list()
            feature_branch = list()
            # t = 0
            for tweet_id in branch:
                segments = postgres_queries.find_segments_utterance(tweet_id, taxonomy, cursor)
                # t += len(segments)
                current_username = postgres_queries.find_username_by_tweet_id(tweet_id, cursor)
                same_username = (root_username == current_username)
                # segment_position_first = 0
                if same_username is True:
                    same_username = 1
                else:
                    same_username = 0
                # segments = sort_segments(segments, taxonomy)
                # for segment in segments:
                for i in range(0, len(segments), 1):
                    segment = segments[i]
                    if i == 0:
                        segment_position_first = 1
                    else:
                        segment_position_first = 0
                # for start_offset, end_offset_utterance in segments.iteritems():
                    start_offset = segment[0]
                    end_offset = segment[1]
                    link = is_link(segment[2])
                    question_mark = has_question_mark(segment[2])
                    explanation_mark = has_explanation_mark(segment[2])
                    hashtag = has_hashtag(segment[2])
                    emoticons = has_emoticons(segment[2])
                    conversation_path_tweet_id.append([tweet_id, start_offset, end_offset])
                    segment_len = end_offset - start_offset + 1
                    question_word = has_question_word(segment[2])
                    first_verb = is_first_verb(segment[2])
                    # add feature token - check if we have them, make as a list
                    features = [segment_len, same_username, segment_position_first, link, question_mark,
                                explanation_mark, hashtag, emoticons, question_word, first_verb]

                    feature_branch.append(features)
            features_list.append(feature_branch)
            conversation_pathes_tweet_id.append(conversation_path_tweet_id)
    return features_list, conversation_pathes_tweet_id


def extract_features_training_set(training_set, taxonomy, states, cursor): #check if in the training set is only german tweets
    observations_length = set()
    emissions_length = collections.defaultdict()
    da_root_username_emissions = collections.defaultdict(dict)
    link_emissions = collections.defaultdict(dict)
    segment_position_first_emissions = collections.defaultdict(dict)
    question_mark_emissions = collections.defaultdict(dict)
    explanation_mark_emissions = collections.defaultdict(dict)
    hashtag_emissions = collections.defaultdict(dict)
    emoticons_emissions = collections.defaultdict(dict)
    question_words_emissions = collections.defaultdict(dict)
    first_verb_emissions = collections.defaultdict(dict)

    observation_root_username = [0, 1] # root, not_root
    observation_segment_position = [0, 1] # first segment, not first segment
    observation_link = [0, 1] # segment has link or not
    observation_question_mark = [True, False]
    observation_explanation_mark = [True, False]
    observation_hashtags = [True, False]
    observation_emoticons = [True, False]
    observation_question_words = [True, False]
    observation_first_verb = [True, False]

    number_of_segments = 0

    for conversation in training_set:
        root = conversation.root
        root_username = postgres_queries.find_username_by_tweet_id(root, cursor)
        all_nodes = conversation.all_nodes()
        for node in all_nodes:
            tweet_id = node.tag
            current_username = postgres_queries.find_username_by_tweet_id(tweet_id, cursor)
            # here!!!
            segment_position_first = 0 # aka False
            segments = postgres_queries.find_segments_utterance(tweet_id, taxonomy, cursor)
            number_of_segments += len(segments)
            for i in range(0, len(segments), 1):
                segment = segments[i]
                if i == 0:
                    segment_position_first = 1 # aka true
                else:
                    segment_position_first = 0
                build_root_usersname_emissions(root_username, current_username, segment, da_root_username_emissions)
                build_length_utterance_emissions(segment, observations_length, emissions_length)
                build_segment_position_emissions(segment_position_first, segment, segment_position_first_emissions)
                build_link_emissions(segment, link_emissions)
                build_question_mark_emissions(segment, question_mark_emissions)
                build_explanation_mark_emissions(segment, explanation_mark_emissions )
                build_hashtag_emissions(segment, hashtag_emissions)
                build_emoticons_emissions(segment, emoticons_emissions)
                build_question_words_emissions(segment, question_words_emissions)
                build_first_verb_emissions(segment, first_verb_emissions)


                # term_frequency(segment, tf_features, observation_tokens)
                # inverse_document_frequency(segment, idf_features)

    # tfidf = calculate_tfidf(tf_features)
    # observation_tokens = choose_word_features(tfidf)
    # new_tf_features = delete_tokens(tf_features, observation_tokens)
    # tf_norm = tf_normalization(new_tf_features)


    # for a, b in tfidf.iteritems():
    #     print sum(b.values())
    # idf = calculate_idf(number_of_segments, idf_features)
    # sorted_x = sorted(idf_features.items(), key=operator.itemgetter(1))
    # sorted_x.reverse()
    # delete not frequent words
    # tf_norm = tf_normalization(tf_features)
    # idf_norm = idf_normalization(tf_features, observation_tokens)
    # calculate_emission_probability_tfidf(tf_norm, idf_norm, observation_tokens, states)

    observations_length = list(observations_length)
    s_count = count_start_conversation(cursor)
    emissions_length['<S>'] = {0: s_count}
    e_count = count_end_conversation(cursor)
    emissions_length['<E>'] = {0: e_count}


    # emissions_probability_tf = calculate_emission_probability_feature(tf_norm, states, observation_tokens)
    # token_observations_boolean = token_observations(observation_tokens)
    emissions_probability_length = calculate_emission_probability_feature(emissions_length, states, observations_length)
    # emission_probability_tf = calculate_emissions_unigrams(observation_tokens, token_observations_boolean, tf_norm, states)
    emissions_probability_root_username = calculate_emission_probability_feature(da_root_username_emissions,
                                                                                 states, observation_root_username)
    emissions_probability_segment_position = calculate_emission_probability_feature(segment_position_first_emissions,
                                                                                    states, observation_segment_position)
    emissions_probability_link = calculate_emission_probability_feature(link_emissions, states, observation_link)

    emissions_probability_questoin_mark = calculate_emission_probability_feature(question_mark_emissions, states, observation_question_mark)
    emissions_probability_explanation_mark = calculate_emission_probability_feature(explanation_mark_emissions, states, observation_explanation_mark)
    emissions_probability_hashtag = calculate_emission_probability_feature(hashtag_emissions, states,
                                                                           observation_hashtags)
    emissions_probability_emoticons = calculate_emission_probability_feature(emoticons_emissions, states,
                                                                             observation_emoticons)
    emissions_probability_question_word = calculate_emission_probability_feature(question_words_emissions, states,
                                                                                 observation_question_words)
    emissions_probability_first_verb = calculate_emission_probability_feature(first_verb_emissions, states,
                                                                               observation_first_verb)

    emission = [emissions_probability_length, emissions_probability_root_username,
                emissions_probability_segment_position, emissions_probability_link, emissions_probability_questoin_mark,
                emissions_probability_explanation_mark, emissions_probability_hashtag, emissions_probability_emoticons,
                emissions_probability_question_word, emissions_probability_first_verb]

    observation = [observations_length, observation_root_username, observation_segment_position,
                   observation_link, observation_question_mark, observation_explanation_mark, observation_hashtags,
                   observation_emoticons, observation_question_words, observation_first_verb]
    observation_product = itertools.product(*observation)
    new_observations_product = list()
    for obs in observation_product:
        new_observations_product.append(obs)

    return observation, emission, new_observations_product
