__author__ = 'snownettle'
from learning.feature import Feature


class Segment:
    def __init__(self, username, root_user, segment, tweet_id, position, embeddings, word_id):
        self.segment = segment[5]
        self.user = username
        self.root_user = root_user
        self.segment_in_tweet = position
        self.tweet_id = tweet_id
        self.start_offset = segment[0]
        self.end_offset = segment[1]
        self.da_id_full = segment[2]
        self.da_id_reduced = segment[3]
        self.da_id_minimal = segment[4]
        self.features = Feature(self.segment, self.start_offset, self.end_offset, self.root_user, self.user,
                                self.segment_in_tweet, embeddings, word_id)


    def get_da_by_taxonomy(self, taxonomy):
        if taxonomy == 'full':
            return self.da_id_full
        elif taxonomy == 'reduced':
            return self.da_id_reduced
        else:
            return self.da_id_minimal

    def get_username(self):
        return self.user


class Branch:
    def __init__(self):
        self.start = None
        self.end = None
        self.branch = list()

    def add_start_segment(self, segment):
        self.start = segment
        self.end = segment
        self.branch.append(segment)

    def add_segment(self, segment):
        self.end = segment
        self.branch.append(segment)

    def get_segments(self):
        return self.branch

    def start_segment(self):
        return self.start

    def end_segment(self):
        return self.end