__author__ = 'snownettle'


def if_tag(tag_name, list_of_tag):
    for tag in list_of_tag:
        for key, value in tag.iteritems():
            if tag_name == key:
                return True
    return False


class Segmentation:
    def __init__(self, tweet_id):
        self.tweet_id = tweet_id
        self.segmentation = {}
        self.tags = {}

    def get_tags(self):
        return self.tags

    def get_segments(self):
        return self.segmentation

    def get_id(self):
        return self.tweet_id

    def set_segmentation(self, segmentation):
        self.segmentation = segmentation

    @staticmethod
    def add_information(tweet, offset_list):
        for offset, tag in offset_list.iteritems():
            tag = str(tag)
            if offset in tweet.segmentation:
                tweet.segmentation[offset] += 1
                list_of_tag = tweet.tags[offset]
                if if_tag(tag, list_of_tag) is True:
                    for tag_occurance in list_of_tag:
                        for key, vl in tag_occurance.iteritems():
                            if tag == key:
                                tag_occurance[tag] += 1
                else:
                    value = dict()
                    value[tag] = 1
                    list_of_tag.append(value)
            else:
                tweet.segmentation[offset] = 1
                value = dict()
                value[tag] = 1
                new_list = [value]
                tweet.tags[offset] = new_list
        return tweet

    @staticmethod
    def add_tags(tweet, offset, tag):
        value = {}
        if offset in tweet.tags:
            value = tweet.tags[offset]
            if tag in value:
                value[tag] += 1
            else:
                value[tag] = 1
        else:
            value[tag] = 1
            tweet.tags[offset] = value

    @staticmethod
    def find_tweet_by_id(tweet_id, list_of_tweets):
        for tweet in list_of_tweets:
            if tweet_id == tweet.tweet_id:
                return tweet
        return Segmentation(tweet_id)


