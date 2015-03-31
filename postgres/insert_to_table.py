__author__ = 'snownettle'

import postgres_configuration


def insert_annotated_conversations(tweet):
    connection, cursor = postgres_configuration.make_connection()
    query = "INSERT INTO Annotated_tweets (Tweet_id, In_replay_to) VALUES (%s, %s)"
    cursor.executemany(query, tweet)
    connection.commit()
    postgres_configuration.close_connection(connection)


def insert_raw_tweets(tweets):
    connection, cursor = postgres_configuration.make_connection()
    query = "INSERT INTO Tweet (Tweet_id, In_replay_to, Text) VALUES (%s, %s, %s)"
    cursor.executemany(query, tweets)
    connection.commit()
    postgres_configuration.close_connection(connection)


