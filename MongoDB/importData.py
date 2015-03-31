__author__ = 'snownettle'
import re
import json
from general.read_file import iterparse


def import_record(data, collection):
    #import only one json record
    collection.insert(data)


def import_from_file(collection, data):
    # import form json file
    for tweet in iterparse(data):
        collection.insert(tweet)


# def iterparse(j):
#     decoder = json.JSONDecoder()
#     pos = 0
#     while True:
#         matched = re.compile(r'\S').search(j, pos)
#         if not matched:
#             break
#         pos = matched.start()
#         decoded, pos = decoder.raw_decode(j, pos)
#         yield decoded




# def test()
#     return re.compile(r'\S')
#
# nonspace = re.compile(r'\S')