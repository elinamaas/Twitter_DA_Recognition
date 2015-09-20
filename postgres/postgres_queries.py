__author__ = 'snownettle'

import postgres_configuration


def find_annotated_conversation_number(cursor):
    query = 'select max(Conversation_id) from Tweet where Annotated = True'
    cursor.execute(query)
    results = cursor.fetchone()
    return results[0]


def find_conversation(conversation_number, cursor):
    query = 'select * from Tweet where Conversation_id = ' + str(conversation_number)
    cursor.execute(query)
    results = cursor.fetchall()
    return results


def find_conversations():
    converasation_number = find_annotated_conversation_number()
    conversation_list = list()
    for i in range(1, converasation_number +1, 1):
        conversation = find_conversation(i)
        conversation_list.append(conversation)
    return conversation_list


def find_conversations_root(cursor):
    query = 'select * from tweet where in_replay_to is null and annotated = True'
    cursor.execute(query)
    results = cursor.fetchall()
    return results


def find_not_german_tweets(cursor):
    query = 'select tweet_id, tweet_text from tweet where german = False'
    cursor.execute(query)
    results = cursor.fetchall()
    print 'There are ' + str(len(results)) + ' not german tweets'
    for result in results:
        print result
    return results


def get_all_da_taxonomy(taxonomy, cursor):
    if taxonomy == 'full':
        query = 'select dialogue_act_id, dialogue_act_name from dialogue_act_full order by dialogue_act_id asc'
    elif taxonomy == 'reduced':
        query = 'select dialogue_act_id, dialogue_act_name from dialogue_act_reduced order by dialogue_act_id asc'
    else:
        query = 'select dialogue_act_id, dialogue_act_name from dialogue_act_minimal order by dialogue_act_id asc'
    cursor.execute(query)
    results = cursor.fetchall()
    return results


def find_das_for_tweet(tweet_id):
    connection, cursor = postgres_configuration.make_connection()
    query = 'select da.dialogue_act_name from segmentation as s, dialogue_act as da' \
            ' where s.tweet_id =' + str(tweet_id) + 'and s.dialogue_act_id = da.dialogue_act_id ' \
                                                   'group by s.dialogue_act_id, da.dialogue_act_name'

    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def find_da_unigrams(taxonomy, cursor):
    if taxonomy == 'full':
        query = 'select count(s.dialogue_act_id_full), da_full.dialogue_act_name ' \
                ' from ' + postgres_configuration.segmentationTable + ' as s, ' + postgres_configuration.fullOntologyTable + ' as da_full ' \
                'where s.dialogue_act_id_full = da_full.dialogue_act_id ' \
                'group by s.dialogue_act_id_full, da_full.dialogue_act_name ' \
                'order by count(s.dialogue_act_id_full) desc'
    elif taxonomy == 'reduced':
        query = 'select count(s.dialogue_act_id_reduced), da_reduced.dialogue_act_name ' \
            ' from ' + postgres_configuration.segmentationTable + ' as s, ' + postgres_configuration.reducedOntologyTable + ' as da_reduced' \
            ' where s.dialogue_act_id_reduced = da_reduced.dialogue_act_id ' \
            'group by s.dialogue_act_id_reduced, da_reduced.dialogue_act_name ' \
            'order by count(s.dialogue_act_id_reduced) desc'
    else:
        query = 'select count(s.dialogue_act_id_min), da_min.dialogue_act_name ' \
            ' from ' + postgres_configuration.segmentationTable + ' as s, ' + postgres_configuration.minimalOntologyTable + ' as da_min ' \
            'where s.dialogue_act_id_min = da_min.dialogue_act_id ' \
            'group by s.dialogue_act_id_min, da_min.dialogue_act_name ' \
            'order by count(s.dialogue_act_id_min) desc'

    cursor.execute(query)
    results = cursor.fetchall()
    # postgres_configuration.close_connection(connection)
    return results


