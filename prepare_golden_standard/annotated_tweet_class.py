__author__ = 'snownettle'
import collections


class AnnotatedTweetEdit:
    def __init__(self, tweet_id, text_id, text):
        self.tweet_id = tweet_id
        self.text_id = text_id
        self.tags_full = collections.defaultdict(dict) #tags for particular offset
        self.tags_reduced = collections.defaultdict(dict) #tags for particular offset
        self.tags_minimal = collections.defaultdict(dict) #tags for particular offset
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

    def get_tags_full(self):
        return self.tags_full

    def get_tags_reduced(self):
        return self.tags_reduced

    def get_tags_minimal(self):
        return self.tags_minimal

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

    def set_tags_full(self, offset, da):
        self.tags_full[offset][da] = 1

    def set_tags_reduced(self, offset, da):
        self.tags_reduced[offset][da] = 1

    def set_tags_minimal(self, offset, da):
        self.tags_minimal[offset][da] = 1

    def add_tag_full(self, tags_dictionary):
        for offset, da in tags_dictionary.iteritems():
            if offset in self.get_tags_full():
                offset_tags_dictionary = self.tags_full[offset]
                if isinstance(da, str):
                    if da in offset_tags_dictionary:
                        self.update_tag_full(offset, da)
                    else:
                        self.set_tags_full(offset, da)
                elif isinstance(da, list):
                    for tag_name in da:
                        if tag_name in offset_tags_dictionary:
                            self.update_tag_full(offset, tag_name)
                        else:
                            self.set_tags_full(offset, tag_name)
            else:
                if isinstance(da, str):
                    self.set_tags_full(offset, da)
                else:
                    for tag_name in da:
                        self.set_tags_full(offset, tag_name)
        return self

    def add_tag_reduced(self, tags_dictionary):
        for offset, da in tags_dictionary.iteritems():
            if offset in self.get_tags_reduced():
                offset_tags_dictionary = self.tags_reduced[offset]
                if isinstance(da, str):
                    if da in offset_tags_dictionary:
                        self.update_tag_reduced(offset, da)
                    else:
                        self.set_tags_reduced(offset, da)
                elif isinstance(da, list):
                    for tag_name in da:
                        if tag_name in offset_tags_dictionary:
                            self.update_tag_reduced(offset, tag_name)
                        else:
                            self.set_tags_reduced(offset, tag_name)
            else:
                if isinstance(da, str):
                    self.set_tags_reduced(offset, da)
                else:
                    for tag_name in da:
                        self.set_tags_reduced(offset, tag_name)
        return self

    def add_tag_minimal(self, tags_dictionary):
        for offset, da in tags_dictionary.iteritems():
            if offset in self.get_tags_minimal():
                offset_tags_dictionary = self.tags_minimal[offset]
                if isinstance(da, str):
                    if da in offset_tags_dictionary:
                        self.update_tag_minimal(offset, da)
                    else:
                        self.set_tags_minimal(offset, da)
                elif isinstance(da, list):
                    for tag_name in da:
                        if tag_name in offset_tags_dictionary:
                            self.update_tag_minimal(offset, tag_name)
                        else:
                            self.set_tags_minimal(offset, tag_name)
            else:
                if isinstance(da, str):
                    self.set_tags_minimal(offset, da)
                else:
                    for tag_name in da:
                        self.set_tags_minimal(offset, tag_name)
        return self

    def update_tag_full(self, offset, da):
        self.tags_full[offset][da] += 1

    def update_tag_reduced(self, offset, da):
        self.tags_reduced[offset][da] += 1

    def update_tag_minimal(self, offset, da):
        self.tags_minimal[offset][da] += 1

    def find_offset(self, offset):
        offset_list = self.tags_full.keys()
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
        return AnnotatedTweetEdit(tweet_id, text_id, text)


class AnnotatedTweet: #for final version, after every merging
    def __init__(self, tweet_id, tweet_text):
        self.tweet_id = tweet_id
        self.tweet_text = tweet_text
        self.segments = dict() # offset: DA
        self.tokens = dict() #offset:{token:da}

    def get_tweet_id(self):
        return self.tweet_id

    def get_text(self):
        return self.tweet_text

    def get_segments(self):
        return self.segments

    def get_tokens(self):
        return self.tokens

    def set_segments(self):
        previous_tag = ''
        start_offset = '4'
        end_offset = ''
        token_da_dict = self.tokens
        for i in range(4, len(self.tokens) + 4, 1):
            token_da = token_da_dict[str(i)]
            for token, da in token_da.iteritems():
                if i == len(self.tokens) + 4 - 1:

                    if i == 4:
                        segmentation_offset = start_offset + ':' + str(i)
                        self.segments[segmentation_offset] = da
                    else:
                        if previous_tag != da:
                            segmentation_offset = start_offset + ':' + str(i-1)
                            self.segments[segmentation_offset] = previous_tag
                            segmentation_offset = str(i) + ':' + str(i)
                            self.segments[segmentation_offset] = da
                        else:
                            segmentation_offset = start_offset + ':' + str(i)
                            self.segments[segmentation_offset] = da

                else:
                    if previous_tag == '':
                        start_offset = str(i)
                        previous_tag = da
                    elif previous_tag != da:
                        end_offset = str(i-1)
                        segmentation_offset = start_offset + ':' + end_offset
                        self.segments[segmentation_offset] = previous_tag
                        previous_tag = da
                        start_offset = str(i)

    def set_token(self, offset, token, da):
        token_da = dict()
        token_da[token] = da
        self.tokens[offset] = token_da


