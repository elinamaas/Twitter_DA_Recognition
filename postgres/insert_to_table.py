__author__ = 'snownettle'

import postgres_configuration
from annotation import dialogue_acts_tree


def insert_annotated_conversations(tweet):
    connection, cursor = postgres_configuration.make_connection()
    query = "INSERT INTO Annotated_tweets (Tweet_id)"
    cursor.executemany(query, tweet)
    connection.commit()
    postgres_configuration.close_connection(connection)


def insert_raw_tweets(tweets):
    connection, cursor = postgres_configuration.make_connection()
    query = "INSERT INTO Tweet (Tweet_id, In_replay_to, Conversation_id, Tweet_text, Annotated) " \
            "VALUES (%s, %s, %s, %s, %s) "
    cursor.executemany(query, tweets)
    connection.commit()
    postgres_configuration.close_connection(connection)


def insert_dialogue_act_names():
    dialogue_act_names_tree = dialogue_acts_tree.build_da_taxonomy()
    root = dialogue_act_names_tree.root()
    da_id = 1
    da_tuple = (da_id, root.tag, 0)
    da_tuple = find_children(dialogue_act_names_tree, root, da_tuple, da_id)
    connection, cursor = postgres_configuration.make_connection()
    query = "INSERT INTO Dialogue_act (Dialogue_act_id, Dialogue_act_name, Parent_act_id) VALUES (%s, %s, %s)"
    cursor.executemany(query, da_tuple)
    connection.commit()
    postgres_configuration.close_connection(connection)


def find_children(tree, parent, da_tuple, da_id):
    children = tree.children(parent)
    for child in children:
        da_id += 1
        da_tuple = (da_tuple,) + (da_id, child.tag, parent.tag)
        find_children(tree, parent, da_tuple, da_id)
    return da_tuple


def select_all_tweets():
    connection, cursor = postgres_configuration.make_connection()
    query = 'SELECT Tweet_id FROM Tweet'
    cursor.execute(query)
    results = cursor.fetchall()
    # connection.commit()
    print results
    postgres_configuration.close_connection(connection)
    tweets_list = list()
    for result in results:
        tweets_list.append(int(result[0]))

    return tweets_list

select_all_tweets()