__author__ = 'snownettle'

from sklearn.datasets import make_multilabel_classification
from sklearn.preprocessing import MultiLabelBinarizer
from postgres import postgres_configuration, postgres_queries
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from bunch import Bunch
import numpy as np

def run_svm(train_set, test_set, taxonomy, cursor, connection):
    tweets_text_da_inform = postgres_queries.find_all_utterance_by_da('Segments_utterance', 'IT_IP_Inform', taxonomy, cursor)
    categories = ['alt.atheism', 'soc.religion.christian','comp.graphics', 'sci.med']
    twenty_train = fetch_20newsgroups(subset='train',categories=categories, shuffle=True, random_state=42)
    # X, Y = make_multilabel_classification(n_samples=90, random_state=5, return_indicator=True)

    # print Y
    # [[2, 3, 4], [2], [0, 1, 3], [0, 1, 2, 3, 4], [0, 1, 2]]
    # print MultiLabelBinarizer().fit_transform(Y)
    # array([[0, 0, 1, 1, 1],
    #        [0, 0, 1, 0, 0],
    #        [1, 1, 0, 1, 0],
    #        [1, 1, 1, 1, 1],
    #        [1, 1, 1, 0, 0]])
    bag_of_words = dict() # word: id
    # print twenty_train
    data = Bunch()
    data.data = list()
    data.target = np.ndarray
    for tweet in tweets_text_da_inform:
        data.data.append(tweet[3])

    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(data) # list of unicode
    print X_train_counts.shape
    tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
    X_train_tf = tf_transformer.transform(X_train_counts)
    print X_train_tf.shape
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    print X_train_tfidf.shape
    clf = MultinomialNB().fit(X_train_tfidf, twenty_train.target)



# svm_test()