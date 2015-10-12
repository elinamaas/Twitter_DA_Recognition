__author__ = 'snownettle'

from postgres import postgres_configuration, postgres_create_database
from evaluation.da_evaluation import evaluation_taxonomy_da
from da_recognition import supervised_learning
from learning import words2vec
from tenFoldCrossValidation.split10 import fold_splitter


print 'start'
words, embeddings, word_id, id_word = words2vec.read_pkl('DATA/polyglot-de.pkl')
connection, cursor = postgres_configuration.make_connection()
gold_standard_file = 'goldStandard.xlsx'
postgres_create_database.create_db_insert(connection, cursor, gold_standard_file)

taxonomy_list = ['full', 'reduced', 'minimal']

######### BASELINE ##########
print 'Baseline evaluation'
for taxonomy in taxonomy_list:

    evaluation_taxonomy_da(taxonomy, cursor)
# evaluate baseline
# baseline(taxonomy_list, cursor, connection)

# predictions


data_set = fold_splitter(cursor, embeddings, word_id)
supervised_learning.recognize_da(taxonomy_list, cursor, connection, data_set)

postgres_configuration.close_connection(connection)
