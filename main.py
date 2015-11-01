__author__ = 'snownettle'

from postgres import postgres_configuration, postgres_create_database
from learning import words2vec, supervised_learning
from tenFoldCrossValidation.split10 import fold_splitter
from statistics import annotatedData_stat
from prepare_gold_standard.extract_gs import analyze_original_data


print 'start'
words, embeddings, word_id, id_word = words2vec.read_pkl('DATA/polyglot-de.pkl')
connection, cursor = postgres_configuration.make_connection()
gold_standard_file = 'DATA/goldStandard.xlsx'

# comment it if you don't want to analyze original data
analyze_original_data(connection, cursor)

postgres_create_database.create_db_insert(connection, cursor, gold_standard_file)
annotatedData_stat.gold_standard_stats(cursor)

taxonomy_list = ['full', 'reduced', 'minimal']

# predictions
data_set = fold_splitter(cursor, embeddings, word_id)
supervised_learning.recognize_da(taxonomy_list, cursor, connection, data_set)

postgres_configuration.close_connection(connection)