def find_states(taxonomy, cursor):
    # connection, cursor = postgres_configuration.make_connection()
    if taxonomy == 'full':
        query = 'select distinct da_full.dialogue_act_name ' \
                ' from ' + postgres_configuration.segmentationTable + ' as s, ' + postgres_configuration.fullOntologyTable + ' as da_full ' \
                'where s.dialogue_act_id_full = da_full.dialogue_act_id '
    elif taxonomy == 'reduced':
        query = 'select distinct da_reduced.dialogue_act_name ' \
            ' from ' + postgres_configuration.segmentationTable + ' as s, ' + postgres_configuration.reducedOntologyTable + ' as da_reduced' \
            ' where s.dialogue_act_id_reduced = da_reduced.dialogue_act_id '
    else:
        query = 'select distinct da_min.dialogue_act_name ' \
            ' from ' + postgres_configuration.segmentationTable + ' as s, ' + postgres_configuration.minimalOntologyTable + ' as da_min ' \
            'where s.dialogue_act_id_min = da_min.dialogue_act_id '

    cursor.execute(query)
    results = cursor.fetchall()
    used_das = list()
    for result in results:
        used_das.append(result[0])
    return used_das


def find_predicted_states(taxonomy, cursor):
    # connection, cursor = postgres_configuration.make_connection()
    if taxonomy == 'full':
        query = 'select distinct da_full.dialogue_act_name ' \
                ' from ' + postgres_configuration.segmentationPredictionTable + ' as s, ' + postgres_configuration.fullOntologyTable + ' as da_full ' \
                'where s.dialogue_act_id_full = da_full.dialogue_act_id '
    elif taxonomy == 'reduced':
        query = 'select distinct da_reduced.dialogue_act_name ' \
            ' from ' + postgres_configuration.segmentationPredictionTable + ' as s, ' + postgres_configuration.reducedOntologyTable + ' as da_reduced' \
            ' where s.dialogue_act_id_reduced = da_reduced.dialogue_act_id '
    else:
        query = 'select distinct da_min.dialogue_act_name ' \
            ' from ' + postgres_configuration.segmentationPredictionTable + ' as s, ' + postgres_configuration.minimalOntologyTable + ' as da_min ' \
            'where s.dialogue_act_id_min = da_min.dialogue_act_id '

    cursor.execute(query)
    results = cursor.fetchall()
    used_das = list()
    for result in results:
        used_das.append(result[0])
    return used_das


def find_segments(tweet_id, cursor):
    # connection, cursor = postgres_configuration.make_connection()
    query = 'select s.start_offset, s.end_offset,  da_full.dialogue_act_name, da_reduced.dialogue_act_name, ' \
            'da_min.dialogue_act_name, s.utterance from ' + postgres_configuration.segmentationUtteranceTable + ' as s, ' \
            + postgres_configuration.fullOntologyTable + ' as da_full, '\
            + postgres_configuration.reducedOntologyTable + ' as da_reduced, ' \
            + postgres_configuration.minimalOntologyTable + ' as da_min where s.tweet_id =' + str(tweet_id) \
            + ' and s.dialogue_act_id_full = da_full.dialogue_act_id ' \
              'and s.dialogue_act_id_reduced = da_reduced.dialogue_act_id ' \
              'and s.dialogue_act_id_min = da_min.dialogue_act_id order by s.start_offset asc'

    cursor.execute(query)
    results = cursor.fetchall()
    # postgres_configuration.close_connection(connection)
    return results


def count_segments(tweet_id, cursor):
    # connection, cursor = postgres_configuration.make_connection()
    query = 'select count(s.start_offset) from ' + postgres_configuration.segmentationTable \
            + ' as s where s.tweet_id =' + str(tweet_id)
    cursor.execute(query)
    results = cursor.fetchall()
    # postgres_configuration.close_connection(connection)
    return int(results[0][0])


