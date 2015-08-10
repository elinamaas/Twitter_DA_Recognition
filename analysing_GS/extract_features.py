import re

__author__ = 'snownettle'


def is_link(utterance):
    if 'http:' in utterance:
        return 1
    else:
        return 0


def is_username(token):
    if '@' in token:
        return 1
    else:
        return 0


def has_numbers(input_string):
    return bool(re.search(r'\d', input_string))


def has_question_mark(utterance):
    return '?' in utterance


def has_explanation_mark(utterance):
    return '!' in utterance


def has_hashtag(utterance):
    return '#' in utterance