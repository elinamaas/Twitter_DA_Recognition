__author__ = 'snownettle'
from general.read_file import iterparse


def import_record(data, collection):
    #import only one json record
    collection.insert(data)


def import_from_file(collection, data):
    # import form json file
    for tweet in iterparse(data):
        collection.insert(tweet)
