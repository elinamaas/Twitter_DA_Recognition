__author__ = 'snownettle'
import re
import json
from general.read_file import iterparse
import mongoDBQueries as queries
from da_recognition import matching_schema
from postgres import postgres_queries, postgres_configuration
import copy


def import_record(data, collection):
    #import only one json record
    collection.insert(data)


def import_from_file(collection, data):
    # import form json file
    for tweet in iterparse(data):
        collection.insert(tweet)


# def import_reduced_annotation_collection(collectionFull, collectionReduced):
#     full_ontology = postgres_configuration.fullOntologyTable
#     records_full_annotation = queries.find_all(collectionFull)
#     not_relevant = ['id', 'conversation_id', 'text_id', 'text', 'tweet_id', '_id']
#     for record in records_full_annotation:
#         new_record = copy.deepcopy(record)
#         for key, value in record.iteritems():
#             if key not in not_relevant:
#                 da_full = record[key][1]
#                 if da_full != '0':
#                     if '|' in da_full:
#                         das_full = da_full.split('|')
#                         das_reduced = ''
#                         for da in das_full:
#                             label = da.split('-')[0]
#                             da_full_no_label = da.split('-')[1]
#                             da_full_id = postgres_queries.find_da_by_name(da_full_no_label, full_ontology)
#                             da_reduced = matching_schema.match_reduced(da_full_id)
#                             da_reduced_label = label + '-' + da_reduced
#                             das_reduced += da_reduced_label + '|'
#                         das_reduced = das_reduced[:-1]
#                         del new_record[key][1]
#                         new_record[key].append(das_reduced)
#                     else:
#                         label = da_full.split('-')[0]
#                         da_full_no_label = da_full.split('-')[1]
#                         da_full_id = postgres_queries.find_da_by_name(da_full_no_label, full_ontology)
#                         da_reduced = matching_schema.match_reduced(da_full_id)
#                         da_reduced_label = label + '-' + da_reduced
#                         # new_record = dict(record)
#                         del new_record[key][1]
#                         new_record[key].append(da_reduced_label)
#         collectionReduced.insert(new_record)
