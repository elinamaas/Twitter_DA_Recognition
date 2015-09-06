__author__ = 'snownettle'

from prepare_gold_standard import rebuild_conversations

def fold_splitter(cursor):
    # Break data set into 10 pieces: n/10, where n ist the number of conversations
    conversation_list = rebuild_conversations.build_conversation(cursor)
    conversation_number = len(conversation_list)
    datesets = dict() # dateset of 10 folders
    for i in range(0, 10, 1):
        if i != 9 and i != 0:
            conversation_index = range(i*conversation_number/10, (i+1)*conversation_number/10)
        elif i == 0:
            conversation_index = range(i, (i+1)*conversation_number/10)
        elif i == 9:
            conversation_index = range(i*conversation_number/10, conversation_number)
        one_fold = list()
        for index in conversation_index:
            one_fold.append(conversation_list[index])
        datesets[i] = one_fold
    return datesets


def train_test_sets(datesets, train_fold_number):
    # 9 dataset for train, 1 for test
    test_dataset = datesets[train_fold_number]
    train_set_index = range(0, 10)
    train_set_index.remove(train_fold_number)
    train_dataset = list()
    for index in train_set_index:
        train_dataset += datesets[index]
    return train_dataset, test_dataset