def find_segments_utterance(tweet_id, taxonomy, cursor):
    # connection, cursor = postgres_configuration.make_connection()
    if taxonomy == 'full':
        query = 'select s.start_offset, s.end_offset, s.utterance, da_full.dialogue_act_name from ' \
                + postgres_configuration.segmentationUtteranceTable + ' as s, ' + \
                postgres_configuration.fullOntologyTable + ' as da_full where s.tweet_id =' + str(tweet_id) \
            + ' and s.dialogue_act_id_full = da_full.dialogue_act_id order by s.start_offset asc'
    elif taxonomy == 'reduced':
        query = 'select s.start_offset, s.end_offset, s.utterance, da_reduced.dialogue_act_name from ' \
            + postgres_configuration.segmentationUtteranceTable + ' as s, ' \
            + postgres_configuration.reducedOntologyTable + ' as da_reduced where s.tweet_id =' + str(tweet_id) \
            + ' and s.dialogue_act_id_reduced = da_reduced.dialogue_act_id order by s.start_offset asc'
    else:
        query = 'select s.start_offset, s.end_offset, s.utterance, da_min.dialogue_act_name from ' \
                + postgres_configuration.segmentationUtteranceTable + ' as s, ' \
                + postgres_configuration.minimalOntologyTable + ' as da_min where s.tweet_id =' + str(tweet_id) \
                + ' and s.dialogue_act_id_min = da_min.dialogue_act_id order by s.start_offset asc'

    cursor.execute(query)
    results = cursor.fetchall()
    # postgres_configuration.close_connection(connection)
    return results
# select s.segmentation_offsets, da.dialogue_act_name from segmentation as s, dialogue_act as da
# where s.tweet_id = 406567743258120192 and s.dialogue_act_id = da.dialogue_act_id
# group by da.dialogue_act_name, s.dialogue_act_id, s.segmentation_offsets


def find_children(tweet_id, cursor):
    query = 'select * from tweet where in_replay_to =' + str(tweet_id) + ' and annotated = True'
    cursor.execute(query)
    results = cursor.fetchall()
    return results


def find_tweet_text(tweet_id, cursor):
    query = 'SELECT tweet_text FROM tweet where tweet_id =' + str(tweet_id)
    cursor.execute(query)
    results = cursor.fetchall()
    return results[0]


def find_all_tokens(cursor):
    query = 'select tweet_id, token from annotated_token_tweet'
    cursor.execute(query)
    results = cursor.fetchall()
    return results


def find_all_tweet_texts(cursor):
    query = 'select tweet_id, tweet_text from tweet'
    cursor.execute(query)
    results = cursor.fetchall()
    return results


def find_all_records(table_name, cursor):
    query = 'select * from ' + table_name
    cursor.execute(query)
    results = cursor.fetchall()
    return results


def find_da_by_name(da_name, table, cursor):
    query = 'select dialogue_act_id from ' + table + ' where dialogue_act_name = \'' + da_name + '\''
    cursor.execute(query)
    results = cursor.fetchone()
    da_id = results[0]
    return da_id


def find_da_for_segment(tweet_id, start_offset, end_offset, taxonomy, cursor):
    if taxonomy == 'full':
        query = 'select dialogue_act_id_full from segmentation ' \
                ' where tweet_id = ' + str(tweet_id) + ' and start_offset =' + str(start_offset)\
                + ' and end_offset = ' + str(end_offset)
    elif taxonomy == 'reduced':
        query = 'select dialogue_act_id_reduced from segmentation ' \
                ' where tweet_id = ' + str(tweet_id) + ' and start_offset =' + str(start_offset)\
                + ' and end_offset = ' + str(end_offset)
    else:
        query = 'select dialogue_act_id_min from segmentation ' \
                ' where tweet_id = ' + str(tweet_id) + ' and start_offset =' + str(start_offset)\
                + ' and end_offset = ' + str(end_offset)
    cursor.execute(query)
    results = cursor.fetchone()
    return results[0]


def find_da_by_id(da_id, table, cursor):
    query = 'select dialogue_act_name from ' + table + ' where dialogue_act_id = ' + str(da_id)
    cursor.execute(query)
    results = cursor.fetchone()
    da_id = results[0]
    return da_id


