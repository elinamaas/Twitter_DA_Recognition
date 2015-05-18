__author__ = 'snownettle'

from mongoDB import queries, mongoDB_configuration
from treelib import Tree
from postgres import postgres_queries
from prepare_golden_standard import rebuild_conversations


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


def students_tweets():# how much tweets were annotated by 1, 2 or 3 students
    new_list_tweet_german = rebuild_conversations.conversation_regarding_language()
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


def segments_in_tweets(list_of_tweets):
    da_instatnses = 0
    segments_count = dict()
    for tweet_id in list_of_tweets:
        results = postgres_queries.find_segments(tweet_id)
        da_instatnses += len(results)
        if len(results) == 0:
            print 'uu'
        if len(results) in segments_count:
            segments_count[len(results)] += 1
        else:
            segments_count[len(results)] = 1
    print da_instatnses
    for segment, count in segments_count.iteritems():
        print segment, '\t', count


def types_of_conversation():
    #find short and long conversation, their depth and width
    conversation_amount = postgres_queries.find_annotated_conversation_number()
    conversation_list = list()
    depth_dict = dict()
    depth_dict_long = dict()
    depth_dict_short = dict()
    number_of_tweets_dict = dict()
    for i in range (0, conversation_amount + 1, 1):
        conversation_tree = Tree()
        converastion = postgres_queries.find_conversation(i)
        for tweet in converastion:
            if tweet[1] is None:
                conversation_tree.create_node(tweet[0], tweet[0])
                rebuild_conversations.build_conversation(tweet[0], converastion, conversation_tree)
                depth = conversation_tree.depth() + 1
                number_of_tweets = len(conversation_tree.all_nodes())
                #short/long
                if number_of_tweets >=20:
                    if depth in depth_dict_long:
                        depth_dict_long[depth] += 1
                    else:
                        depth_dict_long[depth] = 1
                else:
                    if depth in depth_dict_short:
                        depth_dict_short[depth] += 1
                    else:
                        depth_dict_short[depth] = 1

                if number_of_tweets in number_of_tweets_dict:
                    number_of_tweets_dict[number_of_tweets] += 1
                else:
                     number_of_tweets_dict[number_of_tweets] = 1
                if depth in depth_dict:
                    depth_dict[depth] += 1
                else:
                    depth_dict[depth] = 1
        conversation_list.append(conversation_tree)
    #print depth_dict
    print 'Depth of a conversation'
    for depth, count in depth_dict.iteritems():
        print depth, '\t', count
    print 'Number of tweets in a conversation'
    for number, count in number_of_tweets_dict.iteritems():
        print number, '\t', count
    print 'Depth of a long conversation'
    for depth, count in depth_dict_long.iteritems():
        print depth, '\t', count
    print 'Depth of a short conversation'
    for depth, count in depth_dict_short.iteritems():
        print depth, '\t', count

    return conversation_list