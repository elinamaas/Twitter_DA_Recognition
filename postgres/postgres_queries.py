__author__ = 'snownettle'
import collections

import nltk
from nltk import WhitespaceTokenizer

import postgres_configuration

da_full_table = 'dialogue_act_full'
da_reduced_table = 'dialogue_act_reduced'
da_min_table = 'dialogue_act_minimal'
segmentation_table = 'segmentation'
segments_utterance_table = 'segments_utterance'
tweet_table = 'tweet'


def find_annotated_conversation_number():
    connection, cursor = postgres_configuration.make_connection()
    query = 'select max(Conversation_id) from Tweet where Annotated = True'
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results[0][0]


def find_conversation(conversation_number):
    connection, cursor = postgres_configuration.make_connection()
    query = 'select * from Tweet where Conversation_id = ' + str(conversation_number)
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def find_conversations():
    converasation_number = find_annotated_conversation_number()
    conversation_list = list()
    for i in range(1, converasation_number +1, 1):
        conversation = find_conversation(i)
        conversation_list.append(conversation)
    return conversation_list


def find_conversations_root():
    connection, cursor = postgres_configuration.make_connection()
    query = 'select * from tweet where in_replay_to is null and annotated = True'
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def find_not_german_tweets():
    connection, cursor = postgres_configuration.make_connection()
    query = 'select tweet_id, tweet_text from tweet where german = False'
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    print 'There are ' + str(len(results)) + ' not german tweets'
    for result in results:
        print result
    return results


def find_das_for_tweet(tweet_id):
    connection, cursor = postgres_configuration.make_connection()
    query = 'select da.dialogue_act_name from segmentation as s, dialogue_act as da ' \
            'where s.tweet_id =' + str(tweet_id) + 'and s.dialogue_act_id = da.dialogue_act_id ' \
                                                   'group by s.dialogue_act_id, da.dialogue_act_name'

    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def find_da_unigrams(taxonomy):
    connection, cursor = postgres_configuration.make_connection()
    global da_full_table
    global segmentation_table
    global da_reduced_table
    global da_min_table
    if taxonomy == 'full':
        query = 'select count(s.dialogue_act_id_full), da_full.dialogue_act_name ' \
                'from ' + segmentation_table + ' as s, ' + da_full_table + ' as da_full ' \
                'where s.dialogue_act_id_full = da_full.dialogue_act_id ' \
                'group by s.dialogue_act_id_full, da_full.dialogue_act_name ' \
                'order by count(s.dialogue_act_id_full) desc'
    elif taxonomy == 'reduced':
        query = 'select count(s.dialogue_act_id_reduced), da_reduced.dialogue_act_name ' \
            'from ' + segmentation_table + ' as s, ' + da_reduced_table + ' as da_reduced' \
            'where s.dialogue_act_id_reduced = da_reduced.dialogue_act_id ' \
            'group by s.dialogue_act_id_reduced, da_reduced.dialogue_act_name ' \
            'order by count(s.dialogue_act_id_reduced) desc'
    else:
        query = 'select count(s.dialogue_act_id_min), da_min.dialogue_act_name ' \
            'from ' + segmentation_table + 'as s, ' + da_min_table + ' as da_min ' \
            'where s.dialogue_act_min_full = da_min.dialogue_act_id ' \
            'group by s.dialogue_act_id_min, da_min.dialogue_act_name ' \
            'order by count(s.dialogue_act_id_min) desc'

    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def find_segments(tweet_id):
    global da_full_table
    global segmentation_table
    global da_reduced_table
    global da_min_table
    connection, cursor = postgres_configuration.make_connection()
    query = 'select s.segmentation_offsets, da_full.dialogue_act_name, da_reduced.dialogue_act_name, ' \
            'da_min.dialogue_act_name from ' + segmentation_table + ' as s, ' + da_full_table + ' as da_full, '\
            + da_reduced_table + ' as da_reduced, ' + da_min_table + ' as da_min where s.tweet_id =' + str(tweet_id) \
            + 'and s.dialogue_act_id_full = da_full.dialogue_act_id ' \
              'and s.dialogue_act_id_reduced = da_reduced.dialogue_act_id ' \
              'and s.dialogue_act_id_min = da_min.dialogue_act_id'

    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results

