__author__ = 'snownettle'

import psycopg2
import sys


fullOntologyTable = 'Dialogue_act_full'
reducedOntologyTable = 'Dialogue_act_reduced'
minimalOntologyTable = 'Dialogue_act_minimal'
tweetTable = 'Tweet'
editingTweetTable = 'EditTweet'
annotatedTokensTable = 'Annotated_token_tweet'
segmentationTable = 'Segmentation'
segmentationPredictionTable = 'Segmentation_Prediction'
segmentationUtteranceTable = 'Segments_utterance'


def create_db():
    con = None

    try:

        con = psycopg2.connect("dbname='dialogue_acts' user='postgres'")

        cur = con.cursor()

        # cur.execute('drop table Annotated_token_tweet')
        # cur.execute('drop table Segmentation')
        # cur.execute('drop table Tweet')
        cur.execute('CREATE TYPE e_position AS ENUM (\'start\', \'end\', \'intermediate\')')

        cur.execute("CREATE TABLE IF NOT EXISTS Tweet(Tweet_id BIGINT PRIMARY KEY, UserName VARCHAR(1024), "
                    "In_replay_to BIGINT, Conversation_id BIGINT, Tweet_text VARCHAR(1024), "
                    "Annotated BOOLEAN, German Boolean, position_in_conversation e_position )")

        # cur.execute("CREATE TABLE IF NOT EXISTS EditTweet(Tweet_id BIGINT PRIMARY KEY, "
        #             "In_replay_to BIGINT, Conversation_id BIGINT, Tweet_text VARCHAR(1024), "
        #             "Annotated BOOLEAN, German Boolean, position_in_conversation e_position )")

        cur.execute('CREATE TABLE IF NOT EXISTS Dialogue_act_full (Dialogue_act_id INTEGER PRIMARY KEY, '
                    'Dialogue_act_name VARCHAR(100), Parent_act_id INTEGER, '
                    'FOREIGN KEY (Parent_act_id) REFERENCES Dialogue_act_full(Dialogue_act_id))')


        cur.execute('CREATE TABLE IF NOT EXISTS Dialogue_act_reduced (Dialogue_act_id INTEGER PRIMARY KEY, '
                    'Dialogue_act_name VARCHAR(100), Parent_act_id INTEGER, '
                    'FOREIGN KEY (Parent_act_id) REFERENCES Dialogue_act_reduced(Dialogue_act_id))')

        cur.execute('CREATE TABLE IF NOT EXISTS Dialogue_act_minimal (Dialogue_act_id INTEGER PRIMARY KEY, '
                    'Dialogue_act_name VARCHAR(100), Parent_act_id INTEGER, '
                    'FOREIGN KEY (Parent_act_id) REFERENCES Dialogue_act_reduced(Dialogue_act_id))')

        cur.execute('CREATE TABLE IF NOT EXISTS Annotated_token_tweet (Tweet_id BIGINT, '
                    'Token_offset INTEGER, Token VARCHAR(255), Dialogue_act_id_full INTEGER, '
                    'Dialogue_act_id_reduced INTEGER, Dialogue_act_id_min INTEGER,'
                    'PRIMARY KEY(Tweet_id, Token_offset), '
                    'FOREIGN KEY(Tweet_id) REFERENCES Tweet (Tweet_id),'
                    'FOREIGN KEY(Dialogue_act_id_full) REFERENCES Dialogue_act_full (Dialogue_act_id), '
                    'FOREIGN KEY(Dialogue_act_id_reduced) REFERENCES Dialogue_act_reduced (Dialogue_act_id), '
                    'FOREIGN KEY(Dialogue_act_id_min) REFERENCES Dialogue_act_minimal (Dialogue_act_id))')

        cur.execute('CREATE TABLE IF NOT EXISTS Segmentation(Tweet_id BIGINT, '
                    'start_offset INTEGER, end_offset INTEGER, Dialogue_act_id_full INTEGER, '
                    'Dialogue_act_id_reduced INTEGER, Dialogue_act_id_min INTEGER, '
                    'PRIMARY KEY (Tweet_id, start_offset, end_offset) , '
                    'FOREIGN KEY(Tweet_id) REFERENCES Tweet (Tweet_id), '
                    'FOREIGN KEY(Dialogue_act_id_full) REFERENCES  Dialogue_act_full(Dialogue_act_id), '
                    'FOREIGN KEY(Dialogue_act_id_reduced) REFERENCES Dialogue_act_reduced (Dialogue_act_id), '
                    'FOREIGN KEY(Dialogue_act_id_min) REFERENCES Dialogue_act_minimal (Dialogue_act_id))')

        cur.execute('CREATE TABLE IF NOT EXISTS Segmentation_Prediction(Tweet_id BIGINT, '
                    'start_offset INTEGER, end_offset INTEGER, Dialogue_act_id_full INTEGER, '
                    'Dialogue_act_id_reduced INTEGER, Dialogue_act_id_min INTEGER, '
                    'PRIMARY KEY (Tweet_id, start_offset, end_offset) , '
                    'FOREIGN KEY(Tweet_id) REFERENCES Tweet (Tweet_id), '
                    'FOREIGN KEY(Dialogue_act_id_full) REFERENCES  Dialogue_act_full(Dialogue_act_id), '
                    'FOREIGN KEY(Dialogue_act_id_reduced) REFERENCES Dialogue_act_reduced (Dialogue_act_id), '
                    'FOREIGN KEY(Dialogue_act_id_min) REFERENCES Dialogue_act_minimal (Dialogue_act_id))')

        cur.execute('create table if not exists Segments_utterance (Tweet_id bigint, start_offset INTEGER, '
                    'end_offset INTEGER, Utterance Varchar(1024), Dialogue_act_id_full INTEGER, '
                    'Dialogue_act_id_reduced INTEGER, Dialogue_act_id_min INTEGER,'
                    'primary key (Tweet_id, start_offset, end_offset), '
                    'foreign key (tweet_id) references tweet(tweet_id),'
                    'FOREIGN KEY(Dialogue_act_id_full) REFERENCES Dialogue_act_full (Dialogue_act_id), '
                    'FOREIGN KEY(Dialogue_act_id_reduced) REFERENCES Dialogue_act_reduced (Dialogue_act_id), '
                    'FOREIGN KEY(Dialogue_act_id_min) REFERENCES Dialogue_act_minimal (Dialogue_act_id))')

        con.commit()
    except psycopg2.DatabaseError, e:
        if con:
            con.rollback()
        print 'Error %s' % e
        sys.exit(1)
    return con, cur


