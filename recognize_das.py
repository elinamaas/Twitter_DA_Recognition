__author__ = 'snownettle'
from postgres import insert_to_table, postgres_queries, postgres_configuration, update_table
from readData import editedAnnotatedData
from prepare_golden_standard import rebuild_conversations
from da_recognition import baseline
from da_recognition import supervised_learning, annotationRule
from evaluation import da_evaluation
# from mongoDB import mongoDB_configuration, queries
# from prepare_golden_standard.annotated_tweets_final import editing_annotated_tweets
# from prepare_golden_standard import insert_to_postgres
#

# database = 'DARecognition'
# #
# # # make all connection to db here
# collectionRawTwitterData = mongoDB_configuration.get_collection(database, 'rawTwitterData')
# collectionAnnotatedData = mongoDB_configuration.get_collection(database, 'annotatedTwitterData')
# rawTwitterConversation_path = 'DATA/twitterConversation'
# annotatedData_path = 'DATA/annotationed/webanno-projectexport/annotation'
# annotatedDataRAW_path = 'DATA/annotated_tweets_raw.txt'
#
# if mongoDB_configuration.check_tweets_amount(collectionRawTwitterData) == 0:
#     #  Import raw twitter_objects conversation in DB
#     rawTwitterData.import_raw_twitter_data(rawTwitterConversation_path, collectionRawTwitterData)
#
# else:
#     print 'Collection ' + collectionRawTwitterData.name + ' is already existed'
#
# amountOfRawTweets = queries.check_tweets_amount(collectionRawTwitterData)
# print 'There are ',  amountOfRawTweets, ' raw tweets in DB.'
#
#
# if mongoDB_configuration.check_tweets_amount(collectionAnnotatedData) == 0:
#     rawAnnotatedData_read.read_annotated_docs(annotatedData_path, collectionAnnotatedData)
# else:
#     print 'Collection ' + collectionAnnotatedData.name + ' is already existed'
# amountOdAnnotatedTweets = mongoDB_configuration.check_tweets_amount(collectionAnnotatedData)
#
# editing_annotated_tweets(collectionAnnotatedData)


############# Postgres ###############

# import 10GB tweets move to top, so only once we read the txt
# rawTwitterData.import_to_postgres(rawTwitterConversation_path)

# DA Taxonomy
# insert_to_table.insert_dialogue_act_names()
# Insert annotated tweets: tweet id, text, replays, lang
# insert_to_postgres.insert_annotated_tweets_postgres(annotatedData_path)

# rawAnnotatedData_read.concatenate_done_tweets()
# rebuild_conversations.insert_annotated_tweets(tweets_id)

# postgres_queries.find_not_german_tweets()

###################### NEW ################################
print 'start'
connection, cursor = postgres_configuration.make_connection()
if postgres_configuration.check_if_exists_tweet_table() is False:
    # create db
    postgres_configuration.create_db()
    print 'Database is created'

    # insert dit++
    insert_to_table.insert_dialogue_act_names_full(connection, cursor)
    insert_to_table.insert_dialogue_act_names_reduced(connection, cursor)
    insert_to_table.insert_dialogue_act_names_minimal(connection, cursor)
    print 'DIT++ taxonomy is inserted'

    # insert golden standard to db
    print 'Start inserting golden standard'
    list_of_tweets = editedAnnotatedData.import_golden_standard_postgres('goldenStandard.xlsx')
    #update language info
    print 'Update language information'
    postgres_queries.update_lang_info('postgres/update_lang_info.sql')
    # check language, delete non german tweets and their children
    print 'Delete non-german tweets and their children'
    german_tweet_id = rebuild_conversations.delete_non_german_tweets()
    print 'Insert to annotated token table and segmentation table'
    insert_to_table.insert_annotated_table(list_of_tweets, german_tweet_id)
    print 'Insert to segmentation utterance table'
    insert_to_table.make_segmentation_utterance_table()
    print 'Update tweet position in conversation'
    update_table.update_position_conversation_column()
    print 'Golden standard is inserted'

else:
    print 'Golden standard is already there'




# predictions
taxonomy_list = ['full', 'reduced', 'minimal']
# for taxonomy in taxonomy_list:
#     print taxonomy
#     da_unigrams= postgres_queries.find_da_unigrams(taxonomy, cursor)
#     for a in da_unigrams:
#         print str(a[0]) + '\t' + a[1]

print 'Baseline'
# baseline.assign_inform_da()
#
# print 'Baseline evaluation'
# da_evaluation.evaluation_taxonomy('full')
# da_evaluation.evaluation_taxonomy('reduced')
# da_evaluation.evaluation_taxonomy('min')
print 'Supervised learning: HMM'
for taxonomy in taxonomy_list:
    print taxonomy + ' Taxonomy'
    supervised_learning.hmm_algorithm(taxonomy, cursor, connection)
    annotationRule.assign_zero_da(taxonomy, cursor, connection)
    if taxonomy == 'full':
        annotationRule.assign_choice_q_da(taxonomy, cursor, connection)
    if taxonomy != 'full':
        annotationRule.assign_social_da(taxonomy, cursor, connection)
        annotationRule.assign_it_is_da(taxonomy, cursor, connection)
    da_evaluation.evaluation_taxonomy_da(taxonomy, cursor)
    da_evaluation.overall_evaluation(taxonomy, cursor)
# print 'Reduced taxonomy'
# supervised_learning.hmm_algorithm('reduced', cursor, connection)
# annotationRule.assign_zero_da('reduced', cursor, connection)
# annotationRule.assign_social_da('reduced', cursor, connection)
# annotationRule.assign_it_is_da('reduced', cursor, connection)
# da_evaluation.evaluation_taxonomy_da('reduced', cursor)
# da_evaluation.overall_evaluation('reduced', cursor)
# print 'Minimal Taxonomy'
# supervised_learning.hmm_algorithm('minimal', cursor, connection)
# annotationRule.assign_zero_da('minimal', cursor, connection)
# annotationRule.assign_social_da('minimal', cursor, connection)
# annotationRule.assign_it_is_da('minimal', cursor, connection)
# da_evaluation.evaluation_taxonomy_da('minimal', cursor)
# da_evaluation.overall_evaluation('minimal', cursor)

postgres_configuration.close_connection(connection)
