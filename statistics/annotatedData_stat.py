__author__ = 'snownettle'


def number_of_annotated_tweet(list_of_tweets):
    print 'There are ', len(list_of_tweets), ' annotated tweets by linguistic students in DB'


def numbers_of_tweets_agreed_by_three(list_of_tweets):
    agreed_with_segmentation = 0
    argeed_with_tags = 0
    for tweet in list_of_tweets:
        same_dicision = 0
        segmentation_dictionary = tweet.get_segmentation()
        segmentation_values = segmentation_dictionary.values()
        if 2 not in segmentation_values and 1 not in segmentation_values:
            agreed_with_segmentation += 1
            token_dictionary = tweet.get_tags()
            token_number = len(token_dictionary)
            for offset, tags in token_dictionary.iteritems():
                if len(tags) == 1:
                    for tag_name, agreed in tags.iteritems():
                        if agreed == 3:
                            same_dicision += 1
            if same_dicision == token_number:
                argeed_with_tags += 1

    print 'The students are agreed with segmentation for ', agreed_with_segmentation, 'of tweets'
    print 'The students are agreed with tags for ', argeed_with_tags, 'of tweets'


def numbers_of_agreed_tweets_after_merging(list_of_tweets):
    argeed_with_tags = 0
    list_of_tweets_for_editing = list()
    list_of_tweets_done = list()
    for tweet in list_of_tweets:
        same_dicision = 0
        token_dictionary = tweet.get_tags()
        token_number = len(token_dictionary)
        for offset, tags in token_dictionary.iteritems():
            if len(tags) == 1:
                for tag_name, agreed in tags.iteritems():
                    # if agreed == 3:
                    same_dicision += 1
        if same_dicision == token_number:
            argeed_with_tags += 1
            list_of_tweets_done.append(tweet)

        else:
            list_of_tweets_for_editing.append(tweet)
    print 'After merging there are ' + str(len(list_of_tweets_done)) + ' done tweets'
    print 'There are ' + str(len(list_of_tweets_for_editing)) + ' to edit'
    return list_of_tweets_done, list_of_tweets_for_editing


