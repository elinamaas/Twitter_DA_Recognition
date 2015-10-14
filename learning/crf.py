import pycrfsuite
from postgres import postgres_queries, update_table
__author__ = 'snownettle'


def run_crf(train_set, test_set, taxonomy, cursor, connection):
    da_id_taxonomy = find_da_id(taxonomy, cursor)
    X_train, y_train = train_crf(train_set, taxonomy)
    X_test = [conversation2branch(conversation, taxonomy) for conversation in test_set]
    trainer = pycrfsuite.Trainer(verbose=False)
    for i in range(len(X_train)):
        X_conversation = X_train[i]
        y_conversation = y_train[i]
        for j in range(len(X_conversation)):
            X_branch = X_conversation[j]
            y_branch = y_conversation[j]
            for xseq, yseq in zip(X_branch, y_branch):
                a = [xseq]
                b = [yseq]
                trainer.append(a, b)
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
    recognized_segments_da = ()
    for i in range(len(X_test)):
        for j in range(len(X_test[i])):
            for k in range(len(X_test[i][j])):
                feature = [X_test[i][j][k]]
                da = tagger.tag(feature)[0]
                segment = test_set[i][j].branch[k]
                recognized_segments_da = recognized_da_segments(recognized_segments_da, da, da_id_taxonomy, segment)
    update_table.update_da_prediction_bulk(recognized_segments_da, taxonomy, cursor, connection)


def recognized_da_segments(recognized_segments_da, dialog_act_name, da_id_taxonomy, segment):
    da_id = da_id_taxonomy[dialog_act_name]
    tuple_da_segment = (da_id, segment.tweet_id, segment.start_offset, segment.end_offset)
    recognized_segments_da = recognized_segments_da + (tuple_da_segment,)
    return recognized_segments_da


def train_crf(train_set, taxonomy):
    X_train = list()
    y_train = list()
    for i in range(len(train_set)):
        X_conversation = list()
        y_conversation = list()
        for j in range(len(train_set[i])): #branch
            X_branch = list()
            y_branch = list()
            for k in range(len(train_set[i][j].branch)): # segmetns
                features = segment2features(train_set[i][j], k, taxonomy)
                da = train_set[i][j].branch[k].get_da_by_taxonomy(taxonomy)
                X_branch.append(features)
                y_branch.append(da)
            X_conversation.append(X_branch)
            y_conversation.append(y_branch)
        X_train.append(X_conversation)
        y_train.append(y_conversation)
    return X_train, y_train


def segment2features(branch, i, taxonomy):
    segments = branch.branch
    segment = segments[i]
    feature = segment.features
    if taxonomy == 'full':
        language_features = feature.language_features_full
    elif taxonomy == 'reduced':
        language_features = feature.language_features_reduced
    else:
        language_features = feature.language_features_minimal
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
        'imperative=%s' % feature.features['imperative'] #,
        # 'embeddings=%s' % feature.word2vec,
        # 'lang_features=%s' % language_features
    ]
    if i > 0:
        segment1 = segments[i-1]
        feature1 = segment1.features
        features.extend([
            '-1length=%s' % feature1.features['length'],
            '-1pos=%s' % feature1.features['pos'],
            '-1root_user=%s' % feature1.features['root_user'],
            '-1link=%s' % feature1.features['link'],
            '-1question_mark=%s' % feature1.features['question_mark'],
            '-1exclamation_mark=%s' % feature1.features['exclamation_mark'],
            '-1hashtag=%s' % feature1.features['hashtag'],
            '-1emoticons=%s' % feature1.features['emoticons'],
            '-1question_words=%s' % feature1.features['question_words'],
            '-1first_verb=%s' % feature1.features['first_verb'],
            '-1imperative=%s' % feature1.features['imperative'] #,
            # '-1embeddings=%s' % feature1.word2vec,
            # 'lang_features=%s' % language_features
        ])
    else:
        features.append('BB')
    if i < len(segments)-1:
        segment1 = segments[i+1]
        feature1 = segment1.features
        features.extend([
            '+1length=%s' % feature1.features['length'],
            '+1pos=%s' % feature1.features['pos'],
            '+1root_user=%s' % feature1.features['root_user'],
            '+1link=%s' % feature1.features['link'],
            '+1question_mark=%s' % feature1.features['question_mark'],
            '+1exclamation_mark=%s' % feature1.features['exclamation_mark'],
            '+1hashtag=%s' % feature1.features['hashtag'],
            '+1emoticons=%s' % feature1.features['emoticons'],
            '+1question_words=%s' % feature1.features['question_words'],
            '+1first_verb=%s' % feature1.features['first_verb'],
            '+1imperative=%s' % feature1.features['imperative']#,
            # '+1embeddings=%s' % feature1.word2vec,
            # 'lang_features=%s' % language_features
        ])
    else:
        features.append('EB')

    return features


def branch2features(branch, taxonomy):
    return [segment2features(branch, i, taxonomy) for i in range(len(branch.branch))]


def conversation2branch(conversation, taxonomy):
    return [branch2features(branch, taxonomy) for branch in conversation]


def find_da_id(taxonomy, cursor):
    results = postgres_queries.get_all_da(taxonomy, cursor)
    da_id_dict = dict()
    for result in results:
        da_id_dict[result[1]] = result[0]
    return da_id_dict