def find_segments_utterance(tweet_id):
    global da_full_table
    global segmentation_table
    global da_reduced_table
    global da_min_table
    connection, cursor = postgres_configuration.make_connection()
    query = 'select s.segmentation_offsets, s.utterance, da_full.dialogue_act_name, da_reduced.dialogue_act_name, ' \
            'da_min.dialogue_act_name from ' + segments_utterance_table + ' as s, ' + da_full_table + ' as da_full, '\
            + da_reduced_table + ' as da_reduced, ' + da_min_table + ' as da_min where s.tweet_id =' + str(tweet_id) \
            + 'and s.dialogue_act_id_full = da_full.dialogue_act_id ' \
              'and s.dialogue_act_id_reduced = da_reduced.dialogue_act_id ' \
              'and s.dialogue_act_id_min = da_min.dialogue_act_id'

    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results
# select s.segmentation_offsets, da.dialogue_act_name from segmentation as s, dialogue_act as da
# where s.tweet_id = 406567743258120192 and s.dialogue_act_id = da.dialogue_act_id
# group by da.dialogue_act_name, s.dialogue_act_id, s.segmentation_offsets


def find_children(tweet_id):
    connection, cursor = postgres_configuration.make_connection()
    query = 'select * from tweet where in_replay_to =' + str(tweet_id) + 'and annotated = True'
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def find_tweet_text(tweet_id):
    connection, cursor = postgres_configuration.make_connection()
    query = 'SELECT tweet_text FROM tweet where tweet_id =' + str(tweet_id)
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results[0]


def find_all_tokens():
    connection, cursor = postgres_configuration.make_connection()
    query = 'select tweet_id, token from annotated_token_tweet'
    cursor.execute(query)
    results= cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def find_all_records(table_name):
    connection, cursor = postgres_configuration.make_connection()
    query = 'select * from ' + table_name
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def find_da_by_name(da_name, table):
    connection, cursor = postgres_configuration.make_connection()
    query = 'select dialogue_act_id from ' + table + ' where dialogue_act_name = \'' + da_name + '\''
    cursor.execute(query)
    results = cursor.fetchall()
    da_id = results[0][0]
    postgres_configuration.close_connection(connection)
    return da_id


def find_da_for_segment(tweet_id, segment_offset, taxonomy):
    segment_offset = segment_offset.replace(' ', '')
    connection, cursor = postgres_configuration.make_connection()
    if taxonomy == 'full':
        query = 'select dialogue_act_id_full from segmentation ' \
                'where tweet_id = ' + str(tweet_id) + ' and segmentation_offsets =\''+ segment_offset+ '\''
    elif taxonomy == 'reduced':
        query = 'select dialogue_act_id_reduced from segmentation ' \
                'where tweet_id = ' + str(tweet_id) + ' and segmentation_offsets =\''+ segment_offset+ '\''
    else:
        query = 'select dialogue_act_id_min from segmentation ' \
                'where tweet_id = ' + str(tweet_id) + ' and segmentation_offsets =\''+ segment_offset+ '\''
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results[0][0]


def find_da_by_id(da_id, table):
    connection, cursor = postgres_configuration.make_connection()
    query = 'select dialogue_act_name from ' + table + ' where dialogue_act_id = ' + str(da_id)
    cursor.execute(query)
    results = cursor.fetchall()
    da_id = results[0][0]
    postgres_configuration.close_connection(connection)
    return da_id


def find_all_da_occurances_taxonomy(table, da, taxonomy):
    connection, cursor = postgres_configuration.make_connection()
    if taxonomy == 'full':
        da_id = find_da_by_name(da,'Dialogue_act_full')
        query = 'select tweet_id, segmentation_offsets, dialogue_act_id_full from ' + \
                table + ' where dialogue_act_id_full = ' + str(da_id)
    elif taxonomy == 'reduced':
        da_id = find_da_by_name(da,'Dialogue_act_reduced')
        query = 'select tweet_id, segmentation_offsets, dialogue_act_id_reduced from ' + \
                table + ' where dialogue_act_id_reduced = ' + str(da_id)
    else:
        da_id = find_da_by_name(da,'Dialogue_act_minimal')
        query = 'select tweet_id, segmentation_offsets, dialogue_act_id_min from ' + \
                table + ' where dialogue_act_id_min = ' + str(da_id)
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def update_da_prediction(da_name, tweet_id, offset, taxonomy):
    connection, cursor = postgres_configuration.make_connection()
    if taxonomy == 'full':
        da_id = find_da_by_name(da_name, da_full_table)
        query = 'update segmentation_prediction set dialogue_act_id_full = ' + da_id + \
                ' where tweet_id = ' + tweet_id + ' and segmentation_offsets = ' + offset
    elif taxonomy == 'reduced':
        da_id = find_da_by_name(da_name, da_reduced_table)
        query = 'update segmentation_prediction set dialogue_act_id_reduced = ' + da_id + \
                ' where tweet_id = ' + tweet_id + ' and segmentation_offsets = ' + offset
    else:
        da_id = find_da_by_name(da_name, da_min_table)
        query = 'update segmentation_prediction set dialogue_act_id_min = ' + da_id + \
                ' where tweet_id = ' + tweet_id + ' and segmentation_offsets = ' + offset
    cursor.execute(query)
    # results = cursor.fetchall()
    postgres_configuration.close_connection(connection)


