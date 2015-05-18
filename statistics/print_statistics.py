__author__ = 'snownettle'
import rawData_stat
from twitter_objects import conversation
from mongoDB import mongoDB_configuration


def stats_for_raw_data():
    print 'starting...'
    collectionRawTwitterData = mongoDB_configuration.get_collection('DARecognition', 'rawTwitterData')
    print 'Indexing ids ...'
    collectionRawTwitterData.ensure_index('id')
    print 'Indexing in_reply_to_status_id...'
    collectionRawTwitterData.ensure_index('in_reply_to_status_id')
    print 'Start building conversations'
    conversation_list = conversation.build_conversation(collectionRawTwitterData)
    rawData_stat.number_of_conversation_with_replays(conversation_list)
    rawData_stat.depth_of_conversation(conversation_list)
    rawData_stat.width_of_conversation(conversation_list)
    rawData_stat.longest_conversation(conversation_list)


# def stats_for_annotated_data():
#     collectionAnnotatedData = mongoDB_configuration.get_collection('DARecognition', 'annotatedTwitterData')
#     list_of_annotated_tweets = segmentation(collectionAnnotatedData)
#     annotatedData_stat.number_of_annotated_tweet(list_of_annotated_tweets)
#     annotatedData_stat.numbers_of_tweets_agreed_by_three(list_of_annotated_tweets)
#
#     print 'First merge of tags after reading the data' #choosing where is the number bigger
#     #first merge of tags, after building the list
#     list_of_annotated_tweets = merge_annotations(list_of_annotated_tweets)
#     rewrite_segmentation(list_of_annotated_tweets)
#     list_of_tweets_done, list_of_tweets_for_editing = annotatedData_stat.numbers_of_agreed_tweets_after_merging(list_of_annotated_tweets)
#
#     print 'First merge of tag children'
#     #first merge of children
#     da_taxonomy = build_da_taxonomy()
#     merge_da_children(list_of_annotated_tweets, da_taxonomy)
#     rewrite_segmentation(list_of_annotated_tweets)
#     list_of_tweets_done, list_of_tweets_for_editing = annotatedData_stat.numbers_of_agreed_tweets_after_merging(list_of_annotated_tweets)
#
#     print 'Second merge of tags'
#     #second merge of tags
#     list_of_annotated_tweets = merge_annotations(list_of_annotated_tweets)
#     rewrite_segmentation(list_of_annotated_tweets)
#     list_of_tweets_done, list_of_tweets_for_editing = annotatedData_stat.numbers_of_agreed_tweets_after_merging(list_of_annotated_tweets)
#
#     annotatedData_stat.segments_in_tweet(list_of_tweets_done)
#     write_to_xlsx_file(list_of_tweets_for_editing, '../DATA/tweet_to_edit.xlsx')
#     write_to_xlsx_file(list_of_tweets_done, '../DATA/done_tweet.xlsx')

# print 'Stats for annotated data:'
# stats_for_annotated_data()
# print 'Stats for raw data: '
# stats_for_raw_data()


