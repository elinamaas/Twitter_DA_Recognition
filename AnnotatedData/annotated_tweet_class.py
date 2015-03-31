__author__ = 'snownettle'
import collections


class AnnotatedTweet:
    def __init__(self, tweet_id, text_id, text):
        self.tweet_id = tweet_id
        self.text_id = text_id
        self.tags = collections.defaultdict(dict) #tags for particular offset
        self.segmentation = {} #start_ofsset:end_offset, occurancy
        self.text = text
        self.word = {}
        # self.source_tags = collections.defaultdict(list)
        self.source_segmentation = set()

    def get_text(self):
        return self.text

    def set_word(self, word_dictionary):
        if len(self.word) == 0:
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
        self.tags[offset][da] = 1

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

    def find_offset(self, offset):
        offset_list = self.tags.keys()
        if offset in offset_list:
            return True
        else:
            return False

    # def n(self, offset, da):
    #     tag = self.tags[offset]
    #     del tag[da]

    def find_tweet_id(self, tweet_id):
        if self.tweet_id == tweet_id:
            return True
        else:
            return False

    def get_source_segmentation(self):
        return self.source_segmentation

    def add_source_segments(self, source_tags): #calculete segments on this step maybe
        tags_list = source_tags.keys()
        begin_tags = [tag for tag in tags_list if "B-" in tag]
        if '0' in source_tags:
            offset_for_zeros = source_tags['0']
            sorted(offset_for_zeros)
            start_offset = offset_for_zeros[0]
            for i in range(0, len(offset_for_zeros)):
                if (i + 1) == len(offset_for_zeros):
                    segment = str(start_offset) + ':' + str(offset_for_zeros[i])
                    self.source_segmentation.add(segment)
                    if segment in self.segmentation:
                        self.segmentation[segment] += 1
                    else:
                        self.segmentation[segment] = 1
                else:
                    if offset_for_zeros[i+1] - offset_for_zeros[i] != 1:
                        segment = str(start_offset) + ':' + str(offset_for_zeros[i])
                        start_offset = offset_for_zeros[i+1]
                        self.source_segmentation.add(segment)
                        if segment in self.segmentation:
                            self.segmentation[segment] += 1
                        else:
                            self.segmentation[segment] = 1
        for begin in begin_tags: #if two same da - twe end labels, should deal with it
            start_offsets = source_tags[begin]
            sorted(start_offsets)
            tag_name = begin.split('-')[1]
            intern_offsets = source_tags['I-' + tag_name]
            for start_offset in start_offsets:
                    #make with range
                if len(intern_offsets) == 0:
                    segment = str(start_offset) + ':' + str(start_offset)
                    self.source_segmentation.add(segment)
                    if segment in self.segmentation:
                        self.segmentation[segment] += 1
                    else:
                        self.segmentation[segment] = 1
                else:
                    for i in range(0, len(intern_offsets)):
                    # for intern_offset in intern_offsets:
                        if start_offset < intern_offsets[i]:
                            if i+1 != len(intern_offsets):
                                if intern_offsets[i+1] - intern_offsets[i] != 1:
                                    segment = str(start_offset) + ':' + str(intern_offsets[i])
                                    self.source_segmentation.add(segment)
                                    if segment in self.segmentation:
                                        self.segmentation[segment] += 1
                                    else:
                                        self.segmentation[segment] = 1
                                    break
                            else: #last token
                                segment = str(start_offset) + ':' + str(intern_offsets[i])
                                self.source_segmentation.add(segment)
                                if segment in self.segmentation:
                                    self.segmentation[segment] += 1
                                else:
                                    self.segmentation[segment] = 1
                                break

    @staticmethod
    def check_if_tweet_exists(list_of_tweets, tweet_id, text_id, text):
        for tweet in list_of_tweets:
            if tweet.find_tweet_id(tweet_id) is True:
                return tweet
            else:
                continue
        return AnnotatedTweet(tweet_id, text_id, text)
