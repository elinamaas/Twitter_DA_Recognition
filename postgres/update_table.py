__author__ = 'snownettle'
import postgres_configuration
import postgres_queries

def update_segmentation_prediction_table(tweet_id, segment, da_full, da_reduced, da_min):
    connection, cursor = postgres_configuration.make_connection()
    query = 'update segmentation_prediction set dialogue_act_id_full = ' + \
            str(da_full) + ', dialogue_act_id_reduced = ' + str(da_reduced) + ', dialogue_act_id_min = ' + \
            str(da_min) + 'where tweet_id = ' + str(tweet_id) + ' and segmentation_offsets = \' ' + segment + ' \''
    cursor.execute(query)
    connection.commit()
    postgres_configuration.close_connection(connection)


def update_position_conversation_column():
    connection, cursor = postgres_configuration.make_connection()
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
    postgres_configuration.close_connection(connection)


