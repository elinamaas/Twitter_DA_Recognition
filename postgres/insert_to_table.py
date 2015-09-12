__author__ = 'snownettle'

import postgres_configuration
from da_recognition import dialogue_acts_taxonomy, matching_schema
import postgres_queries
from mongoDB import mongoDBQueries, mongoDB_configuration
from general import check_lang


def insert_raw_tweets(tweets):
    connection, cursor = postgres_configuration.make_connection()
    query = "INSERT INTO Tweet (Tweet_id, In_replay_to, Conversation_id, Tweet_text, Annotated, German) " \
            "VALUES (%s, %s, %s, %s, %s, %s) "
    cursor.executemany(query, tweets)
    connection.commit()
    postgres_configuration.close_connection(connection)


def insert_into_edit_tweet_table(conversation_list):
    collection = mongoDB_configuration.get_collection(mongoDB_configuration.db_name,
                                                      mongoDB_configuration.collectionNameAllAnnotations)
    connection, cursor = postgres_configuration.make_connection()
    conversation_id = 1
    for conversation in conversation_list:
        all_tweets = conversation.all_nodes()
        for tweet in all_tweets:
            tweet_data = mongoDBQueries.find_by_id(collection, tweet.tag)[0]
            tweet_id = tweet_data['tweet_id']
            if tweet_data['text_id'] == 0:
                parent_tweet = 'NULL'
            else:
                parent_tweet = conversation.parent(tweet_id).tag
            tweet_text = tweet_data['text'].split('user=')[1]
            username = tweet_text.split(' ')[0]

            if tweet_text != '':

                tweet_text = tweet_text.split(username)[1]
                if '\'' in tweet_text:
                    tweet_text = tweet_text.replace('\'', '\'\'')
                german = check_lang.check_german(tweet_text)
                query = "INSERT INTO Tweet (Tweet_id, In_replay_to, Conversation_id, Tweet_text, Annotated, German) " \
                    "VALUES (%s, %s, %s, \'%s\', %s, %s) " % (tweet_id, parent_tweet, conversation_id, tweet_text, True, german)
                # print query
                cursor.execute(query)
                connection.commit()
        conversation_id += 1
    postgres_configuration.close_connection(connection)


def insert_dialogue_act_names_full(connection, cursor):
    if select_da('Dialogue_act_full'):
        dialogue_act_names_tree = dialogue_acts_taxonomy.build_da_taxonomy_full()
        root = dialogue_act_names_tree.root
        da_list = list()
        da_tuple = (1, root, None)
        da_list.append(da_tuple)
        da_tuple = find_children(dialogue_act_names_tree, root, da_list)
        # connection, cursor = postgres_configuration.make_connection()
        query = "INSERT INTO Dialogue_act_full (Dialogue_act_id, Dialogue_act_name, Parent_act_id) VALUES (%s, %s, %s)"
        cursor.executemany(query, da_tuple)
        connection.commit()
        # postgres_configuration.close_connection(connection)


def insert_dialogue_act_names_reduced(connection, cursor):
    if select_da('Dialogue_act_reduced'):
        dialogue_act_names_tree = dialogue_acts_taxonomy.build_da_taxonomy_reduced()
        root = dialogue_act_names_tree.root
        da_list = list()
        da_tuple = (1, root, None)
        da_list.append(da_tuple)
        da_tuple = find_children(dialogue_act_names_tree, root, da_list)
        # connection, cursor = postgres_configuration.make_connection()
        query = "INSERT INTO Dialogue_act_reduced (Dialogue_act_id, Dialogue_act_name, Parent_act_id) " \
                "VALUES (%s, %s, %s)"
        cursor.executemany(query, da_tuple)
        connection.commit()
        # postgres_configuration.close_connection(connection)


