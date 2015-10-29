from postgres import insert_to_table,  update_table
from postgres.postgres_configuration import check_if_exists_tweet_table, create_db, truncate_tweet_table

from readData import editedAnnotatedData

__author__ = 'snownettle'


def create_db_insert(connection, cursor, file):
    if check_if_exists_tweet_table(cursor) is False:
    # create db
        create_db()
        print 'Database is created'

        # insert dit++
        insert_to_table.insert_dialogue_act_names_full(connection, cursor)
        insert_to_table.insert_dialogue_act_names_reduced(connection, cursor)
        insert_to_table.insert_dialogue_act_names_minimal(connection, cursor)
        print 'DIT++ taxonomy is inserted'

        # insert golden standard to db
        print 'Start inserting gold standard'
        list_of_tweets = editedAnnotatedData.import_golden_standard_postgres(file, cursor, connection)
        print 'Insert to segmentation table'
        insert_to_table.insert_annotated_table(list_of_tweets, cursor, connection)

        # insert_to_table.make_segmentation_utterance_table(cursor, connection)
        print 'Update tweet position in conversation'
        update_table.update_position_conversation_column(cursor, connection)
        print 'Gold standard is inserted'

    else:
        # truncate_tweet_table(connection, cursor)
        # print 'Start inserting gold standard'
        # list_of_tweets = editedAnnotatedData.import_golden_standard_postgres(file, cursor, connection)
        # print 'Insert to segmentation table'
        # insert_to_table.insert_annotated_table(list_of_tweets, cursor, connection)
        # # insert_to_table.make_segmentation_utterance_table(cursor, connection)
        # print 'Update tweet position in conversation'
        # update_table.update_position_conversation_column(cursor, connection)

        print 'Gold standard is inserted'
