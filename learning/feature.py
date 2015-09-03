from analysing_GS import emoticons, question_words
from pattern.de import parse, split, INFINITIVE
import re

__author__ = 'snownettle'

class Feature:
    """
        In this Class is described features that are int the utterance
        Features:
        1. Length : length of the utterance
        2. Root user: Is the utterancce belongs to the root user or not :type: root_user: boolean
        3. Position of the utterance in tweet. Is it first: :type: pos: boolean


    """
        #
    def __init__(self, utterance, start_offset, end_offset, root_username, current_username, pos, tokens):
        self.feature = dict()
        self.extract_features(utterance, start_offset, end_offset, root_username, current_username, pos, tokens)

    def extract_features(self, utterance, start_offset, end_offset, root_username, current_username, pos, tokens):
        utterance = utterance.lower()
        length = self.utterance_length(start_offset, end_offset)
        root_user = self.has_root_username(root_username, current_username)
        link = self.has_link(utterance)
        question_mark = self.has_question_mark(utterance)
        exclamation_mark = self.has_explanation_mark(utterance)
        hashtag = self.has_hashtag(utterance)
        emoticons = self.has_emoticons(utterance)
        question_words = self.has_question_word(utterance)
        first_verb = self.is_first_verb(utterance)
        lang_features = self.extract_lang_features(tokens, utterance)
        self.feature = {'length' : length, 'root_user': root_user, 'pos': pos,
                        'link': link, 'question_mark': question_mark, 'exclamation_mark': exclamation_mark,
                        'hashtag': hashtag, 'emoticons': emoticons, 'question_words': question_words,
                        'first_verb': first_verb, 'language_features': lang_features}

    def compare(self, existing_feature):
        return self.feature == existing_feature.feature

    def add_new_feature(self, feature_list):
        do_not_add = False
        for feature in feature_list:
            if self.compare(feature):
                do_not_add = True
        if do_not_add is False:
            feature_list.append(self)

    def find_index_in_feature_list(self, feature_list):
        for i in range(0, len(feature_list), 1):
            if self.compare(feature_list[i]):
                return i

    def contains_in_list(self, feature_list):
        for i in range(0, len(feature_list), 1):
            feature = feature_list[i]
            if self.compare(feature):
                return i
        return None

    def extract_lang_features(self, tokens, utterance):
        language_features = [False]*len(tokens)
        if '@' in utterance:
            utterance = self.delete_username(utterance)
        if self.has_link(utterance):
            utterance = self.delete_link(utterance)
        utterance = self.delete_non_alphabetic_symbols(utterance)
        sentences = parse(utterance, relations=True, lemmata=True).split()
        # tokens = utterance.split(' ')
        for sentence in sentences:
            for token in sentence:
                if token[0] in tokens:
                    i = tokens.index(token[0])
                    language_features[i] = True
        return language_features

    @staticmethod
    def has_link(utterance):
        if 'http:' in utterance:
            return True
        else:
            return False

    @staticmethod
    def delete_link(utterance):
        new_utterance = ''
        tokens = utterance.split(' ')
        for token in tokens:
            if 'http:' not in token:
                new_utterance += token + ' '
        return new_utterance[:-1]

    @staticmethod
    def delete_username(utterance):
        new_utterance = ''
        tokens = utterance.split(' ')
        for token in tokens:
            if '@' not in token:
                new_utterance += token + ' '
        return new_utterance[:-1]
    @staticmethod
    def has_numbers(input_string):
        return bool(re.search(r'\d', input_string))

    @staticmethod
    def delete_non_alphabetic_symbols(token):
        if Feature.has_numbers(token):
            token = re.sub('\d', '', token)
        chars_to_remove = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '[', ']', '{', '}', ';', ':', ',', '.',
                           '/', '<', '>', '?', '`', '\\', '~', '-', '=', '_', '+''|', u'\xe2', u'\x80', u'\xa6']
        rx = '[' + re.escape(''.join(chars_to_remove)) + ']'
        return re.sub(rx, ' ', token).lower()

    @staticmethod
    def utterance_length(start_offset, end_offset):
        return end_offset - start_offset + 1

    @staticmethod
    def has_root_username(root_username, current_username):
        return root_username == current_username

    @staticmethod
    def has_link(utterance):
        if 'http:' in utterance:
            return True
        else:
            return False

    @staticmethod
    def has_question_mark(utterance):
        return '?' in utterance

    @staticmethod
    def has_explanation_mark(utterance):
        return '!' in utterance

    @staticmethod
    def has_hashtag(utterance):
        return '#' in utterance

    @staticmethod
    def has_emoticons(utterance):
        emoticons_list = emoticons.emoticons_lib()
        for emoticon in emoticons_list:
            if emoticon in utterance and 'http:' not in utterance:
                return True
        return False

    @staticmethod
    def has_question_word(utterance):
        utterance = str(utterance)
        question_words_list = question_words.german_question_words()
        utterance = Feature.delete_conjuction(utterance)
        for qw in question_words_list:
            utterance = Feature.delete_conjuction(utterance)
            # delete first conjuction: und, aber, oder
            if utterance.startswith(qw):
                return True
        return False

    @staticmethod
    def is_first_verb(utterance):
        if '@' in utterance:
            utterance = Feature.delete_username(utterance)
        utterance = Feature.delete_conjuction(utterance)
        sentences = parse(utterance, relations=True, lemmata=True).split()
        pos_list = ['VB', 'VBP', 'VBZ', 'VBG', 'VBD', 'BN']
        if len(sentences) != 0:
            if len(sentences[0]) != 0:
                pos = sentences[0][0][1]
                if pos in pos_list:
                    return True
        return False

    @staticmethod
    def delete_username(utterance):
        new_utterance = ''
        tokens = utterance.split(' ')
        for token in tokens:
            if '@' not in token:
                new_utterance += token + ' '
        return new_utterance[:-1]

    @staticmethod
    def delete_conjuction(utterance):
        conjuction_list = ['und', 'oder', 'aber']
        utterance = utterance.lower()
        tokens = utterance.split(' ')
        if tokens[0] in conjuction_list:
            return utterance.split(' ', 1)[1]
        else:
            return utterance










