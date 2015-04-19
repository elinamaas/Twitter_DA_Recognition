__author__ = 'snownettle'
from mongoDB import mongoDB_configuration
from annotatedData.editing_annotated_tweets import segmentation, merge_annotations, \
    rewrite_segmentation, merge_da_children, check_final_segmentation, numbers_of_tweets_agreed_by_three
from statistics import annotatedData_stat
from annotation.dialogue_acts_tree import build_da_taxonomy
from annotatedData.write_to import write_to_xlsx_file
import os.path


def editing_annotated_tweets(collectionAnnotatedData):

    list_of_annotated_tweets = segmentation(collectionAnnotatedData)
    agreed_with_segmentation, agreed, tweets_to_edit = numbers_of_tweets_agreed_by_three(list_of_annotated_tweets)
    annotatedData_stat.number_of_annotated_tweet(list_of_annotated_tweets)
    annotatedData_stat.numbers_of_tweets_agreed_by_three(agreed_with_segmentation, agreed)

    print 'First merge of tags after reading the data' #choosing where is the number bigger
    #first merge of tags, after building the list
    tweets_to_edit = merge_annotations(tweets_to_edit)
    rewrite_segmentation(tweets_to_edit)
    list_of_tweets_done, tweets_to_edit = annotatedData_stat.numbers_of_agreed_tweets_after_merging(tweets_to_edit, agreed)
    agreed += list_of_tweets_done

    print 'First merge of tag children'
    #first merge of children
    da_taxonomy = build_da_taxonomy()
    merge_da_children(tweets_to_edit, da_taxonomy)
    rewrite_segmentation(tweets_to_edit)
    list_of_tweets_done, tweets_to_edit = annotatedData_stat.numbers_of_agreed_tweets_after_merging(tweets_to_edit, agreed)
    agreed += list_of_tweets_done

    print 'Second merge of tags'
    #second merge of tags
    tweets_to_edit = merge_annotations(tweets_to_edit)
    rewrite_segmentation(tweets_to_edit)
    list_of_tweets_done, tweets_to_edit = annotatedData_stat.numbers_of_agreed_tweets_after_merging(tweets_to_edit, agreed)
    agreed += list_of_tweets_done

    #check segmentation
    # check_final_segmentation(list_of_tweets_done)

    if os.path.isfile('DATA/goldenStandard/tweet_to_edit.csv') is False:
        write_to_xlsx_file(tweets_to_edit, 'DATA/goldenStandard/tweet_to_edit.csv')
        write_to_xlsx_file(agreed, 'DATA/goldenStandard/done_tweet.csv')

    # tweets_id = set()
    # for tweet in list_of_annotated_tweets:
    #     tweets_id.add(int(tweet.get_tweet_id()))
    # return tweets_id


