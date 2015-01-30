__author__ = 'snownettle'
class Tweet:
    def __init__(self, tweet_id, replays_ids=[]):
        self.id = tweet_id
        self.replays = replays_ids

    def set_replay(self, tweet):
        self.replays.append(tweet)

    def search_by_id(self, tweet_id):
        if self.id == tweet_id:
            return self
        else:
            return None

    def get_id(self):
        return self.id

    # def conversation_length(tweet, length):
    #     if len(tweet.replays)>0
    #         for replay in tweet.replays:
    #             length+=1
    #             conversation_length(replay, length)
    #
    # def conversation_length(self, length):
    #     if len(self.replays)>0:
    #         for tweet in self.replays:
    #             length+=1
    #             conversation_length()


