__author__ = 'snownettle'

from prepare_gold_standard import rebuild_conversations
from postgres import postgres_queries
from conversation_branches import Segment, Branch


def fold_splitter(cursor, embeddings, word_id):
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
            # braches
            # build_branches(conversation_list[index], cursor)
            one_fold.append(build_branches(conversation_list[index], cursor, embeddings, word_id))
        datesets[i] = one_fold
    return datesets


def build_branches(conversation, cursor, embeddings, word_id):
    branches = conversation.paths_to_leaves()
    branch_list = list()
    root = conversation.root
    root_user_name = postgres_queries.find_username_by_tweet_id(root, cursor)
    for branch in branches:
        start_branch = True
        segments_branch = Branch()
        for tweet in branch:
            username = postgres_queries.find_username_by_tweet_id(tweet, cursor)
            segments = postgres_queries.find_segments(tweet, cursor)
            for i in range(0, len(segments), 1):
                segment = segments[i]
                #root
                s = Segment(username, root_user_name, segment, tweet, i, embeddings, word_id)
                if start_branch is True:
                    segments_branch.add_start_segment(s)
                else:
                    segments_branch.add_segment(s)
                start_branch = False
        branch_list.append(segments_branch)
    return branch_list


def train_test_sets(datesets, train_fold_number):
    # 9 dataset for train, 1 for test
    test_dataset = datesets[train_fold_number]
    train_set_index = range(0, 10)
    train_set_index.remove(train_fold_number)
    train_dataset = list()
    for index in train_set_index:
        train_dataset += datesets[index]
    return train_dataset, test_dataset


