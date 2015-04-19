__author__ = 'snownettle'

import postgres_configuration
from annotation import dialogue_acts_tree


def insert_raw_tweets(tweets):
    connection, cursor = postgres_configuration.make_connection()
    query = "INSERT INTO Tweet (Tweet_id, In_replay_to, Conversation_id, Tweet_text, Annotated, German) " \
            "VALUES (%s, %s, %s, %s, %s, %s) "
    cursor.executemany(query, tweets)
    connection.commit()
    postgres_configuration.close_connection(connection)


def insert_dialogue_act_names():
    if select_da():
        dialogue_act_names_tree = dialogue_acts_tree.build_da_taxonomy()
        root = dialogue_act_names_tree.root
        da_list = list()
        da_tuple = (1, root, None)
        da_list.append(da_tuple)
        da_tuple = find_children(dialogue_act_names_tree, root, da_list)
        connection, cursor = postgres_configuration.make_connection()
        query = "INSERT INTO Dialogue_act (Dialogue_act_id, Dialogue_act_name, Parent_act_id) VALUES (%s, %s, %s)"
        cursor.executemany(query, da_tuple)
        connection.commit()
        postgres_configuration.close_connection(connection)


def find_children(tree, parent, da_list):
    if parent == 'DIT++ Taxonomy':
        children = tree.children(parent)
    else:
        children = tree.children(parent.tag)
    for child in children:
        if parent == 'DIT++ Taxonomy':
            # print 'here'
            current_tuple = (len(da_list) + 1, child.tag, 1)
        else:
            parent_id = find_parent_id(da_list, parent.tag)
            current_tuple = (len(da_list) + 1, child.tag, parent_id)
        da_list.append(current_tuple)
        find_children(tree, child, da_list)
    return da_list


def find_parent_id(da_list, parent_name):
    for da in da_list:
        if da[1] == parent_name:
            return da[0]
    return 0


def select_all_tweets():
    connection, cursor = postgres_configuration.make_connection()
    query = 'SELECT Tweet_id FROM Tweet'
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    tweets_list = set()
    for result in results:
        tweets_list.add(str(result[0]))
    return tweets_list


def select_da():
    connection, cursor = postgres_configuration.make_connection()
    query = 'select * from Dialogue_act'
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        postgres_configuration.close_connection(connection)
        return True
    else:
        postgres_configuration.close_connection(connection)
        return False


def insert_annotated_tweets(tweets_list): # insert to segment table
    connection, cursor = postgres_configuration.make_connection()
    for tweet in tweets_list:
        segments = tweet.get_segments()
        for segment_offset, da in segments.iteritems():
            query = 'select dialogue_act_id from dialogue_act where dialogue_act_name = \'' + da + '\''
            cursor.execute(query)
            results = cursor.fetchall()
            for result in results:
                segments_tuple = (int(tweet.get_tweet_id()), segment_offset, result[0])
                query = 'insert into segmentation (tweet_id, segmentation_offsets, dialogue_act_id) values (%s, %s, %s)'
                cursor.executemany(query, [segments_tuple])
                connection.commit()
        tokens = tweet.get_tokens()
        for offset, token_da in tokens.iteritems():
            for token, da in token_da.iteritems():
                query = 'select dialogue_act_id from dialogue_act where dialogue_act_name = \'' + da + '\''
                cursor.execute(query)
                results = cursor.fetchall()
                for result in results:
                    token_da_tuple = (int(tweet.get_tweet_id()), offset, token, result[0])
                    query = 'insert into annotated_token_tweet (tweet_id, token_offset, token, dialogue_act_id) ' \
                            'values (%s, %s, %s, %s) '
                    cursor.executemany(query, [token_da_tuple])
                    connection.commit()

    postgres_configuration.close_connection(connection)

