__author__ = 'snownettle'

import pickle
import numpy
from operator import itemgetter
from itertools import izip, islice
import re

# Noramlize digits by replacing them with #
DIGITS = re.compile("[0-9]", re.UNICODE)


def read_pkl(file):
    # file = '../DATA/polyglot-de.pkl'
    words, embeddings = pickle.load(open(file, 'rb'))
    # print len(words)
    # print ("Emebddings shape is {}".format(embeddings.shape))
    word_id = {w:i for (i, w) in enumerate(words)}
    id_word = dict(enumerate(words))
    # find_word_embeddings('dazu',embeddings, word_id, id_word)
    return words, embeddings, word_id, id_word


def case_normalizer(word, dictionary):
    """ In case the word is not available in the vocabulary,
     we can try multiple case normalizing procedure.
     We consider the best substitute to be the one with the lowest index,
     which is equivalent to the most frequent alternative."""
    w = word
    lower = (dictionary.get(w.lower(), 1e12), w.lower())
    upper = (dictionary.get(w.upper(), 1e12), w.upper())
    title = (dictionary.get(w.title(), 1e12), w.title())
    results = [lower, upper, title]
    results.sort()
    index, w = results[0]
    if index != 1e12:
        return w
    return word


def normalize(word, word_id):
    """ Find the closest alternative in case the word is OOV."""
    if not word in word_id:
        word = DIGITS.sub("#", word)
    if not word in word_id:
        word = case_normalizer(word, word_id)
    if not word in word_id:
        return None
    return word


# def l2_nearest(embeddings, word_index, k):
#     """Sorts words according to their Euclidean distance.
#        To use cosine distance, embeddings has to be normalized so that their l2 norm is 1."""
#
#     e = embeddings[word_index]
#     distances = (((embeddings - e) ** 2).sum(axis=1) ** 0.5)
#     sorted_distances = sorted(enumerate(distances), key=itemgetter(1))
#     return zip(*sorted_distances[:k])


def find_word_embeddings(word, embeddings,  word_id):
    word = normalize(word, word_id)
    # if word in language_features:
        # index_emb = language_features.index(word)
    if not word:
        # print("OOV word")
        return

    word_index = word_id[word]
    e = embeddings[word_index]
    return e

    # indices, distances = l2_nearest(embeddings, word_index, k)
    # neighbors = [id_word[idx] for idx in indices]
    # for i, (word, distance) in enumerate(izip(neighbors, distances)):
    #   print i, '\t', word, '\t\t', distance


# read_pkl()
