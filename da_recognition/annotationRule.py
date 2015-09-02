__author__ = 'snownettle'
from postgres import postgres_queries, update_table
from analysing_GS import emoticons, question_words


def assign_zero_da(taxonomy, cursor, connection):
    # @username or some symbols
    records = postgres_queries.find_all_records('segments_utterance', cursor)
    for record in records:
        tweet_id = str(record[0])
        start_offset = record[1]
        end_offset = record[2]
        utterance = record[3]
        if utterance.startswith('@') or start_offset - end_offset == 0:
            da_name = '0'
            postgres_queries.update_da_prediction(da_name, tweet_id, start_offset, end_offset,
                                                  taxonomy, cursor, connection)



def assign_social_da(taxonomy, cursor, connection):
    #
    emoticons_list = emoticons.emoticons_lib()
    records = postgres_queries.find_all_records('segments_utterance', cursor)
    for record in records:
        tweet_id = str(record[0])
        start_offset = record[1]
        end_offset = record[2]
        utterance = record[3]
        utterance = utterance.lower()
        if [e for e in emoticons_list if e in utterance] and end_offset - start_offset < 2 and 'http' not in utterance \
                or 'danke' in utterance:
            da_name = 'SOCIAL'
            postgres_queries.update_da_prediction(da_name, tweet_id, start_offset, end_offset,
                                                  taxonomy, cursor, connection)


def assign_it_is_da(taxonomy, cursor, connection):
    #
    # q_words = question_words.german_question_words()
    records = postgres_queries.find_all_records('segments_utterance', cursor)
    for record in records:
        tweet_id = str(record[0])
        start_offset = record[1]
        end_offset = record[2]
        utterance = record[3]
        # if [e for e in q_words if e in utterance] or '?' in utterance:
        if '?' in utterance:
            # if taxonomy != 'full':
            da_name = 'IT_IS'
            postgres_queries.update_da_prediction(da_name, tweet_id, start_offset, end_offset,
                                                  taxonomy, cursor, connection)


def assign_choice_q_da(taxonomy, cursor, connection):
    records = postgres_queries.find_all_records('segments_utterance', cursor)
    for record in records:
        tweet_id = str(record[0])
        start_offset = record[1]
        end_offset = record[2]
        utterance = record[3]
        # if [e for e in q_words if e in utterance] or '?' in utterance:
        if '?' in utterance and 'oder' in utterance:
            # if taxonomy != 'full':
            da_name = 'IT_IS_Q_ChoiceQuestion'
            postgres_queries.update_da_prediction(da_name, tweet_id, start_offset, end_offset,
                                                  taxonomy, cursor, connection)
