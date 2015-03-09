__author__ = 'snownettle'

from treelib import Tree
class Tweet:
    def __init__(self, tweet_id):
        self.tweet_id = tweet_id
        # self.replays = set()

    # def add_replay(self, tweet):
    #     self.replays.add(tweet)

    def get_tweet_id(self):
        return self.tweet_id

    def find_by_id(self, tweet_id):
        if self.tweet_id == tweet_id:
            return True
        else:
            return False

