__author__ = 'snownettle'
import postgres_queries, postgres_configuration
from da_taxonomy import matching_schema


def update_segmentation_prediction_table(tweet_id, segment, da_full, da_reduced, da_min, connection, cursor):
    query = 'update segmentation_prediction set dialogue_act_id_full = ' + \
            str(da_full) + ', dialogue_act_id_reduced = ' + str(da_reduced) + ', dialogue_act_id_min = ' + \
            str(da_min) + ' where tweet_id = ' + str(tweet_id) + ' and segmentation_offsets = \' ' + segment + ' \''
    cursor.execute(query)
    connection.commit()


def update_position_conversation_column(cursor, connection):
    query_start = 'update tweet set position_in_conversation = \'start\' where in_replay_to is null'
    cursor.execute(query_start)
    connection.commit()
    query_end = 'update tweet set position_in_conversation = \'end\' ' \
                'where tweet.tweet_id in (' \
                'select distinct t3.tweet_id from tweet as t3 where t3.tweet_id not in (' \
                'select distinct t1.tweet_id from tweet as t1, tweet as t2 where t1.tweet_id = t2.in_replay_to))'
    cursor.execute(query_end)
    connection.commit()
    query_int = 'update tweet set position_in_conversation = \'intermediate\'  where position_in_conversation is null'
    cursor.execute(query_int)
    connection.commit()


def update_segmentation_prediction_table_baseline(cursor, connection):
    records = postgres_queries.find_all_records('Segmentation', cursor)
    da_id_full = postgres_queries.find_da_by_name('IT_IP_Inform', 'dialogue_act_full', cursor)
    da_reduced = matching_schema.match_reduced(da_id_full, cursor)
    da_id_reduced = postgres_queries.find_da_by_name(da_reduced, 'dialogue_act_reduced', cursor)
    da_min = matching_schema.match_min(da_id_full, cursor)
    da_id_min = postgres_queries.find_da_by_name(da_min, 'dialogue_act_minimal', cursor)
    tweet_list = list()
    for record in records:
        tweet_id = record[0]
        start_offset = record[1]
        end_offset = record[2]
        tweet = (tweet_id, start_offset, end_offset)
        tweet_list.append(tweet)
    query = 'update segmentation_prediction set dialogue_act_id_full = ' + \
            str(da_id_full) + ', dialogue_act_id_reduced = ' + str(da_id_reduced) + ', dialogue_act_id_min = ' + \
            str(da_id_min) + ' where tweet_id = %s and start_offset = %s and end_offset = %s'
    cursor.executemany(query, tweet_list)
    connection.commit()


def update_da_prediction_bulk(tuples, taxonomy, cursor, connection):
    if taxonomy == 'full':
        query = 'update segmentation_prediction set dialogue_act_id_full = %s where tweet_id =  %s ' \
                'and start_offset = %s  and end_offset= %s'
    elif taxonomy == 'reduced':
        query = 'update segmentation_prediction set dialogue_act_id_reduced = %s where tweet_id = %s' \
                ' and start_offset = %s and end_offset= %s'
    else:
        query = 'update segmentation_prediction set dialogue_act_id_min = %s where tweet_id = %s' \
                ' and start_offset = %s and end_offset= %s'
    cursor.executemany(query, tuples)
    connection.commit()


def update_lang_info(filename, cursor, connection):
    for line in open(filename,'r'):
        cursor.execute(line)
        connection.commit()


def update_da_prediction_baseline(taxonomy, cursor, connection):
    # connection, cursor = postgres_configuration.make_connection()
    if taxonomy == 'full':
        da_id = postgres_queries.find_da_by_name('IT_IP_Inform', postgres_configuration.fullOntologyTable, cursor)
        query = 'update segmentation_prediction set dialogue_act_id_full = ' + str(da_id)
    elif taxonomy == 'reduced':
        da_id = postgres_queries.find_da_by_name('IT_IP_Inform', postgres_configuration.reducedOntologyTable, cursor)
        query = 'update segmentation_prediction set dialogue_act_id_reduced = ' + str(da_id)
    else:
        da_id = postgres_queries.find_da_by_name('IT_IP', postgres_configuration.minimalOntologyTable, cursor)
        query = 'update segmentation_prediction set dialogue_act_id_min = ' + str(da_id)
    cursor.execute(query)
    connection.commit()
