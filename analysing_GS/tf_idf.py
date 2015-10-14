__author__ = 'snownettle'
import math, operator
from collections import defaultdict


def calculate_tf_idf(train_set):
    tf_full = defaultdict(dict)
    idf_full = defaultdict(set)
    tf_reduced = defaultdict(dict)
    idf_reduced = defaultdict(set)
    tf_min = defaultdict(dict)
    idf_min = defaultdict(set)
    das_full = set()
    das_reduced = set()
    das_min = set()
    for conversation in train_set:
        for branch in conversation:
            for segment in branch.branch:
                add_token_da_frequency(tf_full, idf_full, tf_reduced, idf_reduced, tf_min, idf_min, segment,
                                       das_full, das_reduced, das_min)
    tf_idf_full = tfidf(tf_full, idf_full, das_full)
    tf_idf_reduced = tfidf(tf_reduced, idf_reduced, das_full)
    tf_idf_min = tfidf(tf_min, idf_min, das_full)
    tokens_full = choose_word_features(tf_idf_full)
    tokens_reduced = choose_word_features(tf_idf_reduced)
    tokens__min = choose_word_features(tf_idf_min)
    return tokens_full, tokens_reduced, tokens__min


def word_appearance_tfidf (train_set, tokens_full, tokens_reduced, tokens__min):
    for conversation in train_set:
        for branch in conversation:
            for segment in branch.branch:
                segment.features.add_language_features(tokens_full, tokens_reduced, tokens__min)


def add_token_da_frequency(tf_full, idf_full, tf_reduced, idf_reduced, tf_min, idf_min, segment, das_full, das_reduced, das_min):
    token_appearance = segment.features.token_appearance
    da_full = segment.da_id_full
    da_reduced = segment.da_id_reduced
    da_min = segment.da_id_minimal
    das_full.add(da_full)
    das_reduced.add(da_reduced)
    das_min.add(da_min)

    for token, freq in token_appearance.iteritems():
        if token in tf_full:
            if da_full in tf_full[token]:
                idf_full[token].add(da_full)
                tf_full[token][da_full] += freq
            else:
                idf_full[token].add(da_full)
                tf_full[token][da_full] = freq
            if da_reduced in tf_reduced[token]:
                idf_reduced[token].add(da_reduced)
                tf_reduced[token][da_reduced] += freq
            else:
                idf_reduced[token].add(da_reduced)
                tf_reduced[token][da_reduced] = freq
            if da_min in tf_min[token]:
                idf_min[token].add(da_min)
                tf_min[token][da_min] += freq
            else:
                idf_min[token].add(da_min)
                tf_min[token][da_min] = freq
        else:
                idf_full[token].add(da_full)
                tf_full[token][da_full] = freq
                idf_reduced[token].add(da_reduced)
                tf_reduced[token][da_reduced] = freq
                idf_min[token].add(da_min)
                tf_min[token][da_min] = freq


def choose_word_features(tfidf):
    words_set = set()
    for da, tfidf_value in tfidf.iteritems():
        sorted_x = sorted(tfidf_value.items(), key=operator.itemgetter(1))
        sorted_x.reverse()
        i = 0
        for tf in sorted_x:
            if i == 100:
                break
            else:
                words_set.add(tf[0])
            i += 1
    words_list = list(words_set)
    return words_list


def tfidf(tf_features, idf_features, das_list):
    tfidf_dict = defaultdict(dict)
    for da in das_list:
        for token, da_set in idf_features.iteritems():
            nt = len(da_set)
            if da in tf_features[token]:
                freq = tf_features[token][da]
            else:
                freq = 0
            tfidf_dict[da][token] = freq * math.log10(len(das_list)/float(nt))
    return tfidf_dict
