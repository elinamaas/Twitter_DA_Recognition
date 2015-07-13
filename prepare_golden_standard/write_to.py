__author__ = 'snownettle'
import xlsxwriter
import re
import rebuild_conversations
from postgres import postgres_queries
from mongoDB import mongoDBQueries, mongoDB_configuration


def write_to_xlsx_file(list_of_tweets, file_name):
    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()
    row = 1
    col = 0
    worksheet.write(0, 0, 'offset')
    worksheet.write(0, 1, 'token')
    worksheet.write(0, 2, 'variant 1')
    worksheet.write(0, 3, 'variant 2')
    worksheet.write(0, 4, 'variant 3')
    worksheet.write(0, 5, 'variant 4')
    worksheet.write(0, 6, 'dialogue act')
    for tweet in list_of_tweets:
            text = tweet.get_text()
            tweet_text = re.split('user=', text)[1]
            tweet_text = tweet_text.partition(' ')[2]
            if tweet_text != '':
                worksheet.write(row, col, text)
                row += 1
                tokens = tweet.get_tags_full()
                for offset, tags_list in tokens.iteritems():
                    word = tweet.get_word(offset)
                    if len(tags_list) == 1:
                        for tag_name, value in tags_list.iteritems():
                            worksheet.write(row, col, offset)
                            worksheet.write(row, col+1, word)
                            worksheet.write(row, col+6, tag_name)
                    else:
                        data = list()
                        data.append(offset)
                        data.append(word)
                        for tag_name, value in tags_list.iteritems():
                            data.append(tag_name)
                        number_of_tags = len(data)
                        for i in range(0, number_of_tags, 1):
                            worksheet.write(row, col + i, data[i])
                    row += 1
                row += 1
            else:
                print tweet.get_text()
    workbook.close()


def write_to_xlsx_file_final(list_of_tweets, file_name):
    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()
    row = 1
    col = 0
    worksheet.write(0, 0, 'offset')
    worksheet.write(0, 1, 'token')
    worksheet.write(0, 2, 'dialogue act')
    for tweet in list_of_tweets:
        text = tweet.get_text()
        worksheet.write(row, col, text)
        row += 1
        tokens = tweet.get_tokens()
        for i in range(4, len(tokens) + 4, 1):
            token_da = tokens[str(i)]
            for token, da in token_da.iteritems():
                worksheet.write(row, col, str(i))
                worksheet.write(row, col+1, token)
                worksheet.write(row, col+2, da)
                row += 1
        row += 1
    workbook.close()


def write_to_xls_pure_annotation(list_of_tweet_tuple, file_name):
    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()
    row = 1
    col = 0
    worksheet.write(0, 0, 'offset')
    worksheet.write(0, 1, 'token')
    worksheet.write(0, 2, 'dialogue act')
    conversation_id = 0
    for tweet in list_of_tweet_tuple:
        text_id = tweet[0]
        if text_id == 0:
            conversation_id += 1
            line = 'conversation_id=' + str(conversation_id)
            worksheet.write(row, col, line)
            row += 1
        tweet_id = tweet[1]
        tweet_text = tweet[2]
        in_replay_to = tweet[4]
        da_segments = tweet[3]
        original_annotation = tweet[5]
        line = '#text=' + str(text_id) + ' #tweet_id=' + str(tweet_id) + ' #in_replay_to=' + str(in_replay_to) \
               + ' #tweet_text=' + tweet_text
        line = unicode(line, 'utf-8')
        worksheet.write(row, col, line)
        row += 1
        tokens = str(tweet_text).split(' ')
        for i in range(4, len(tokens) + 4, 1):
            # annotations = original_annotation.copy()
            token_da = tokens[i-4]
            token_da = unicode(token_da, 'utf-8')
            worksheet.write(row, col, str(i))
            worksheet.write(row, col+1, token_da)
            da = find_da_for_token(da_segments, i)
            worksheet.write(row, col+2, da)
            for annotation in original_annotation:
                original_da = annotation[str(i)][1]
                worksheet.write(row, col+3, original_da)
                col += 1
            col = 0
            row += 1
        row += 1
    workbook.close()


def find_da_for_token(segments_da, token_offset):
    for segment in segments_da:
        offsets = segment[0]
        start_offset = int(offsets.split(':')[0])
        end_offset = int(offsets.split(':')[1])
        if token_offset >= start_offset and token_offset <= end_offset:
            return segment[1]


def find_children_annotations(parent_tweet_id, conversation_tree, list_of_tweet_tuples, previous_text_id, mongo_collection):
    children = conversation_tree.children(parent_tweet_id)
    for child in children:
        tweet_id = child.tag
        tweet_text = postgres_queries.find_tweet_text(tweet_id)[0]
        tweet_segments_da = postgres_queries.find_segments(tweet_id)
        text_id = previous_text_id + 1
        annotations = mongoDBQueries.find_by_id(mongo_collection, str(tweet_id))
        original_annotation = list(annotations[:])
        tweet_tuple = (text_id, tweet_id, tweet_text, tweet_segments_da, parent_tweet_id, original_annotation)
        list_of_tweet_tuples.append(tweet_tuple)
        find_children_annotations(tweet_id, conversation_tree, list_of_tweet_tuples, text_id, mongo_collection)


def pure_annotation():
    tweet_id_list, list_of_conversations = rebuild_conversations.conversation_regarding_language() # list of Trees
    list_of_tweet_tuples = list()
    collection_annotated_data = mongoDB_configuration.get_collection('DARecognition', 'annotatedTwitterData')
    for conversation in list_of_conversations:
        tweet_id = conversation.root
        if tweet_id is not None:
            tweet_segments_da = postgres_queries.find_segments(tweet_id)
            tweet_text = postgres_queries.find_tweet_text(tweet_id)[0]
            text_id = 0
            #here mongodb
            annotations = mongoDBQueries.find_by_id(collection_annotated_data, str(tweet_id))
            original_annotation = list(annotations[:])
            tweet_tuple = (text_id, tweet_id, tweet_text, tweet_segments_da, None, original_annotation)# in_replay_to
            list_of_tweet_tuples.append(tweet_tuple)
            find_children_annotations(tweet_id, conversation, list_of_tweet_tuples, text_id, collection_annotated_data)
    return list_of_tweet_tuples

#
# list_of_conversation = pure_annotation()
# write_to_xls_pure_annotation(list_of_conversation, '../output/annotated.xlsx')