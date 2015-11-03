from analysing_GS import emoticons, question_words
from pattern.de import parse, split
import re
from learning import words2vec
import numpy as np

__author__ = 'snownettle'


class Feature:
    """
        Feature extraction from a segment
        Features:
        1. Length : length of the utterance
        2. Root user: Is the utterancce belongs to the root user or not :type: root_user: boolean
        3. Position of the utterance in tweet. Is it first: :type: pos: int
        4. Link: is there a link in a segment :type: link: boolean
        5. Question mark :type: boolean
        6. Exclamation mark :type: boolean
        7. Hashtag :type: boolean
        8. Emoticons :type: boolean
        9. Question words :type: boolean
        10. First verb :type: boolean
        11. First verb imperativ :type: boolean
        12. Oder :type: boolean
        13. Language features: a list with boolens, each item represents a words.
                               True - this word appears in a segment, otherwise False :type language_features: list
        14. Word embeddings :type: vector


    """
        #
    def __init__(self, utterance, start_offset, end_offset, root_username, current_username, pos, embeddings, word_id):
        self.features = dict()
        self.word2vec = np.zeros((64,))
        # self.word2vec = list()
        # self.features_hmm = list()
        self.token_appearance = dict()
        self.extract_features(utterance, start_offset, end_offset, root_username, current_username, pos, embeddings, word_id)
        # self.features_hmm = self.extract_features_hmm()
        self.language_features_full = list()
        self.language_features_reduced = list()
        self.language_features_minimal = list()

    def add_language_features(self, tf_idf_full, tf_idf_reduced, tf_idf_min):
        self.language_features_full = [t in self.token_appearance for t in tf_idf_full]
        self.language_features_reduced = [t in self.token_appearance for t in tf_idf_reduced]
        self.language_features_minimal = [t in self.token_appearance for t in tf_idf_min]

    def extract_features(self, utterance, start_offset, end_offset, root_username, current_username, pos, embeddings, word_id):
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
        oder = self.has_word_oder(utterance)
        word_embeddings, token_appearance = self.extract_lang_features(utterance, embeddings, word_id)
        self.token_appearance = token_appearance
        self.word2vec = word_embeddings
        self.features = {'length': length, 'root_user': root_user, 'pos': position,
                         'link': link, 'question_mark': question_mark, 'exclamation_mark': exclamation_mark,
                         'hashtag': hashtag, 'emoticons': emoticons, 'question_words': question_words,
                         'first_verb': first_verb, 'imperative': imperative, 'oder': oder}
            # ,  'language_features': lang_features}
                         # 'word_embeddings': word_embeddings}

    @staticmethod
    def position_in_tweet(pos):
        if pos > 2:
            return pos
        else:
            return 3

    def has_word_oder(self, utterance):
        utterance = utterance.lower()
        tokens = utterance.split(' ')
        for token in tokens:
            if token == 'oder':
                return True
        return False

    def extract_lang_features(self, utterance, embeddings, word_id):
        shape = (64,)
        word_embeddings = np.zeros(shape)
        token_appearance = dict()
        if '@' in utterance:
            utterance = self.delete_username(utterance)
        if self.has_link(utterance):
            utterance = self.delete_link(utterance)
        utterance = self.delete_non_alphabetic_symbols(utterance)
        sentences = parse(utterance, relations=True, lemmata=True).split()
        # tokens = utterance.split(' ')
        token_number = 1
        for sentence in sentences:
            token_number += len(sentence)
            for token in sentence:
                if token[5] in token_appearance:
                    token_appearance[token[5]] += 1
                else:
                    token_appearance[token[5]] = 1
                embedding = words2vec.find_word_embeddings(token[0], embeddings, word_id)
                if embedding is not None:
                    word_embeddings = np.add(word_embeddings, embedding)
                    # embedding = np.zeros(64)
                # embeddings_list = np.append(embeddings_list, embedding, axis=0)
                # embeddings_list.append(embedding)
        if token_number > 1:
            token_number = token_number - 1
        word_embeddings = np.divide(word_embeddings, token_number)
        return word_embeddings, token_appearance

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

    @staticmethod
    def delete_conjuction(utterance):
        conjuction_list = ['und', 'oder', 'aber']
        utterance = utterance.lower()
        tokens = utterance.split(' ')
        if tokens[0] in conjuction_list:
            return utterance.split(' ', 1)[1]
        else:
            return utterance




