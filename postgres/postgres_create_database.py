from postgres import insert_to_table, postgres_queries, update_table
from postgres.postgres_configuration import check_if_exists_tweet_table, create_db
import postgres.update_table
from prepare_gold_standard import rebuild_conversations
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
        # update language info
        print 'Update language information'
        postgres.update_table.update_lang_info('postgres/update_lang_info.sql', cursor, connection)
        # check language, delete non german tweets and their children
        print 'Delete non-german tweets and their children'
        german_tweet_id = rebuild_conversations.delete_non_german_tweets(cursor, connection)
        print 'Insert to segmentation table'
        insert_to_table.insert_annotated_table(list_of_tweets, german_tweet_id, cursor, connection)

        # insert_to_table.make_segmentation_utterance_table(cursor, connection)
        print 'Update tweet position in conversation'
        update_table.update_position_conversation_column(cursor, connection)
        print 'Gold standard is inserted'

    else:
        print 'Gold standard is already there'