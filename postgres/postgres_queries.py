__author__ = 'snownettle'
import postgres_configuration


def find_annotated_conversation_number():
    connection, cursor = postgres_configuration.make_connection()
    query = 'select max(Conversation_id) from Tweet where Annotated = True'
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results[0][0]


def find_conversation(conversation_number):
    connection, cursor = postgres_configuration.make_connection()
    query = 'select * from Tweet where Conversation_id = ' + str(conversation_number)
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def find_conversations():
    converasation_number = find_annotated_conversation_number()
    conversation_list = list()
    for i in range(1, converasation_number +1, 1):
        conversation = find_conversation(i)
        conversation_list.append(conversation)
    return conversation_list


def find_conversations_root():
    connection, cursor = postgres_configuration.make_connection()
    query = 'select * from tweet where in_replay_to is null and annotated = True'
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def find_not_german_tweets():
    connection, cursor = postgres_configuration.make_connection()
    query = 'select tweet_id, tweet_text from tweet where german = False'
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    print 'There are ' + str(len(results)) + ' not german tweets'
    for result in results:
        print result
    return results


def find_das_for_tweet(tweet_id):
    connection, cursor = postgres_configuration.make_connection()
    query = 'select da.dialogue_act_name from segmentation as s, dialogue_act as da ' \
            'where s.tweet_id =' + str(tweet_id) + 'and s.dialogue_act_id = da.dialogue_act_id ' \
                                                   'group by s.dialogue_act_id, da.dialogue_act_name'

    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def find_da_unigrams():
    connection, cursor = postgres_configuration.make_connection()
    query = 'select count(s.dialogue_act_id), da.dialogue_act_name ' \
            'from segmentation as s, dialogue_act as da ' \
            'where s.dialogue_act_id = da.dialogue_act_id ' \
            'group by s.dialogue_act_id, da.dialogue_act_name ' \
            'order by count(s.dialogue_act_id) desc'
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results


def find_segments(tweet_id):
    connection, cursor = postgres_configuration.make_connection()
    query = 'select s.segmentation_offsets, da.dialogue_act_name from segmentation as s, dialogue_act as da ' \
            'where s.tweet_id =' + str(tweet_id) + 'and s.dialogue_act_id = da.dialogue_act_id ' \
                                              'group by da.dialogue_act_name, s.dialogue_act_id, s.segmentation_offsets'
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results
# select s.segmentation_offsets, da.dialogue_act_name from segmentation as s, dialogue_act as da
# where s.tweet_id = 406567743258120192 and s.dialogue_act_id = da.dialogue_act_id
# group by da.dialogue_act_name, s.dialogue_act_id, s.segmentation_offsets

def find_children(tweet_id):
    connection, cursor = postgres_configuration.make_connection()
    query = 'select * from tweet where in_replay_to =' + str(tweet_id) + 'and annotated = True'
    cursor.execute(query)
    results = cursor.fetchall()
    postgres_configuration.close_connection(connection)
    return results