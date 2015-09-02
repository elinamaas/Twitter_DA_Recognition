__author__ = 'snownettle'
from tenFoldCrossValidation import split10
from learning import hmm, svm


def hmm_algorithm(taxonomy, cursor, connection):
    datasets = split10.fold_splitter(cursor)
    for i in range(0, 10, 1):
        train_set, test_set = split10.train_test_sets(datasets, i)
        hmm.calculate_hmm(train_set, test_set, taxonomy, cursor, connection)


def svm(taxonomy, cursor, connection):
    datasets = split10.fold_splitter(cursor)
    for i in range(0, 10, 1):
        train_set, test_set = split10.train_test_sets(datasets, i)
        svm.run_svm(train_set, test_set, taxonomy, cursor, connection)


# hmm_utterance_length()