def find_all_da_occurances_taxonomy(table, da, taxonomy, cursor):
    if taxonomy == 'full':
        da_id = find_da_by_name(da,'Dialogue_act_full', cursor)
        query = 'select tweet_id, start_offset, end_offset, dialogue_act_id_full from ' + \
                table + ' where dialogue_act_id_full = ' + str(da_id)
    elif taxonomy == 'reduced':
        da_id = find_da_by_name(da,'Dialogue_act_reduced', cursor)
        query = 'select tweet_id, start_offset, end_offset, dialogue_act_id_reduced from ' + \
                table + ' where dialogue_act_id_reduced = ' + str(da_id)
    else:
        da_id = find_da_by_name(da,'Dialogue_act_minimal', cursor)
        query = 'select tweet_id, start_offset, end_offset, dialogue_act_id_min from ' + \
                table + ' where dialogue_act_id_min = ' + str(da_id)
    cursor.execute(query)
    results = cursor.fetchall()
    return results


def find_all_utterance_by_da(table, da, taxonomy, cursor):
    if taxonomy == 'full':
        da_id = find_da_by_name(da,'Dialogue_act_full', cursor)
        query = 'select * from ' + \
                table + ' where dialogue_act_id_full = ' + str(da_id)
    elif taxonomy == 'reduced':
        da_id = find_da_by_name(da,'Dialogue_act_reduced', cursor)
        query = 'select * from ' + \
                table + ' where dialogue_act_id_reduced = ' + str(da_id)
    else:
        da_id = find_da_by_name(da,'Dialogue_act_minimal', cursor)
        query = 'select * from ' + \
                table + ' where dialogue_act_id_min = ' + str(da_id)
    cursor.execute(query)
    results = cursor.fetchall()
    return results


def get_utterance_da_by_tweet_id(table, id, cursor):

    query = 'select * from ' + table + ' where tweet_id = ' + str(id)
    cursor.execute(query)
    results = cursor.fetchone()
    return results


def update_da_prediction(da_name, tweet_id, start_offset, end_offset, taxonomy, cursor, connection):
    if taxonomy == 'full':
        da_id = find_da_by_name(da_name, postgres_configuration.fullOntologyTable, cursor)
        query = 'update segmentation_prediction set dialogue_act_id_full = ' + str(da_id) + \
                ' where tweet_id = ' + tweet_id + ' and start_offset = ' + str(start_offset) \
                + ' and end_offset= ' + str(end_offset)
    elif taxonomy == 'reduced':
        da_id = find_da_by_name(da_name, postgres_configuration.reducedOntologyTable, cursor)
        query = 'update segmentation_prediction set dialogue_act_id_reduced = ' + str(da_id) + \
                ' where tweet_id = ' + tweet_id + ' and start_offset = ' + str(start_offset) \
                + ' and end_offset= ' + str(end_offset)
    else:
        da_id = find_da_by_name(da_name, postgres_configuration.minimalOntologyTable, cursor)
        query = 'update segmentation_prediction set dialogue_act_id_min = ' + str(da_id) + \
                ' where tweet_id = ' + tweet_id + ' and start_offset = ' + str(start_offset) \
                + ' and end_offset= ' + str(end_offset)
    cursor.execute(query)
    connection.commit()


def find_tokens_by_offset(tweet_id, start_offset, end_offset, cursor):
    end_offset += 1
    start_offset -= 1
    query = 'select token_offset, token from annotated_token_tweet where tweet_id =' + str(tweet_id) + \
            ' and token_offset > ' + str(start_offset) + ' and token_offset < ' + str(end_offset) + \
            ' order by token_offset asc'
    cursor.execute(query)
    results = cursor.fetchall()
    return results


def count_segments_training_set(training_set):
    segment_count = 0
    for conversation in training_set:
        all_nodes = conversation.all_nodes()
        for node in all_nodes:
            tweet_id = node.tag
            segments = find_segments(tweet_id)
            segment_count += len(segments)
    return segment_count


