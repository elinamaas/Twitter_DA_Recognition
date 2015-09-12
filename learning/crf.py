import pycrfsuite
from itertools import chain
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelBinarizer
from postgres import postgres_queries
from feature import Feature
from analysing_GS.extract_features import extract_language_features
__author__ = 'snownettle'


def run_crf(train_set, test_set, taxonomy, cursor, connection):
    tokens = extract_language_features(train_set, taxonomy, cursor)

    train_data, train_branches = extract_data(train_set, tokens, taxonomy, cursor)
    X_train = [utterance2features(s, tokens) for s in train_data]
    y_train = [utterance2labels(s) for s in train_data]
    test_data, test_branches = extract_data(test_set, tokens, taxonomy, cursor)
    X_test = [utterance2features(s, tokens) for s in test_data]
    y_test = [utterance2labels(s) for s in test_data]
    trainer = pycrfsuite.Trainer(verbose=False)
    for xseq, yseq in zip(X_train, y_train):
        trainer.append(xseq, yseq)
    trainer.set_params({
        'c1': 1.0,   # coefficient for L1 penalty
        'c2': 1e-3,  # coefficient for L2 penalty
        'max_iterations': 50,  # stop earlier

        # include transitions that are possible, but not observed
        'feature.possible_transitions': True
    })
    trainer.params()
    trainer.train('conll2002-esp.crfsuite')
    tagger = pycrfsuite.Tagger()
    tagger.open('conll2002-esp.crfsuite')
    y_pred = [tagger.tag(xseq)[0] for xseq in X_test]
    i = 0
    for branch in test_branches:
        for segment in branch:
            dialog_act_name = y_pred[i]
            tweet_id = str(segment[0])
            start_offset = int(segment[1])
            end_offset = int(segment[2])
            postgres_queries.update_da_prediction(dialog_act_name, tweet_id, start_offset, end_offset,
                                                  taxonomy, cursor, connection)

            i += 1
    # y_test_test = list()
    # for a in y_test:
    #     y_test_test.append(a[0])
    # print(bio_classification_report(y_test_test, y_pred))


def extract_data(train_set, tokens, taxonomy, cursor): # tuple (utterance, user, pos,  DA_id)
    train_data_tuples = list()
    conversation_pathes_tweet_id = list()
    for conversation in train_set:
        root = conversation.root
        root_username = postgres_queries.find_username_by_tweet_id(root, cursor)
        all_conversation_branches = conversation.paths_to_leaves()
        for branch in all_conversation_branches:
            conversation_path_tweet_id = list()
            for tweet_id in branch:
                segments = postgres_queries.find_segments_utterance(tweet_id, taxonomy, cursor)
                current_username = postgres_queries.find_username_by_tweet_id(tweet_id, cursor)
                for i in range(0, len(segments), 1):
                    segment = segments[i]
                    if i == 0:
                        pos = True
                    else:
                        pos = False
                    start_offset = segment[0]
                    end_offset = segment[1]
                    utterance = segment[2]
                    da = segment[3]
                    utterance_tuple = (utterance, start_offset, end_offset, root_username, current_username, pos, da,
                                       tokens)
                    train_data_tuples.append(utterance_tuple)
                    conversation_path_tweet_id.append([tweet_id, start_offset, end_offset])
            conversation_pathes_tweet_id.append(conversation_path_tweet_id)
    return train_data_tuples, conversation_pathes_tweet_id


def word2features(utterance, tokens):
    utterance_string = utterance[0]
    start_offset = utterance[1]
    end_offset = utterance[2]
    root_user = utterance[3]
    current_user = utterance[4]
    pos = utterance[5]
    feature = Feature(utterance_string, start_offset, end_offset, root_user, current_user, pos, tokens)
    features = [
        'length=%s' % feature.features['length'],
        'pos=%s' % feature.features['pos'],
        'root_user=%s' % feature.features['root_user'],
        'link=%s' % feature.features['link'],
        'question_mark=%s' % feature.features['question_mark'],
        'exclamation_mark=%s' % feature.features['exclamation_mark'],
        'hashtag=%s' % feature.features['hashtag'],
        'emoticons=%s' % feature.features['emoticons'],
        'question_words=%s' % feature.features['question_words'],
        'first_verb=%s' % feature.features['first_verb'],
        'lang_features=%s' % feature.features['language_features']
    ]

    return features


def utterance2features(utterance, tokens):
    return [word2features(utterance, tokens)]


def utterance2labels(sent):
    return [sent[6]]


def utterance2tokens(sent):
    return [sent[0]]


# def bio_classification_report(y_true, y_pred):
#     """
#     Classification report for a list of BIO-encoded sequences.
#     It computes token-level metrics and discards "O" labels.
#
#     Note that it requires scikit-learn 0.15+ (or a version from github master)
#     to calculate averages properly!
#     """
#     lb = LabelBinarizer()
#     y_true_combined = lb.fit_transform(list(chain.from_iterable(y_true)))
#     y_pred_combined = lb.transform(list(chain.from_iterable(y_pred)))
#
#     tagset = set(lb.classes_) - {'O'}
#     tagset = sorted(tagset, key=lambda tag: tag.split('-', 1)[::-1])
#     class_indices = {cls: idx for idx, cls in enumerate(lb.classes_)}
#
#     return classification_report(
#         y_true_combined,
#         y_pred_combined,
#         labels = [class_indices[cls] for cls in tagset],
#         target_names = tagset,
#     )

