__author__ = 'snownettle'

import postgres.postgres_create_database
from postgres import postgres_configuration, update_table
from da_recognition import baseline
from da_recognition import supervised_learning
from evaluation import da_evaluation
from learning import words2vec
from tenFoldCrossValidation.split10 import fold_splitter


print 'start'
words, embeddings, word_id, id_word = words2vec.read_pkl('DATA/polyglot-de.pkl')

connection, cursor = postgres_configuration.make_connection()
gold_standard_file = 'goldStandard.xlsx'
postgres.postgres_create_database.create_db_insert(connection, cursor, gold_standard_file)

# predictions
taxonomy_list = ['full', 'reduced', 'minimal']

######### BASELINE ##########

# print 'Inserting Baseline'
# if postgres_configuration.check_if_exists_prediction_table(cursor) is False:
#     baseline.assign_inform_da(cursor)
# else:
#     update_table.update_segmentation_prediction_table_baseline(cursor, connection)
# for taxonomy in taxonomy_list:
#     print taxonomy + ' Taxonomy'
#     da_evaluation.evaluation_taxonomy_da(taxonomy, cursor)
#     da_evaluation.inter_annotation_agreement(taxonomy, cursor)
#     da_evaluation.confusion_matrix(taxonomy, cursor)


data_set = fold_splitter(cursor, embeddings, word_id)
supervised_learning.recognize_da(taxonomy_list, cursor, connection, data_set)

postgres_configuration.close_connection(connection)