def find_tokens_by_offset(tweet_id, start_offset, end_offset):
    end_offset = int(end_offset)+1
    start_offset = int(start_offset) - 1
    connection, cursor = postgres_configuration.make_connection()
    query = 'select token_offset, token from annotated_token_tweet where tweet_id =' + str(tweet_id) + \
            'and token_offset > ' + str(start_offset) + ' and token_offset < ' + str(end_offset) + \
            'order by token_offset asc'
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def find_utterance(taxonomy):
    connection, cursor = postgres_configuration.make_connection()
    if taxonomy == 'full':
        query = 'select s.utterance, da.dialogue_act_name from ' + segments_utterance_table + ' as s, ' \
                + da_full_table + ' as da where s.dialogue_act_id_full = da.dialogue_act_id'
    elif taxonomy == 'reduced':
        query = 'select s.utterance, da.dialogue_act_name from ' + segments_utterance_table + ' as s, ' \
                + da_reduced_table + ' as da where s.dialogue_act_id_reduced = da.dialogue_act_id'
    else:
        query = 'select s.utterance, da.dialogue_act_name from ' + segments_utterance_table + ' as s, ' \
                + da_min_table + ' as da where s.dialogue_act_id_min = da.dialogue_act_id'
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def count_segments_training_set(training_set):
    segment_count = 0
    seg_len = set()
    for conversation in training_set:
        all_nodes = conversation.all_nodes()
        for node in all_nodes:
            tweet_id = node.tag
            segments = find_segments(tweet_id)
            segment_count += len(segments)
    return segment_count


def find_utterance_tweet(taxonomy, tweet_id):
    connection, cursor = postgres_configuration.make_connection()
    if taxonomy == 'full':
        query = 'select s.utterance, da.dialogue_act_name from ' + segments_utterance_table + ' as s, ' \
                + da_full_table + ' as da where s.dialogue_act_id_full = da.dialogue_act_id ' \
                                  'and s.tweet_id= ' + str(tweet_id)
    elif taxonomy == 'reduced':
        query = 'select s.utterance, da.dialogue_act_name from ' + segments_utterance_table + ' as s, ' \
                + da_reduced_table + ' as da where s.dialogue_act_id_reduced = da.dialogue_act_id ' \
                                     'and s.tweet_id= ' + str(tweet_id)
    else:
        query = 'select s.utterance, da.dialogue_act_name from ' + segments_utterance_table + ' as s, ' \
                + da_min_table + ' as da where s.dialogue_act_id_min = da.dialogue_act_id ' \
                                 'and s.tweet_id= ' + str(tweet_id)
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def lenght_feature_segments_utterance(training_set, taxonomy):
    observations = set()
    emissions = collections.defaultdict()
    for conversation in training_set:
        all_nodes = conversation.all_nodes()
        for node in all_nodes:
            tweet_id = node.tag
            segments = find_utterance_tweet(taxonomy, tweet_id)
            for segment in segments:
                segment_len = len(nltk.word_tokenize(segment[0]))
                if '@' in segment[0]:
                    segment_len = len(WhitespaceTokenizer().tokenize(segment[0]))
                observations.add(segment_len)
                if segment[1] in emissions:
                    da_utterance_len = emissions[segment[1]]
                    if segment_len in da_utterance_len:
                        da_utterance_len[segment_len] += 1
                    else:
                        da_utterance_len[segment_len] = 1
                        # emissions[segment[1]] = {segment_len:1}
                else:
                    da_utterance_len = dict()
                    da_utterance_len[segment_len] = 1
                    emissions[segment[1]] = da_utterance_len
    observations = list(observations)
    s_count = count_start_conversation()
    emissions['<S>'] = {0:s_count}
    e_count = count_end_conversation()
    emissions['<E>'] = {0:e_count}
    return observations, emissions


def count_end_conversation():
    connection, cursor = postgres_configuration.make_connection()
    query = 'select distinct tweet_id from tweet where position_in_conversation = \'end\''
    cursor.execute(query)
    results = cursor.rowcount
    postgres_configuration.close_connection(connection)
    return results


def count_start_conversation():
    connection, cursor = postgres_configuration.make_connection()
    query = 'select distinct tweet_id from tweet where position_in_conversation = \'start\''
    cursor.execute(query)
    results = cursor.rowcount
    postgres_configuration.close_connection(connection)
    return results


