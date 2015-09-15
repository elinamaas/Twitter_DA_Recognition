import postgres.postgres_create_database

__author__ = 'snownettle'
from postgres import insert_to_table, postgres_queries, postgres_configuration, update_table
from readData import editedAnnotatedData
from prepare_gold_standard import rebuild_conversations
from da_recognition import baseline
from da_recognition import supervised_learning, annotationRule
from evaluation import da_evaluation
from learning import words2vec
# from mongoDB import mongoDB_configuration, queries
# from prepare_gold_standard.annotated_tweets_final import editing_annotated_tweets
# from prepare_gold_standard import insert_to_postgres
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
# words, embeddings, word_id, id_word = words2vec.read_pkl('DATA/polyglot-de.pkl')
connection, cursor = postgres_configuration.make_connection()
gold_standard_file = 'goldStandard.xlsx'
postgres.postgres_create_database.create_db_insert(connection, cursor, gold_standard_file)

# predictions
taxonomy_list = ['full', 'reduced', 'minimal']
# supervised_learning.hmm_algorithm('minimal', cursor, connection)
# da_evaluation.evaluation_taxonomy_da('minimal', cursor)
print 'Inserting Baseline'
if postgres_configuration.check_if_exists_prediction_table(cursor) is False:
    baseline.assign_inform_da(cursor)
else:
    update_table.update_segmentation_prediction_table_baseline(cursor, connection)
for taxonomy in taxonomy_list:
    print taxonomy + ' Taxonomy'
    da_evaluation.evaluation_taxonomy_da(taxonomy, cursor)
    da_evaluation.inter_annotation_agreement(taxonomy, cursor)
    da_evaluation.confusion_matrix(taxonomy, cursor)

#
# print 'Baseline evaluation'
# da_evaluation.evaluation_taxonomy('full')
# da_evaluation.evaluation_taxonomy('reduced')
# da_evaluation.evaluation_taxonomy('min')
# da_evaluation.inter_annotation_agreement('full', cursor)
# da_evaluation.inter_annotation_agreement('reduced', cursor)
# da_evaluation.inter_annotation_agreement('minimal', cursor)
# da_evaluation.confusion_matrix('minimal', cursor)

# supervised_learning.conditional_random_fields('minimal', cursor, connection)
# da_evaluation.evaluation_taxonomy_da('minimal', cursor)
# da_evaluation.inter_annotation_agreement('full', cursor)
# da_evaluation.confusion_matrix('full', cursor)

print 'Supervised learning: HMM'
for taxonomy in taxonomy_list:
    print taxonomy + ' Taxonomy'
    supervised_learning.hmm_algorithm(taxonomy, cursor, connection)
    da_evaluation.evaluation_taxonomy_da(taxonomy, cursor)
    da_evaluation.inter_annotation_agreement(taxonomy, cursor)
    da_evaluation.confusion_matrix(taxonomy, cursor)
    # da_evaluation.overall_evaluation(taxonomy, cursor)

print '#############################################################'
print 'With Rules'
for taxonomy in taxonomy_list:
    print taxonomy + ' Taxonomy'
    annotationRule.assign_zero_da(taxonomy, cursor, connection)
    if taxonomy == 'full':
        annotationRule.assign_choice_q_da(taxonomy, cursor, connection)
    if taxonomy != 'full':
        annotationRule.assign_social_da(taxonomy, cursor, connection)
        annotationRule.assign_it_is_da(taxonomy, cursor, connection)
    da_evaluation.evaluation_taxonomy_da(taxonomy, cursor)
    da_evaluation.inter_annotation_agreement(taxonomy, cursor)
    da_evaluation.confusion_matrix(taxonomy, cursor)


print 'Supervised learning: CRF'
for taxonomy in taxonomy_list:
    print taxonomy + ' Taxonomy'
    supervised_learning.conditional_random_fields(taxonomy, cursor, connection)
    da_evaluation.evaluation_taxonomy_da(taxonomy, cursor)
    da_evaluation.inter_annotation_agreement(taxonomy, cursor)
    da_evaluation.confusion_matrix(taxonomy, cursor)
    # da_evaluation.overall_evaluation(taxonomy, cursor)

print '#############################################################'
print 'With Rules'
for taxonomy in taxonomy_list:
    print taxonomy + ' Taxonomy'
    annotationRule.assign_zero_da(taxonomy, cursor, connection)
    if taxonomy == 'full':
        annotationRule.assign_choice_q_da(taxonomy, cursor, connection)
    if taxonomy != 'full':
        annotationRule.assign_social_da(taxonomy, cursor, connection)
        annotationRule.assign_it_is_da(taxonomy, cursor, connection)
    da_evaluation.evaluation_taxonomy_da(taxonomy, cursor)
    da_evaluation.inter_annotation_agreement(taxonomy, cursor)
    da_evaluation.confusion_matrix(taxonomy, cursor)

postgres_configuration.close_connection(connection)