def make_connection():
    con = None

    try:

        con = psycopg2.connect("dbname='dialogue_acts' user='postgres'")

        cur = con.cursor()

        # cur.execute('drop table Annotated_token_tweet')
        # cur.execute('drop table Segmentation')
        # cur.execute('drop table Tweet')
        # cur.execute('CREATE TYPE IF NOT EXISTS e_position AS ENUM (\'start\', \'end\', \'intermediate\')')
        #
        # cur.execute("CREATE TABLE IF NOT EXISTS Tweet(Tweet_id BIGINT PRIMARY KEY, "
        #             "In_replay_to BIGINT, Conversation_id BIGINT, Tweet_text VARCHAR(1024), "
        #             "Annotated BOOLEAN, German Boolean, position_in_conversation e_position )")
        #
        # cur.execute('CREATE TABLE IF NOT EXISTS Dialogue_act_full (Dialogue_act_id INTEGER PRIMARY KEY, '
        #             'Dialogue_act_name VARCHAR(100), Parent_act_id INTEGER, '
        #             'FOREIGN KEY (Parent_act_id) REFERENCES Dialogue_act_full(Dialogue_act_id))')
        #
        #
        # cur.execute('CREATE TABLE IF NOT EXISTS Dialogue_act_reduced (Dialogue_act_id INTEGER PRIMARY KEY, '
        #             'Dialogue_act_name VARCHAR(100), Parent_act_id INTEGER, '
        #             'FOREIGN KEY (Parent_act_id) REFERENCES Dialogue_act_reduced(Dialogue_act_id))')
        #
        # cur.execute('CREATE TABLE IF NOT EXISTS Dialogue_act_minimal (Dialogue_act_id INTEGER PRIMARY KEY, '
        #             'Dialogue_act_name VARCHAR(100), Parent_act_id INTEGER, '
        #             'FOREIGN KEY (Parent_act_id) REFERENCES Dialogue_act_reduced(Dialogue_act_id))')
        #
        # cur.execute('CREATE TABLE IF NOT EXISTS Annotated_token_tweet (Tweet_id BIGINT, '
        #             'Token_offset INTEGER, Token VARCHAR(255), Dialogue_act_id_full INTEGER, '
        #             'Dialogue_act_id_reduced INTEGER, Dialogue_act_id_min INTEGER,'
        #             'PRIMARY KEY(Tweet_id, Token_offset), '
        #             'FOREIGN KEY(Tweet_id) REFERENCES Tweet (Tweet_id),'
        #             'FOREIGN KEY(Dialogue_act_id_full) REFERENCES Dialogue_act_full (Dialogue_act_id), '
        #             'FOREIGN KEY(Dialogue_act_id_reduced) REFERENCES Dialogue_act_reduced (Dialogue_act_id), '
        #             'FOREIGN KEY(Dialogue_act_id_min) REFERENCES Dialogue_act_minimal (Dialogue_act_id))')
        #
        # cur.execute('CREATE TABLE IF NOT EXISTS Segmentation(Tweet_id BIGINT, '
        #             'Segmentation_offsets VARCHAR(10), Dialogue_act_id_full INTEGER, '
        #             'Dialogue_act_id_reduced INTEGER, Dialogue_act_id_min INTEGER, '
        #             'PRIMARY KEY (Tweet_id, Segmentation_offsets) , '
        #             'FOREIGN KEY(Tweet_id) REFERENCES Tweet (Tweet_id), '
        #             'FOREIGN KEY(Dialogue_act_id_full) REFERENCES  Dialogue_act_full(Dialogue_act_id), '
        #             'FOREIGN KEY(Dialogue_act_id_reduced) REFERENCES Dialogue_act_reduced (Dialogue_act_id), '
        #             'FOREIGN KEY(Dialogue_act_id_min) REFERENCES Dialogue_act_minimal (Dialogue_act_id))')
        #
        # cur.execute('CREATE TABLE IF NOT EXISTS Segmentation_Prediction(Tweet_id BIGINT, '
        #             'Segmentation_offsets VARCHAR(10), Dialogue_act_id_full INTEGER, '
        #             'Dialogue_act_id_reduced INTEGER, Dialogue_act_id_min INTEGER, '
        #             'PRIMARY KEY (Tweet_id, Segmentation_offsets) , '
        #             'FOREIGN KEY(Tweet_id) REFERENCES Tweet (Tweet_id), '
        #             'FOREIGN KEY(Dialogue_act_id_full) REFERENCES  Dialogue_act_full(Dialogue_act_id), '
        #             'FOREIGN KEY(Dialogue_act_id_reduced) REFERENCES Dialogue_act_reduced (Dialogue_act_id), '
        #             'FOREIGN KEY(Dialogue_act_id_min) REFERENCES Dialogue_act_minimal (Dialogue_act_id))')
        #
        # cur.execute('create table if not exists Segments_utterance (Tweet_id bigint, Segmentation_offsets VARCHAR(10),'
        #             'Utterance Varchar(1024), Dialogue_act_id_full INTEGER, '
        #             'Dialogue_act_id_reduced INTEGER, Dialogue_act_id_min INTEGER,'
        #             'primary key (Tweet_id, Segmentation_offsets), '
        #             'foreign key (tweet_id) references tweet(tweet_id),'
        #             'FOREIGN KEY(Dialogue_act_id_full) REFERENCES Dialogue_act_full (Dialogue_act_id), '
        #             'FOREIGN KEY(Dialogue_act_id_reduced) REFERENCES Dialogue_act_reduced (Dialogue_act_id), '
        #             'FOREIGN KEY(Dialogue_act_id_min) REFERENCES Dialogue_act_minimal (Dialogue_act_id))')
        #
        # con.commit()
    except psycopg2.DatabaseError, e:
        if con:
            con.rollback()
        print 'Error %s' % e
        sys.exit(1)
    return con, cur


def close_connection(connection):
    connection.close()


def check_if_exists_tweet_table():
    connection, cursor = make_connection()
    cursor.execute('select * from information_schema.tables where table_name=\'tweet\'')
    return bool(cursor.rowcount)


# def check_if_exists_edit_tweet_table():
#     connection, cursor = make_connection()
#     cursor.execute('select * from information_schema.tables where table_name=\'edittweet\'')
#     return bool(cursor.rowcount)