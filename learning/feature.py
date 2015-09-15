from analysing_GS import emoticons, question_words
from pattern.de import parse, split
import re
from learning import words2vec
import numpy as np

__author__ = 'snownettle'


class Feature:
    """
        In this Class is described features that are int the utterance
        Features:
        1. Length : length of the utterance
        2. Root user: Is the utterancce belongs to the root user or not :type: root_user: boolean
        3. Position of the utterance in tweet. Is it first: :type: pos: int


    """
        #
    def __init__(self, utterance, start_offset, end_offset, root_username, current_username, pos, language_features):
        self.features = dict()
        # self.word2vec = list()
        self.extract_features(utterance, start_offset, end_offset, root_username, current_username, pos, language_features)

    def extract_features(self, utterance, start_offset, end_offset, root_username, current_username, pos, language_features):
        utterance = utterance.lower()
        length = self.utterance_length(start_offset, end_offset)
        root_user = self.has_root_username(root_username, current_username)
        position = self.position_in_tweet(pos)
        link = self.has_link(utterance)
        question_mark = self.has_question_mark(utterance)
        exclamation_mark = self.has_explanation_mark(utterance)
        hashtag = self.has_hashtag(utterance)
        emoticons = self.has_emoticons(utterance)
        question_words = self.has_question_word(utterance)
        first_verb, imperative = self.is_first_verb(utterance)
        lang_features = self.extract_lang_features(utterance, language_features)
        self.features = {'length': length, 'root_user': root_user, 'pos': position,
                         'link': link, 'question_mark': question_mark, 'exclamation_mark': exclamation_mark,
                         'hashtag': hashtag, 'emoticons': emoticons, 'question_words': question_words,
                         'first_verb': first_verb, 'imperative': imperative,  'language_features': lang_features}

    @staticmethod
    def position_in_tweet(pos):
        if pos > 2:
            return pos
        else:
            return 3

    def compare(self, existing_feature):
        # if self.features == existing_feature.features:
        #     return np.array_equal(self.word2vec, existing_feature.word2vec)
        # else:
        #     return False
        return self.features == existing_feature.features

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

    def extract_lang_features(self, utterance, tokens):
        language_features = [False]*len(tokens)
        shape = (64, len(language_features))
        embeddings_list = np.zeros(shape)
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
                # embedding = words2vec.find_word_embeddings(token[0], embeddings, embeddings_list, word_id, language_features)
                # if embedding is None:
                #     embedding = np.zeros(64)
                # embeddings_list = np.append(embeddings_list, embedding, axis=0)
                # embeddings_list.append(embedding)
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
    def delete_hashtag(utterance):
        new_utterance = ''
        tokens = utterance.split(' ')
        for token in tokens:
            if '#' in token:
                new_utterance += token[1:] + ' '
        return new_utterance[:-1]

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
        is_verb = False
        is_imperativ = False
        if '@' in utterance:
            utterance = Feature.delete_username(utterance)
        utterance = Feature.delete_conjuction(utterance)
        sentences = parse(utterance, relations=True, lemmata=True, tagset='STTS').split()
        pos_list = [ 'VVFIN','VAFIN', 'VVINF', 'VAINF', 'VVIZU', 'VVIMP', 'VAIMP', 'VVPP', 'VAPP']
        pos_imp = ['VVIMP', 'VAIMP']
        # a = mood(utterance)
        # print a
        if len(sentences) != 0:
            if len(sentences[0]) != 0:
                pos = sentences[0][0][1]
                if pos in pos_list:
                    is_verb = True
                    if pos in pos_imp:
                        is_imperativ = True
                    return is_verb, is_imperativ
        return is_verb, is_imperativ

    # @staticmethod
    # def delete_username(utterance):
    #     new_utterance = ''
    #     tokens = utterance.split(' ')
    #     for token in tokens:
    #         if '@' not in token:
    #             new_utterance += token + ' '
    #     return new_utterance[:-1]

    @staticmethod
    def delete_conjuction(utterance):
        conjuction_list = ['und', 'oder', 'aber']
        utterance = utterance.lower()
        tokens = utterance.split(' ')
        if tokens[0] in conjuction_list:
            return utterance.split(' ', 1)[1]
        else:
            return utterance










