__author__ = 'snownettle'
# get first document form the collection
import mongoDB_configuration


def search_first_tweet(db_name, collection_name):
    tweets_collection = mongoDB_configuration.get_collection(db_name, collection_name)
    tweet = tweets_collection.find_one()
    print tweet


def check_lang(tweets_collection):
    print tweets_collection.find({'lang':'de'}).count()
    print tweets_collection.find({'lang':'en'}).count()


def search_root_tweets(collection):
    return collection.find({'in_reply_to_status_id': None})


def find_all(collection):
    return collection.find(timeout=False)


def find_by_id(collection, tweet_id):
    return collection.find({'tweet_id': tweet_id})


def find_all_conversation_id(collection):
    return collection.distinct('conversation_id')


def find_by_conversation_id(collection, conversation_id):
    return collection.find({'conversation_id': conversation_id}).sort('text_id', 1)


def find_by_id_raw(collection, tweet_id):
    return collection.find_one({'tweet_id': tweet_id})


def search_replays(collection, tweet_id):
    replays = collection.find({'in_reply_to_status_id': tweet_id})
    if replays.count() != 0:
        return replays
    else:
        return None


def check_tweets_amount(collectionName):
    return collectionName.count()
