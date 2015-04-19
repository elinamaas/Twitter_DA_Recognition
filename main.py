__author__ = 'snownettle'
from readData import rawTwitterData, annotatedData_read
from mongoDB import mongoDB_configuration, importTwitterConversation, queries
from annotatedData.annotated_tweets_final import editing_annotated_tweets
from annotatedData import rebuild_conversations
from postgres import insert_to_table, postgres_queries


database = 'DARecognition'
#
# # make all connection to db here
collectionRawTwitterData = mongoDB_configuration.get_collection(database, 'rawTwitterData')
collectionAnnotatedData = mongoDB_configuration.get_collection(database, 'annotatedTwitterData')
rawTwitterConversation_path = 'DATA/twitterConversation'
annotatedData_path = 'DATA/annotationed/webanno-projectexport/annotation'
annotatedDataRAW_path = 'DATA/annotated_tweets_raw.txt'

if mongoDB_configuration.check_tweets_amount(collectionRawTwitterData) == 0:
    #  Import raw twitter_objects conversation in DB
    rawTwitterData.import_raw_twitter_data(rawTwitterConversation_path, collectionRawTwitterData)

else:
    print 'Collection ' + collectionRawTwitterData.name + ' is already existed'

amountOfRawTweets = queries.check_tweets_amount(collectionRawTwitterData)
print 'There are ',  amountOfRawTweets, ' raw tweets in DB.'


if mongoDB_configuration.check_tweets_amount(collectionAnnotatedData) == 0:
    annotatedData_read.read_annotated_docs(annotatedData_path, collectionAnnotatedData)
else:
    print 'Collection ' + collectionAnnotatedData.name + ' is already existed'
amountOdAnnotatedTweets = mongoDB_configuration.check_tweets_amount(collectionAnnotatedData)

editing_annotated_tweets(collectionAnnotatedData)


############# Postgres ###############

# import 10GB tweets move to top, so only once we read the txt
# rawTwitterData.import_to_postgres(rawTwitterConversation_path)

# DA Taxonomy
insert_to_table.insert_dialogue_act_names()
# Insert annotated tweets: tweet id, text, replays, lang
rebuild_conversations.insert_annotated_tweets_postgres(annotatedData_path)

annotatedData_read.concatenate_done_tweets()
# rebuild_conversations.insert_annotated_tweets(tweets_id)

# postgres_queries.find_not_german_tweets()

