__author__ = 'snownettle'
from postgres import postgres_queries
import re

def find_tokenizer_error():
    tokens = postgres_queries.find_all_tokens()
    for token in tokens:
        if check_token(token[1]) is not None:
            print token[0], ' : ', token[1]


def check_token(token):
    return re.search(r'\.[a-z]', token)
    # return re.match('[a-z]+[^a-zA-Z0-9_][a-z]', token)

find_tokenizer_error()

# print re.search(r'\.[a-z]', 'abc.de')
# print m.start()

# print check_token('uuu')