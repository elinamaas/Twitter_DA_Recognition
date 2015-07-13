__author__ = 'snownettle'
# calculate ICA for those tweets where we have the same segmentation, segments wise!
from math import factorial as fac
from math import pow
import collections
import itertools
from collections import defaultdict

import xlsxwriter
import numpy as np

from da_recognition import dialogue_acts_taxonomy


def chance_corrected_coefficient_categories(list_of_tweets, ontology): #overall_observed_agreement
    sum_arg_category = 0
    i = 0 #number_of segments
    number_of_assignments_to_category = dict() # nk
    seg_confusion_matrix = collections.defaultdict(list)
    for tweet in list_of_tweets:
        sum_arg_category, i, seg_confusion_matrix = tag_pro_segments_agreement(tweet, sum_arg_category, i,
                                                                number_of_assignments_to_category, seg_confusion_matrix)
    overall_observed_agreement = sum_arg_category/float(i)
    expected_agreement = ea(number_of_assignments_to_category, i)
    ccc = (overall_observed_agreement - expected_agreement)/float(1 - expected_agreement)
    confusion_matrix(seg_confusion_matrix, ontology)
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print 'Inter annotater agreement for dialogue acts:' + '\n'
    # print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print 'Overall observed agreement: ' + str(overall_observed_agreement)
    print 'Expected agreement:' + str(expected_agreement)
    print 'Chance-corrected coefficients: ' + str(ccc)


def ea(number_of_assignments_to_category, i): # calculate expected agreement
    expected_agreement = 0
    for tag, agreement in number_of_assignments_to_category.iteritems():
        p_k = agreement/float(i*3)
        expected_agreement += pow(p_k, 2)
    return expected_agreement


def binomial(x, y):
    try:
        binom = fac(x) // fac(y) // fac(x - y)
    except ValueError:
        binom = 0
    return binom


def tag_pro_segments_agreement(tweet, sum_arg, i, number_of_assignments_to_category, seg_confusion_matrix):
    segments = tweet.get_source_segmentation() #set()
    tokens = tweet.get_tags_full()
    for segment in segments:
        start_offset = int(segment.split(':')[0])
        tags_variations = tokens[start_offset]
        i += 1
        sum_n_ik = 0
        for tag, agreement in tags_variations.iteritems():
            n_ik = agreement  # stand for the number of times an item i is classified in categoty k
            binomial_n_ik = binomial(n_ik, 2)
            sum_n_ik += binomial_n_ik
            tags_agreement_con_matrix = dict()
            tags_agreement_con_matrix[tag] = agreement
            seg_confusion_matrix[i].append(tags_agreement_con_matrix)
            if tag in number_of_assignments_to_category:
                number_of_assignments_to_category[tag] += agreement
            else:
                number_of_assignments_to_category[tag] = agreement
        arg_i = sum_n_ik/float(binomial(3, 2))
        sum_arg += arg_i
    return sum_arg, i, seg_confusion_matrix


def confusion_matrix(segmentation_agreement, ontology):
    segments_list = []
    da_list = []
    segments_list.extend(range(1, len(segmentation_agreement) + 1, 1))
    da_tree = dialogue_acts_taxonomy.build_da_taxonomy_full()
    nodes = da_tree.all_nodes()
    matrix_tuple = list()
    for node in nodes:
        da_list.append(node.tag)
    da_list = sorted(da_list)
    da_list.insert(0, "_segments")
    tuple_zero = list()
    for i in range(0, 58, 1):
        tuple_zero.append(0)
    for segment, agreements in segmentation_agreement.iteritems(): # check if sorted!
        current_tuple = list(tuple_zero)
        current_tuple[0] = segment
        for tag_agreement in agreements:
            for tag, agreement in tag_agreement.iteritems():
                i = da_list.index(tag)
                current_tuple[i] = agreement
                # matrix_tuple = MatrixTuple
        matrix_tuple.append(current_tuple)
    write_to_file(matrix_tuple, da_list, '../DATA/confusion_matrix_' +ontology + '.xlsx')
    error_matrix = make_error_matrix(matrix_tuple, da_list)
    i = 1
    for error_line in error_matrix:
        error_line.insert(0, da_list[i])
        i += 1
    write_to_file(error_matrix, da_list, '../DATA/error_matrix_' + ontology + '.xlsx')


