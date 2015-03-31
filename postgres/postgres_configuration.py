__author__ = 'snownettle'

import psycopg2
import sys


def make_connection():
    con = None

    try:

        con = psycopg2.connect("dbname='dialogue_acts' user='postgres'")

        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS Tweet(Tweet_id BIGINT PRIMARY KEY, "
                    "In_replay_to BIGINT, Text VARCHAR(255))")
        cur.execute("CREATE TABLE IF NOT EXISTS Annotated_tweets(Tweet_id BIGINT PRIMARY KEY, "
                    "In_replay_to BIGINT, FOREIGN KEY (Tweet_id) REFERENCES Tweet (Tweet_id))")

        cur.execute('CREATE TABLE IF NOT EXISTS Dialogue_act (Dialogue_act_id INTEGER PRIMARY KEY, '
                    'Dialogue_act_name VARCHAR(100), Parent_act INTEGER, '
                    'FOREIGN KEY (Parent_act) REFERENCES Dialogue_act(Dialogue_act_id) )')
        cur.execute('CREATE TABLE IF NOT EXISTS Token_tweet (Tweet_id BIGINT, '
                    'Token_offset INTEGER, Token VARCHAR(50), Dialogue_act_id INTEGER, '
                    'PRIMARY KEY(Tweet_id, Token_offset), '
                    'FOREIGN KEY(Tweet_id) REFERENCES Tweet (Tweet_id),'
                    'FOREIGN KEY(Dialogue_act_id) REFERENCES Dialogue_act (Dialogue_act_id))')
        cur.execute('CREATE TABLE IF NOT EXISTS Segmentation(Tweet_id BIGINT PRIMARY KEY, '
                    'Segmentation_offsets VARCHAR(10),'
                    ' Dialogue_act_id INTEGER, FOREIGN KEY(Tweet_id) REFERENCES Tweet (Tweet_id), '
                    'FOREIGN KEY(Dialogue_act_id) REFERENCES  Dialogue_act(Dialogue_act_id))')

        con.commit()
    except psycopg2.DatabaseError, e:
        if con:
            con.rollback()
        print 'Error %s' % e
        sys.exit(1)
    return con, cur


def close_connection(connection):
    connection.close()