def insert_dialogue_act_names_minimal(connection, cursor):
    if select_da('Dialogue_act_minimal'):
        dialogue_act_names_tree = dialogue_acts_taxonomy.build_da_taxonomy_minimal()
        root = dialogue_act_names_tree.root
        da_list = list()
        da_tuple = (1, root, None)
        da_list.append(da_tuple)
        da_tuple = find_children(dialogue_act_names_tree, root, da_list)
        # connection, cursor = postgres_configuration.make_connection()
        query = "INSERT INTO Dialogue_act_minimal (Dialogue_act_id, Dialogue_act_name, Parent_act_id) " \
                "VALUES (%s, %s, %s)"
        cursor.executemany(query, da_tuple)
        connection.commit()
        # postgres_configuration.close_connection(connection)


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


def select_da(table):
    connection, cursor = postgres_configuration.make_connection()
    query = 'select * from ' + table
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        postgres_configuration.close_connection(connection)
        return True
    else:
        postgres_configuration.close_connection(connection)
        return False


def insert_annotated_tweets_to_segment_table(tweets_list): # insert to segment table
    connection, cursor = postgres_configuration.make_connection()
    for tweet in tweets_list:
        segments = tweet.get_segments()
        for segment_offset, da in segments.iteritems():
            # query = 'select dialogue_act_id from dialogue_act where dialogue_act_name = \'' + da + '\''
            # cursor.execute(query)
            # results = cursor.fetchall()
            results = postgres_queries.find_da_by_name(da)
            for result in results:
                segments_tuple = (int(tweet.get_tweet_id()), segment_offset, result[0])
                query = 'insert into segmentation (tweet_id, segmentation_offsets, dialogue_act_id) values (%s, %s, %s)'
                cursor.executemany(query, [segments_tuple])
                connection.commit()
        tokens = tweet.get_tokens()
        for offset, token_da in tokens.iteritems():
            for token, da in token_da.iteritems():
                # query = 'select dialogue_act_id from dialogue_act where dialogue_act_name = \'' + da + '\''
                # cursor.execute(query)
                # results = cursor.fetchall()
                results = postgres_queries.find_da_by_name(da)
                for result in results:
                    token_da_tuple = (int(tweet.get_tweet_id()), offset, token, result[0])
                    query = 'insert into annotated_token_tweet (tweet_id, token_offset, token, dialogue_act_id) ' \
                            'values (%s, %s, %s, %s) '
                    cursor.executemany(query, [token_da_tuple])
                    connection.commit()

    postgres_configuration.close_connection(connection)


def insert_into_segmantation_prediction_table(tweet_id, start_offset, end_offset, da_id_full, da_reduced, da_min):
    connection, cursor = postgres_configuration.make_connection()
    query = 'INSERT INTO Segmentation_Prediction (Tweet_id, start_offset, end_offset, dialogue_act_id_full, ' \
            'dialogue_act_id_reduced, dialogue_act_id_min)' \
            'VALUES (%s, %s , %s,  %s, %s, %s) ' %(tweet_id, start_offset, end_offset, da_id_full, da_reduced, da_min)
    cursor.execute(query)
    connection.commit()
    postgres_configuration.close_connection(connection)


def make_segmentation_utterance_table(cursor, connection):
    # connection, cursor = postgres_configuration.make_connection()
    segmentation_table_records = postgres_queries.find_all_records('segmentation', cursor)
    segments_utt_data = list()
    for record in segmentation_table_records:
        tweet_id = record[0]
        # segmentation_offset = record[1]
        da_id_full = record[3]
        da_id_reduced = record[4]
        da_id_min = record[5]
        start_offset = record[1]
        end_offset = record[2]
        token_results = postgres_queries.find_tokens_by_offset(tweet_id, start_offset, end_offset, cursor)
        tokens = str() # as string with space
        for token in token_results:
            tokens += token[1] + ' '
        # delete last whitespace
        tokens = tokens[:-1]
        segments_utt_dict = {'tweet_id':tweet_id, 'start_offset': start_offset, 'end_offset': end_offset,
                             'utterance': tokens, 'da_full': da_id_full,
                             'da_reduced': da_id_reduced, 'da_min': da_id_min}
        segments_utt_data.append(segments_utt_dict)
    query = 'INSERT INTO Segments_utterance (Tweet_id , start_offset, end_offset, Utterance, ' \
            'Dialogue_act_id_full, Dialogue_act_id_reduced, Dialogue_act_id_min) ' \
            'VALUES (%(tweet_id)s, %(start_offset)s, %(end_offset)s, %(utterance)s, ' \
            '%(da_full)s, %(da_reduced)s, %(da_min)s)'
    cursor.executemany(query, segments_utt_data)
    connection.commit()
    # postgres_configuration.close_connection(connection)


