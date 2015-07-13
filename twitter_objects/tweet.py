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


class AnnotatedTweetFinal:
    def __init__(self, tweet_id, tweet_text, in_replay_to, conversation_id):
        self.tweet_id = tweet_id
        self.tweet_text = tweet_text
        self.in_replay_to = in_replay_to
        self.tokens = dict() # offset, [word, da]
        self.segments = dict() #start-end offset, da
        self.conversation_id = conversation_id
        self.start_position = False
        self.end_position = False
        self.intemediate_position = False

    def get_tweet_id(self):
        return self.tweet_id

    def get_tweet_text(self):
        return self.tweet_text

    def get_in_replay_to_id(self):
        return self.in_replay_to

    def get_tokens(self):
        return self.tokens

    def get_segments(self):
        return self.segments

    def get_conversation_id(self):
        return self.conversation_id

    def set_tokens(self, offset, token, da):
        self.tokens[offset] = [token, da]

    def set_segments(self):
        previous_tag = ''
        start_offset = '4'
        end_offset = ''
        token_da_dict = self.tokens
        for i in range(4, len(self.tokens) + 4, 1):
            token = token_da_dict[str(i)][0]
            da = token_da_dict[str(i)][1]
            if i == len(self.tokens) + 4 - 1:
                # last token
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