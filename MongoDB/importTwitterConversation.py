import conDB
import re
import json


def importData(dbName, collectionName, data):
    collection = conDB.getCollection(dbName, collectionName)
    for tweet in iterparse(data):
        collection.insert(tweet)


nonspace = re.compile(r'\S')


def iterparse(j):
    decoder = json.JSONDecoder()
    pos = 0
    while True:
        matched = nonspace.search(j, pos)
        if not matched:
            break
        pos = matched.start()
        decoded, pos = decoder.raw_decode(j, pos)
        yield decoded

# with open("test.txt") as f:
#     content = f.read()
# for decoded in iterparse(content):
#     print(decoded)


#importData("testDataTweets", content)
