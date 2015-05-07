__author__ = 'snownettle'

# from postgres import postgres_queries
# from twitter_objects.conversation import Conversation
from mongoDB import queries, mongoDB_configuration
import test



def number_of_annotated_tweet(list_of_tweets):
    print 'There are ', len(list_of_tweets), ' annotated tweets by linguistic students in DB'


def numbers_of_tweets_agreed_by_three(agreed_with_segmentation, agreed_with_tags):
    print 'The students are agreed with segmentation for ', len(agreed_with_segmentation), 'of tweets'
    print 'The students are agreed with tags for ', len(agreed_with_tags), 'of tweets'


def numbers_of_agreed_tweets_after_merging(list_of_tweets, agreed):
    argeed_with_tags = 0
    list_of_tweets_for_editing = list()
    list_of_tweets_done = list()
    for tweet in list_of_tweets:
        same_decision = 0
        token_dictionary = tweet.get_tags()
        token_number = len(token_dictionary)
        for offset, tags in token_dictionary.iteritems():
            if len(tags) == 1:
                same_decision += 1
        if same_decision == token_number:
            argeed_with_tags += 1
            list_of_tweets_done.append(tweet)

        else:
            list_of_tweets_for_editing.append(tweet)
    print 'After merging there are ' + str(len(list_of_tweets_done) + len(agreed)) + ' done tweets'
    print 'There are ' + str(len(list_of_tweets_for_editing)) + ' to edit'
    return list_of_tweets_done, list_of_tweets_for_editing


#rewrite!

def segments_in_tweet(list_of_annotated_tweets):
    number_of_segments = dict()
    average_number_of_tweets = list()
    overal_segments = 0
    for tweet in list_of_annotated_tweets:
        segments = tweet.get_segments()
        occurrence = len(segments)
        overal_segments += occurrence
        if occurrence in number_of_segments:
            number_of_segments[occurrence] += 1
        else:
            number_of_segments[occurrence] = 1
    for number, value in number_of_segments.iteritems():
        print 'Number of segments: ', number, ' occur: ', value, ' times'


def unigrams_raw_annotation(list_of_annotated_tweets):
    number_of_unigrams = dict()
    for tweet in list_of_annotated_tweets:
        tags = tweet.get_tags()
        for segment, tag in tags.iteritmes:
            if segment in number_of_unigrams:
                number_of_unigrams[segment] += 1
            else:
                number_of_unigrams[segment] = 1
    for tag_name, occurancy in number_of_unigrams.iteritems():
        print tag_name + '; ' + occurancy
    # return number_of_unigrams


def students_tweets():
    new_list_tweet_german = test.conversation_regarding_language()
    collection = mongoDB_configuration.get_collection('DARecognition', 'annotatedTwitterData')
    results = queries.find_all(collection)
    tweets_dict = dict()
    for tweet in results:
        tweet_id = long(tweet['tweet_id'])
        if tweet_id in new_list_tweet_german:
            if tweet_id in tweets_dict:
                tweets_dict[tweet_id] += 1
            else:
                tweets_dict[tweet_id] = 1
    statistics = dict()
    for tweet_id, count in tweets_dict.iteritems():
        if count in statistics:
            statistics[count] += 1
        else:
            statistics[count] = 1
    for students, number_of_tweets in statistics.iteritems():
        print str(number_of_tweets) + ' were annotated by ' + str(students) + ' students'
    three_annotators = set()
    for tweet_id, count in tweets_dict.iteritems():
        if count == 3:
            three_annotators.add(tweet_id)

    return three_annotators#ids with 3 annotator


students_tweets()