def find_utterance_tweet(taxonomy, tweet_id, cursor):
    if taxonomy == 'full':
        query = 'select s.utterance, da.dialogue_act_name from ' + postgres_configuration.segmentationUtteranceTable + ' as s, ' \
                + postgres_configuration.fullOntologyTable + ' as da where s.dialogue_act_id_full = da.dialogue_act_id' \
                                  ' and s.tweet_id= ' + str(tweet_id)
    elif taxonomy == 'reduced':
        query = 'select s.utterance, da.dialogue_act_name from ' + postgres_configuration.segmentationUtteranceTable + ' as s, ' \
                + postgres_configuration.reducedOntologyTable + ' as da where s.dialogue_act_id_reduced = da.dialogue_act_id' \
                                     ' and s.tweet_id= ' + str(tweet_id)
    else:
        query = 'select s.utterance, da.dialogue_act_name from ' + postgres_configuration.segmentationUtteranceTable + ' as s, ' \
                + postgres_configuration.minimalOntologyTable + ' as da where s.dialogue_act_id_min = da.dialogue_act_id' \
                                 ' and s.tweet_id= ' + str(tweet_id)
    cursor.execute(query)
    results = cursor.fetchall()
    return results


def count_end_conversation(cursor):
    query = 'select distinct tweet_id from tweet where position_in_conversation = \'end\''
    cursor.execute(query)
    results = cursor.rowcount
    return results


def count_start_conversation(cursor):
    # connection, cursor = postgres_configuration.make_connection()
    query = 'select distinct tweet_id from tweet where position_in_conversation = \'start\''
    cursor.execute(query)
    results = cursor.rowcount
    return results


def find_username_by_tweet_id(tweet_id, cursor):
    query = 'select username from tweet where tweet_id = ' + str(tweet_id)
    cursor.execute(query)
    results = cursor.fetchone()
    return results[0]


def update_lang_info(filename, cursor, connection):
    for line in open(filename,'r'):
        cursor.execute(line)
        connection.commit()


def delete_non_german_tweets(tweets_list, cursor, connection):
    for tweet in tweets_list:
        query = 'delete from tweet where tweet_id = ' + str(tweet)
        cursor.execute(query)
        connection.commit()


def find_all_tweets(cursor):
    query = 'select tweet_id from tweet'
    cursor.execute(query)
    results = cursor.fetchall()
    return results


def join_tables(taxonomy, cursor):
    if taxonomy == 'full':
        query = 'SELECT gs.dialogue_act_id_full, pr.dialogue_act_id_full' \
                ' FROM ' + postgres_configuration.segmentationUtteranceTable + ' as gs' \
                ' JOIN ' + postgres_configuration.segmentationPredictionTable + ' as pr ' \
                'ON pr.tweet_id = gs.tweet_id and pr.start_offset = gs.start_offset'
    elif taxonomy == 'reduced':
        query = 'SELECT gs.dialogue_act_id_reduced, pr.dialogue_act_id_reduced' \
                ' FROM ' + postgres_configuration.segmentationUtteranceTable + ' as gs' \
                ' JOIN ' + postgres_configuration.segmentationPredictionTable + ' as pr ' \
                'ON pr.tweet_id = gs.tweet_id and pr.start_offset = gs.start_offset'
    else:
        query = 'SELECT gs.dialogue_act_id_min, pr.dialogue_act_id_min' \
                ' FROM ' + postgres_configuration.segmentationUtteranceTable + ' as gs' \
                ' JOIN ' + postgres_configuration.segmentationPredictionTable + ' as pr ' \
                'ON pr.tweet_id = gs.tweet_id and pr.start_offset = gs.start_offset'
    cursor.execute(query)
    results = cursor.fetchall()
    return results


def get_all_da(taxonomy, cursor):
    if taxonomy == 'full':
        query = 'select dialogue_act_id, dialogue_act_name from ' + postgres_configuration.fullOntologyTable
    elif taxonomy == 'reduced':
        query = 'select dialogue_act_id, dialogue_act_name from ' + postgres_configuration.reducedOntologyTable
    else:
        query = 'select dialogue_act_id, dialogue_act_name from ' + postgres_configuration.minimalOntologyTable
    cursor.execute(query)
    results = cursor.fetchall()
    return results



