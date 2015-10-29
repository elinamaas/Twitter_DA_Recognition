__author__ = 'snownettle'
from tenFoldCrossValidation import split10
from learning import hmm_multinomial, crf, hmm_gaussian
from evaluation import da_evaluation
from learning.tf_idf import calculate_tf_idf, word_appearance_tfidf


def train_test_seq(data_set, settings):

    train_test_list = list()
    for i in range(0, 10, 1):
        data_set_copy = data_set.copy()
        train_set, test_set = split10.train_test_sets(data_set_copy, i)
        tokens_full, tokens_reduced, tokens__min = calculate_tf_idf(train_set, settings)
        word_appearance_tfidf(train_set,tokens_full, tokens_reduced, tokens__min)
        word_appearance_tfidf(test_set,tokens_full, tokens_reduced, tokens__min)
        train_test_list.append([train_set, test_set])
    return train_test_list


def hmm_gaussian_algorithm(taxonomy, cursor, connection, train_test_list, settings):
    for train_test in train_test_list:
        train_set = train_test[0]
        test_set = train_test[1]
        hmm_gaussian.calculate_hmm_g(train_set, test_set, taxonomy, cursor, connection, settings)


def hmm_multinomial_algorithm(taxonomy, cursor, connection, train_test_list, settings):
    for train_test in train_test_list:
        train_set = train_test[0]
        test_set = train_test[1]
        hmm_multinomial.calculate_hmm_m(train_set, test_set, taxonomy, cursor, connection, settings)


def conditional_random_fields(taxonomy, cursor, connection, train_test_list, settings):
    for train_test in train_test_list:
        train_set = train_test[0]
        test_set = train_test[1]
        crf.run_crf(train_set, test_set, taxonomy, cursor, connection, settings)


def recognize_da(taxonomy_list, cursor, connection, data_set):
    settings = set_training_settings()
    train_test_set = train_test_seq(data_set, settings)
    result_values = set_result_values()

    # print 'Baseline'
    # for taxonomy in taxonomy_list:
    #     print taxonomy + ' Taxonomy'
    #     update_table.update_da_prediction_baseline(taxonomy, cursor, connection)
    #     da_evaluation.evaluation_taxonomy_da(taxonomy, cursor)
    #     da_evaluation.inter_annotation_agreement(taxonomy, cursor)

    #choose models 1-4
    if settings[1] == 1:
        print 'HMM Multinomial'
        for taxonomy in taxonomy_list:
            hmm_multinomial_algorithm(taxonomy, cursor, connection, train_test_set, settings)
            da_evaluation.evaluation_taxonomy_da(taxonomy, cursor, settings, result_values, 'MHMM')
            if settings[3] == 1:
                print 'Confusion matrix for ' + taxonomy
                da_evaluation.confusion_matrix(taxonomy, cursor)

    elif settings[1] == 2:
        print 'HMM Gaussian'
        for taxonomy in taxonomy_list:
            hmm_gaussian_algorithm(taxonomy, cursor, connection, train_test_set, settings)
            da_evaluation.evaluation_taxonomy_da(taxonomy, cursor, settings, result_values, 'GHMM')
            if settings[3] == 1:
                print 'Confusion matrix for ' + taxonomy
                da_evaluation.confusion_matrix(taxonomy, cursor)
    elif settings[2] == 3:
        print 'CRF'
        for taxonomy in taxonomy_list:
            conditional_random_fields(taxonomy, cursor, connection, train_test_set, settings)
            da_evaluation.evaluation_taxonomy_da(taxonomy, cursor, settings, result_values, 'CRF')
            if settings[3] == 1:
                print 'Confusion matrix for ' + taxonomy
                da_evaluation.confusion_matrix(taxonomy, cursor)
    else:
        for taxonomy in taxonomy_list:
            print 'HMM Multinomial'
            hmm_multinomial_algorithm(taxonomy, cursor, connection, train_test_set, settings)
            da_evaluation.evaluation_taxonomy_da(taxonomy, cursor, settings, result_values, 'MHMM')
            if settings[3] == 1:
                print 'Confusion matrix for ' + taxonomy
                da_evaluation.confusion_matrix(taxonomy, cursor)

            print 'HMM Gaussian'
            hmm_gaussian_algorithm(taxonomy, cursor, connection, train_test_set, settings)
            da_evaluation.evaluation_taxonomy_da(taxonomy, cursor, settings, result_values, 'GHMM')
            if settings[3] == 1:
                print 'Confusion matrix for ' + taxonomy
                da_evaluation.confusion_matrix(taxonomy, cursor)

            print 'CRF'
            conditional_random_fields(taxonomy, cursor, connection, train_test_set, settings)
            da_evaluation.evaluation_taxonomy_da(taxonomy, cursor, settings, result_values, 'CRF')
            if settings[3] == 1:
                print 'Confusion matrix for ' + taxonomy
                da_evaluation.confusion_matrix(taxonomy, cursor)

    da_evaluation.print_eva_table_small(result_values)


