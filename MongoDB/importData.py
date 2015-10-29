__author__ = 'snownettle'
import re
import json
from general.read_file import iterparse
import mongoDBQueries as queries
from da_taxonomy import matching_schema
from postgres import postgres_queries, postgres_configuration
import copy


def import_record(data, collection):
    #import only one json record
    collection.insert(data)


def import_from_file(collection, data):
    # import form json file
    for tweet in iterparse(data):
        collection.insert(tweet)
