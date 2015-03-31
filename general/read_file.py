__author__ = 'snownettle'
import os.path
import json
import re


def readTXT(file_name):
    if os.path.exists(file_name) is True:
        with open(file_name) as f:
            content = f.read()
            return content
    else:
        print 'There is no such file'
        return None


def iterparse(j):
    decoder = json.JSONDecoder()
    pos = 0
    while True:
        matched = re.compile(r'\S').search(j, pos)
        if not matched:
            break
        pos = matched.start()
        decoded, pos = decoder.raw_decode(j, pos)
        yield decoded