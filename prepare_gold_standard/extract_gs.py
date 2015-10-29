__author__ = 'snownettle'
from mongoDB import mongoDB_configuration
from readData import rawAnnotatedData_read
import annotated_tweets_final
from postgres import postgres_configuration, insert_to_table, update_table
import rebuild_conversations
from prepare_gold_standard.editing_annotated_tweets import tweets_to_be_reviewed
from readData.rawAnnotatedData_read import concatenate_done_tweets


def analyze_original_data(connection, cursor):
    print 'start'
    # connection, cursor = postgres_configuration.make_connection()
    if postgres_configuration.check_if_exists_tweet_table(cursor) is False:
        # create db
        postgres_configuration.create_db()
        print 'Database is created'

        # insert dit++
        insert_to_table.insert_dialogue_act_names_full(connection, cursor)
        insert_to_table.insert_dialogue_act_names_reduced(connection, cursor)
        insert_to_table.insert_dialogue_act_names_minimal(connection, cursor)
        print 'DIT++ taxonomy is inserted'

    database_name = mongoDB_configuration.db_name
    collectionNameAllAnnotations = mongoDB_configuration.collectionNameAllAnnotations

    annotatedData_path = mongoDB_configuration.pathToAnnotatedData
    # make connection to mongodb
    collectionAllAnnotation = mongoDB_configuration.get_collection(database_name, collectionNameAllAnnotations)


    if mongoDB_configuration.check_tweets_amount(collectionAllAnnotation) == 0:
        print 'Start inserting to mongoDB...'
        rawAnnotatedData_read.import_annotated_docs(annotatedData_path, collectionAllAnnotation)
        print 'Collection ' + collectionNameAllAnnotations + ' is already existed and has ' \
              + str(mongoDB_configuration.check_tweets_amount(collectionAllAnnotation)) + ' records'
    else:
        print 'Collection ' + collectionNameAllAnnotations + ' is already existed and has ' \
              + str(mongoDB_configuration.check_tweets_amount(collectionAllAnnotation)) + ' records'


    conversation_list = rebuild_conversations.build_conversation_from_mongo(collectionAllAnnotation)

    # if postgres_configuration.check_if_exists_tweet_table() is False:
    insert_to_table.insert_into_edit_tweet_table(conversation_list, connection, cursor)
    update_table.update_lang_info('postgres/update_lang_info.sql', cursor, connection)
    # delete non german
    german_tweets = rebuild_conversations.delete_non_german_tweets(cursor, connection)
    tweets_list = tweets_to_be_reviewed(collectionAllAnnotation, german_tweets)
    print '\n' + '\033[1m' + 'Full ontology'
    print '\033[0m'
    agreed, tweets_to_edit = annotated_tweets_final.iaa_ontologies(tweets_list,  ontology='full', cursor=cursor)
    # annotated_tweets_final.merging(agreed, tweets_to_edit)
    print '\n' + '\033[1m' + 'Reduced ontology'
    print '\033[0m'
    annotated_tweets_final.iaa_ontologies(tweets_list, ontology='reduced', cursor=cursor)
    print '\n' + '\033[1m' + 'Minimal ontology'
    print '\033[0m'
    annotated_tweets_final.iaa_ontologies(tweets_list, ontology='minimal', cursor= cursor)

    # merging
    annotated_tweets_final.merging(agreed, tweets_to_edit)
    concatenate_done_tweets(cursor, connection)



