# import mongoDB_configuration
# import re
# import json
#
#
# def importData(collection, data):
#     for tweet in iterparse(data):
#         collection.insert(tweet)
#
#
# nonspace = re.compile(r'\S')
#
#
# def iterparse(j):
#     decoder = json.JSONDecoder()
#     pos = 0
#     while True:
#         matched = nonspace.search(j, pos)
#         if not matched:
#             break
#         pos = matched.start()
#         decoded, pos = decoder.raw_decode(j, pos)
#         yield decoded
#