def multiple_tweets_insert(tweets_list, connection, cursor):
    connection, cursor = postgres_configuration.make_connection()
    query_tuple = ()
    for tweet in tweets_list:
        tweet_id = tweet.get_tweet_id()
        tweet_text = tweet.get_tweet_text()
        username = tweet.get_username()
        if '\'' in tweet_text:
            tweet_text = tweet_text.replace('\'', '\'\'')
        in_replay_to = str(tweet.get_in_replay_to_id())
        if in_replay_to == 'None ':
            in_replay_to = None
        conversation_id = tweet.get_conversation_id()
        german = check_lang.check_german(tweet_text)
        tweet_tuple = (tweet_id, username, in_replay_to, conversation_id, tweet_text, True, german)
        query_tuple = (tweet_tuple,) + query_tuple
    query = 'INSERT INTO Tweet (Tweet_id, Username, In_replay_to, Conversation_id, Tweet_text, Annotated, German) ' \
            'VALUES (%s, %s, %s, %s , %s , %s, %s)'
    cursor.executemany(query, query_tuple)
    connection.commit()
    # postgres_configuration.close_connection(connection)


def insert_annotated_table(list_of_tweets, german_tweet_id, cursor, connection):
    # connection, cursor = postgres_configuration.make_connection()
    segment_dict_list = list()
    token_dict_list = list()
    ontology_dict = matching_schema.make_ontology_dict(cursor)
    for tweet in list_of_tweets:
        tweet_id = int(tweet.get_tweet_id())
        if tweet_id in german_tweet_id:
            tokens = tweet.get_tokens()
            segments = tweet.get_segments()
            for offset, token_da in tokens.iteritems():
                token = token_da[0]
                if type(token) is unicode:
                    if '\'' in token:
                        token = token.replace('\'', '\'\'')
                da_id_ontologies = ontology_dict[token_da[1]]
                da_id_full = da_id_ontologies[0]
                da_id_reduced = da_id_ontologies[1]
                da_id_min = da_id_ontologies[2]
                token_dict = {'tweet_id': tweet_id, 'offset': offset, 'token': token, 'da_id_full': da_id_full,
                              'da_id_reduced': da_id_reduced, 'da_id_min': da_id_min}
                token_dict_list.append(token_dict)

            for segment, da in segments.iteritems():
                da_id_ontologies = ontology_dict[da]
                da_id_full = da_id_ontologies[0]
                da_id_reduced = da_id_ontologies[1]
                da_id_min = da_id_ontologies[2]
                start_offset = int(segment.split(':')[0])
                end_offset = int(segment.split(':')[1])
                segment_dict = {'tweet_id': tweet_id, 'start_offset': start_offset, 'end_offset': end_offset,
                                'da_id_full': da_id_full,
                                'da_id_reduced': da_id_reduced, 'da_id_min': da_id_min}
                segment_dict_list.append(segment_dict)

    query_segmentation = 'insert into segmentation (tweet_id, start_offset, end_offset, dialogue_act_id_full, ' \
                         'dialogue_act_id_reduced, dialogue_act_id_min ) values (%(tweet_id)s, %(start_offset)s, ' \
                         '%(end_offset)s, %(da_id_full)s, %(da_id_reduced)s, %(da_id_min)s)'
    cursor.executemany(query_segmentation, segment_dict_list)
    connection.commit()

    query_tokes = 'insert into annotated_token_tweet (tweet_id, token_offset, token, dialogue_act_id_full, ' \
                  'dialogue_act_id_reduced, dialogue_act_id_min) values (%(tweet_id)s, %(offset)s, %(token)s,' \
                  ' %(da_id_full)s, %(da_id_reduced)s, %(da_id_min)s) '
    cursor.executemany(query_tokes, token_dict_list)
    connection.commit()