def make_error_matrix(matrix_tuple, da_list):
    error_matrix = list()
    tuple_zero = list()
    # errors = list()
    for i in range(0, 57, 1):
        tuple_zero.append(0)
    for i in range(0, 57, 1):
        error_matrix.append(list(tuple_zero))
    for tuple_old in matrix_tuple:
        if len(tuple_old) == 58:
            del tuple_old[0]
        values = np.array(tuple_old)
        error_index = np.where(values != 0)
        error_pairs = itertools.permutations(error_index[0], 2)
        for error in error_pairs:
            error_matrix[error[0]][error[1]] += 1
    return error_matrix


def write_to_file(matrix_tuple, da_list, file_name):
    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()
    row = 0
    col = 0
    worksheet.write_row(row, 0, da_list)
    # worksheet.write_row()
    row = 1
    for tuple in matrix_tuple:
        worksheet.write_row(row, 0,  tuple)
        row += 1
    workbook.close()


def make_list_for_three_annotators(all_tweets, list_with_three):
    list_with_three = list(list_with_three)
    new_tweet_list = list()
    for tweet in all_tweets:
        tweet_id = long(tweet.get_tweet_id())
        if tweet_id in list_with_three:
            new_tweet_list.append(tweet)
    return new_tweet_list


def chance_corrected_coefficient_labels(all_tweets, list_with_three): #overall_observed_agreement
    list_of_tweets = make_list_for_three_annotators(all_tweets, list_with_three)
    j = 0 # number of tokens
    sum_arg_segmentation = 0
    dict_ea = dict()
    dict_ea['B'] = 0
    dict_ea['I'] = 0
    for tweet in list_of_tweets:
        sum_arg_segmentation, j = token_label_agreement(tweet, sum_arg_segmentation, j, dict_ea)
    arg = sum_arg_segmentation/float(binomial(3, 2))

    overall_observed_agreement = arg/float(j)
    expected_agreement = ea(dict_ea, j)
    ccc = (overall_observed_agreement - expected_agreement)/float(1 - expected_agreement)
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print 'Inter annotater agreement for segmentation:' + '\n'
    # print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print 'Overall observed agreement: ' + str(overall_observed_agreement)
    print 'Expected agreement:' + str(expected_agreement)
    print 'Chance-corrected coefficients: ' + str(ccc)


def token_label_agreement(tweet, sum_arg_segmentation, j, dict_ea):
    segments = tweet.get_segmentation()
    tokens = tweet.get_tags_full()
    end_offset = 4 + len(tokens)
    # for i in_ range(4, end_offset, 1):
    tokens_dict = defaultdict(list)
    tweet_offset = list()
    j += len(tokens)
    for offsets, count in segments.iteritems():
        #j += 1
        start_offset = int(offsets.split(':')[0])
        end_offset = int(offsets.split(':')[1])
        tweet_offset = list()
        tweet_offset.extend(range(start_offset + 1, end_offset + 1, 1))
        labels_dict = dict()
        labels_dict['B'] = count
        dict_ea['B'] += count
        if start_offset in tokens_dict:
            existing_label = tokens_dict[start_offset]
            if len(existing_label) == 1:
                if 'B' in existing_label[0]:
                    existing_label[0]['B'] += count
                else:
                    tokens_dict[offset].append(labels_dict.copy())
            elif len(existing_label) == 2:
                for label_count in existing_label:
                    if 'B' in label_count:
                        label_count['B'] += count
            # if 'B' in existing_label[0] or 'B' in existing_label[0]:
            #     for label_count in existing_label:
            #         if 'B' in label_count:
            #             label_count['B'] += count
            else:
                tokens_dict[start_offset].append(labels_dict.copy())
        else:
            tokens_dict[start_offset].append(labels_dict.copy())
        labels_dict = dict()
        labels_dict['I'] = count
        for offset in tweet_offset:
            dict_ea['I'] += count
            if offset in tokens_dict:
                existing_label = tokens_dict[offset]
                if len(existing_label) == 1:
                    if 'I' in existing_label[0]:
                        existing_label[0]['I'] += count
                    else:
                        tokens_dict[offset].append(labels_dict.copy())
                elif len(existing_label) == 2:
                    for label_count in existing_label:
                        if 'I' in label_count:
                            label_count['I'] += count
                else:
                    tokens_dict[offset].append(labels_dict.copy())
            else:
                tokens_dict[offset].append(labels_dict.copy())
    sum_arg_segmentation = labels_sum_agreement(sum_arg_segmentation, tokens_dict)
    return sum_arg_segmentation, j


def labels_sum_agreement(sum_arg_segmentation, tokens_dict):
    for offsets, labels_dict in tokens_dict.iteritems():
        for label in labels_dict:
            for l, count in label.iteritems():
                agreemnt = binomial(count, 2)
                sum_arg_segmentation += agreemnt
    return sum_arg_segmentation