def set_training_settings():
    print 'Which model do you want to test: ' \
          '\n 1 HMM with multinomial distidution ' \
          '\n 2 HMM with Gaussan distribution ' \
          '\n 3 Conditional Random field ' \
          '\n 4 All'
    models = input('Model: ')
    print 'Choose how many significant words from each DA should be included.'
    tf_idf_top = input('Press number from 1 to 100: ')
    print 'Please, choose feature sets grom the list: \n 1. User-defined ' \
          '\n 2. User-defined + language model top ' + str(tf_idf_top)+ \
          '\n 3. User-defined + words embeddings \n 4. User-defined all'
    feature_set = input('Press number from 1 to 4:')
    print 'Do you want to see all output?'
    output = input('yes(1)/no(0): ')
    print 'Do you want to observe confusion matrix: '
    confusion_matrix = input('yes(1)/no(0): ')
    settings = [tf_idf_top, models, feature_set, confusion_matrix, output]
    return settings


def set_result_values():
    results = {'full':
                   {'MHMM': {'UD':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + top':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + WE':{'f1': 0, 'acc.': 0, 'pi':0},
                             'ALL':{'f1': 0, 'acc.': 0, 'pi':0}},
                    'GHMM': {'UD':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + top':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + WE':{'f1': 0, 'acc.': 0, 'pi':0},
                             'ALL':{'f1': 0, 'acc.': 0, 'pi':0}},
                    'CRF':  {'UD':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + top':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + WE':{'f1': 0, 'acc.': 0, 'pi':0},
                             'ALL':{'f1': 0, 'acc.': 0, 'pi':0}}
                    },
               'reduced':
                   {'MHMM': {'UD':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + top':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + WE':{'f1': 0, 'acc.': 0, 'pi':0},
                             'ALL':{'f1': 0, 'acc.': 0, 'pi':0}},
                    'GHMM': {'UD':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + top':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + WE':{'f1': 0, 'acc.': 0, 'pi':0},
                             'ALL':{'f1': 0, 'acc.': 0, 'pi':0}},
                    'CRF':  {'UD':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + top':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + WE':{'f1': 0, 'acc.': 0, 'pi':0},
                             'ALL':{'f1': 0, 'acc.': 0, 'pi':0}}
                    },
               'minimal':
                   {'MHMM': {'UD':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + top':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + WE':{'f1': 0, 'acc.': 0, 'pi':0},
                             'ALL':{'f1': 0, 'acc.': 0, 'pi':0}},
                    'GHMM': {'UD':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + top':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + WE':{'f1': 0, 'acc.': 0, 'pi':0},
                             'ALL':{'f1': 0, 'acc.': 0, 'pi':0}},
                    'CRF':  {'UD':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + top':{'f1': 0, 'acc.': 0, 'pi':0},
                             'UD + WE':{'f1': 0, 'acc.': 0, 'pi':0},
                             'ALL':{'f1': 0, 'acc.': 0, 'pi':0}}
                    },
               }
    return results