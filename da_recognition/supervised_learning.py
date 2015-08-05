__author__ = 'snownettle'
from tenFoldCrossValidation import split10
from learning import hmm



def hmm_utterance_length(taxonomy):
    datasets = split10.fold_splitter()
    for i in range(0, 10, 1):
        train_set, test_set = split10.train_test_sets(datasets, i)
        hmm.calculate_hmm(train_set, test_set, taxonomy)

# hmm_utterance_length()

