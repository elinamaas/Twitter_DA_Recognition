__author__ = 'snownettle'
import collections

class Annotated_Tweet:
    def __init__(self, tweet_id, text_id, text):
        self.tweet_id = tweet_id
        self.text_id = text_id
        self.tags = collections.defaultdict(dict) #tags for particular offset
        self.segmentation = {} #start_ofsset:end_offset
        self.text = text
        self.word = {}

    def get_text(self):
        return self.text

    def set_word(self, word_dictionary):
        if len(self.word)== 0:
            self.word = word_dictionary
        return self

    def get_word(self, offset):
        return self.word[offset]

    def get_tweet_id(self):
        return self.tweet_id

    def get_text_id(self):
        return self.text_id

    def get_tags(self):
        return self.tags

    def get_segmentation(self):
        return self.segmentation

    def set_new_segmentation(self, segmentation):
        self.segmentation = {}
        self.segmentation = segmentation

    def add_segmentation(self, offsets):
        for offset in offsets:
            if offset in self.segmentation.keys():
                self.segmentation[offset] += 1
            else:
                self.segmentation[offset] = 1
        return self

    def set_tags(self, offset, da):
        # tag = dict()
        # tag[da] = 1
        self.tags[offset][da] = 1

    # old function with list, replace with dictionary of dictionay
    # def set_token(self, offset, da):
    #     tag = dict()
    #     tag[da] = 1
    #     if offset in self.token.keys():
    #         list_of_tags = self.token[offset]
    #         list_of_tags.append(tag)
    #     else:
    #         list_of_tags = [tag]
    #         self.token[offset] = list_of_tags

    def add_tag(self, tags_dictionary):
        for offset, da in tags_dictionary.iteritems():
            if offset in self.get_tags():
                offset_tags_dictionary = self.tags[offset]
                if isinstance(da, str):
                    if da in offset_tags_dictionary:
                        self.update_tag(offset, da)
                    else:
                        self.set_tags(offset, da)
                elif isinstance(da, list):
                    for tag_name in da:
                        if tag_name in offset_tags_dictionary:
                            self.update_tag(offset, tag_name)
                        else:
                            self.set_tags(offset, tag_name)
            else:
                if isinstance(da, str):
                    self.set_tags(offset, da)
                else:
                    for tag_name in da:
                        self.set_tags(offset, tag_name)
        return self

    def update_tag(self, offset, da):
        self.tags[offset][da] += 1
        # if len(self.token) == 0:
        #     for offset, da in tags_dictionary.iteritems():
        #         if type(da) is str:
        #             self.set_token(offset, da)
        #         else:
        #             self.add_token_list(offset, da)
        #     return self
        # else:
        #     for offset, da in tags_dictionary.iteritems():
        #         if type(da) is str:
        #             self.update_token(offset, da)
        #         else:
        #             self.add_token_list(offset, da)

    # def add_token(self, tags_dictionary):
    #     if len(self.token) == 0:
    #         for offset, da in tags_dictionary.iteritems():
    #             if type(da) is str:
    #                 self.set_token(offset, da)
    #             else:
    #                 self.add_token_list(offset, da)
    #         return self
    #     else:
    #         for offset, da in tags_dictionary.iteritems():
    #             if type(da) is str:
    #                 self.update_token(offset, da)
    #             else:
    #                 self.add_token_list(offset, da)
    #         return self

    # def add_token_list(self, offset, tags):
    #     for da in tags:
    #         da_dict = dict()
    #         da_dict[offset] = da
    #         self.add_token(da_dict)

    # def update_token(self, offset, da):
    #     if self.find_offset(offset) is True:
    #         tags_list = self.token[offset]
    #         if self.find_tag(offset, da) is True:
    #             for tag in tags_list:
    #                 for tag_name, count in tag.iteritems():
    #                     if tag_name == da:
    #                         tag[da] += 1
    #         else:
    #             self.set_token(offset, da)
    #     else:
    #         self.set_token(offset, da)

    # def find_tag(self, offset, da):
    #     tags_list = self.tags[offset]
    #     for tag in tags_list:
    #         for tag_name, count in tag.iteritems():
    #             if tag_name == da:
    #                 return True
    #     return False

    def find_offset(self, offset):
        offset_list = self.tags.keys()
        if offset in offset_list:
            return True
        else:
            return False

    def n(self, offset, da):
        tag = self.tags[offset]
        del tag[da]

    def find_tweet_id(self, tweet_id):
        if self.tweet_id == tweet_id:
            return True
        else:
            return False

    @staticmethod
    def check_if_tweet_exists(list_of_tweets, tweet_id, text_id, text):
        for tweet in list_of_tweets:
            if tweet.find_tweet_id(tweet_id) is True:
                return tweet
            else:
                continue
        return Annotated_Tweet(tweet_id, text_id, text)
