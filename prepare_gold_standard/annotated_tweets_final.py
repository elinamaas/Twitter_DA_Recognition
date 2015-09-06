__author__ = 'snownettle'

import os.path
from prepare_gold_standard.editing_annotated_tweets import tweets_to_be_reviewed, majority_vote, \
    rewrite_segmentation, merge_da_children, numbers_of_tweets_agreed_by_three
from da_recognition.dialogue_acts_taxonomy import build_da_taxonomy_full
from prepare_gold_standard.write_to import write_to_xlsx_file
from prepare_gold_standard import inter_annotater_agreement
from statistics import annotatedData_stat
from prepare_gold_standard.rebuild_conversations import delete_non_german_tweets_from_conversation, \
    conversation_regarding_language
from postgres import postgres_queries


def iaa_ontologies(collectionAnnotatedData, ontology):

    list_of_annotated_tweets = tweets_to_be_reviewed(collectionAnnotatedData, ontology)
    new_tweets_lang, conversation_list = conversation_regarding_language()
    #delete not german tweets
    list_of_annotated_tweets = delete_non_german_tweets_from_conversation(list_of_annotated_tweets, new_tweets_lang)

    agreed_with_segmentation, agreed, tweets_to_edit = numbers_of_tweets_agreed_by_three(list_of_annotated_tweets)
    tweet_id_three_annotator = annotatedData_stat.students_tweets()

    inter_annotater_agreement.chance_corrected_coefficient_labels(list_of_annotated_tweets, tweet_id_three_annotator)
    inter_annotater_agreement.chance_corrected_coefficient_categories(agreed_with_segmentation, ontology)

    annotatedData_stat.number_of_annotated_tweet(list_of_annotated_tweets)
    annotatedData_stat.numbers_of_tweets_agreed_by_three(agreed_with_segmentation, agreed)
    return agreed, tweets_to_edit


def merging(agreed, tweets_to_edit):

    print 'First merge of tags after reading the data' #choosing where is the number bigger
    #first merge of tags, after building the list
    tweets_to_edit = majority_vote(tweets_to_edit)
    rewrite_segmentation(tweets_to_edit)
    list_of_tweets_done, tweets_to_edit = annotatedData_stat.numbers_of_agreed_tweets_after_merging(tweets_to_edit, agreed)
    agreed += list_of_tweets_done

    print 'First merge of tag children'
    #first merge of children
    da_taxonomy = build_da_taxonomy_full()
    merge_da_children(tweets_to_edit, da_taxonomy)
    rewrite_segmentation(tweets_to_edit)
    list_of_tweets_done, tweets_to_edit = annotatedData_stat.numbers_of_agreed_tweets_after_merging(tweets_to_edit, agreed)
    agreed += list_of_tweets_done

    print 'Second merge of tags'
    #second merge of tags
    tweets_to_edit = majority_vote(tweets_to_edit)
    rewrite_segmentation(tweets_to_edit)
    list_of_tweets_done, tweets_to_edit = annotatedData_stat.numbers_of_agreed_tweets_after_merging(tweets_to_edit, agreed)
    agreed += list_of_tweets_done

    #check segmentation
    # check_final_segmentation(list_of_tweets_done)

    if os.path.isfile('DATA/goldenStandard/tweet_to_edit.csv') is False:
        write_to_xlsx_file(tweets_to_edit, 'DATA/goldenStandard/tweet_to_edit.csv')
        write_to_xlsx_file(agreed, 'DATA/goldenStandard/done_tweet.csv')



