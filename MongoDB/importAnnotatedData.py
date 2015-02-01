__author__ = 'snownettle'
import json

def importAnnotatedData(data, collection):
    # tweet = json.loads(data)
    # print type(tweet)
    collection.insert(data)
