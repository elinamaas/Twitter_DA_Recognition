__author__ = 'snownettle'
from postgres import postgres_queries, postgres_configuration
from tabulate import tabulate
from operator import itemgetter
import math
import nltk


def evaluation_taxonomy_da(taxonomy_name, cursor):
    da_names = postgres_queries.find_states(taxonomy_name, cursor)
    evaluation_data = list()
    for da_name in da_names:
        # relevant_docs = len(postgres_queries.find_all_da_occurances_taxonomy('segmentation',
        #                                                                              da_name, taxonomy_name, cursor))
        tp, fp, fn, tn = find_tp_fp_tn_fn(taxonomy_name, da_name, cursor)
        # print da_name + '\t' + str(tp + fp) + '\t' + str(tp)
        precision = calculate_precision(tp, fp)
        recall = calculate_recall(tp, fn)
        true_negative_rate = calculate_tn_rate(tn, fp)
        accuracy = calculate_accuracy(tp, tn, fp, fn)
        f_measure = calculate_f_measure(precision, recall)
        da_evaluation = [da_name, precision, recall, true_negative_rate, accuracy,  f_measure, tp, fp, fn, tn]
        evaluation_data.append(da_evaluation)
    evaluation_data = sorted(evaluation_data, key=itemgetter(0))
    evaluation_dict = put_in_dict(evaluation_data)
    print_evaluation(taxonomy_name, evaluation_data, evaluation_dict)


def put_in_dict(evaluation_data):
    evaluation_dict = dict()
    for row in evaluation_data:
        evaluation_dict[row[0]] = {'precision': row[1], 'recall': row[2], 'tn_rate':row[3], 'accuracy': row[4],
                                   'f1': row[5], 'tp': row[6], 'fp': row[7], 'fn': row[8], 'tn': row[9]}
    return evaluation_dict


def find_tp_fp_tn_fn(taxonomy, da_name, cursor):
    tp = 0
    fp = 0
    relevant_docs = postgres_queries.find_all_da_occurances_taxonomy('Segmentation', da_name, taxonomy, cursor)
    records = postgres_queries.find_all_da_occurances_taxonomy('Segmentation_Prediction', da_name, taxonomy, cursor)
    all_segments = postgres_queries.find_all_records('Segmentation_Prediction', cursor)
    for record in records:
        tweet_id = record[0]
        start_offset = record[1]
        end_offset = record[2]
        da = record[3]
        da_gs = postgres_queries.find_da_for_segment(tweet_id, start_offset, end_offset, taxonomy, cursor)
        # relevant_docs += len(da_gs)
        if da == da_gs:
            tp += 1
        else:
            fp += 1
    fn = len(relevant_docs) - tp
    tn = len(all_segments) - tp - fp - fn
    # print fn, tn
    return tp, fp, fn, tn


def calculate_tn_rate(tn, fp):
    if (tn + fp) == 0:
        return 0
    else:
        return tn/float(tn+fp)


def calculate_accuracy(tp, tn, fp, fn):
    if (tp+tn+fp+fn)==0:
        return 0
    else:
        return (tp+tn)/float(tp+tn+fp+fn)


def calculate_precision(tp, fp):
    if (tp+fp) == 0:
        return 0
    else:
        precision_value = tp/float(tp+fp)
        return precision_value


def calculate_recall(tp, fn):
    if (tp+fn) == 0:
        return 0
    else:
        recall_value = tp/float(tp+fn)
        return recall_value


def calculate_f_measure(precision, recall):
    if (recall + precision) ==0:
        return 0
    else:
        f_measure_value = 2*recall*precision/float(recall + precision)
        return f_measure_value


def print_evaluation(taxonomy, evaluation_data, evaluation_dict):
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print 'Evaluation for ' + taxonomy + ' taxonomy'
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print tabulate(evaluation_data, headers=['dialogue act name', 'precision', 'recall', 'True negative Rate',
                                             'Accuracy', 'F-measure', 'True Positive', 'False Positive',
                                             'False Negative', 'True Negative']) # delete accuracy
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print 'Overall evaluation for ' + taxonomy + ' taxonomy'
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    evaluation_data_micro_macro = overall_evaluation(evaluation_dict)
    print tabulate(evaluation_data_micro_macro, headers=[' ', 'precision', 'recall', 'True negative Rate', 'Accuracy',
                                                         'F-measure',]) #


def overall_evaluation(evaluation_dict):
    evaluation_data = list()
    recall = 0
    precision = 0
    tp = 0
    fp = 0
    rd = 0
    tn_rate = 0
    accurcy = 0
    for da, values in evaluation_dict.iteritems():
        if da != '0':
            recall_da = values['recall'] * (values['tp'] + values['fn'])
            recall += recall_da
            # recall += values['recall']
            precision_da = values['precision'] * (values['tp'] + values['fn'])
            precision += precision_da
            tn_rate_da = values['tn_rate'] * (values['tp'] + values['fn'])
            tn_rate += tn_rate_da
            accuracy_da = values['accuracy'] * (values['tp'] + values['fn'])
            accurcy += accuracy_da
            # precision += values['precision']
            tp += values['tp']
            fp += values['fp']
            rd += values['tp'] + values['fn']

    classification_numbers = len(evaluation_dict.values())
    # average_pr = precision/float(classification_numbers)
    average_pr = precision/float(rd)
    # average_re = recall/float(classification_numbers)
    average_re = recall/float(rd)
    average_tn_rate = tn_rate/float(rd)
    average_accuracy = accurcy/float(rd)
    average_f1 = 2*average_pr*average_re/float(average_pr+average_re)
    da_evaluation = ['Macro-average Method', average_pr, average_re, average_tn_rate, average_accuracy, average_f1]
    evaluation_data.append(da_evaluation)
    print 'Accuracy:' + str(tp/float(rd))
    # micro_pr = tp/float(tp+fp)
    # micro_re = tp/float(rd)
    # micro_f1 = 2*micro_pr*micro_re/float(micro_pr+micro_re)
    # da_evaluation = ['Micro-average Method', micro_pr, micro_re, micro_f1]
    # evaluation_data.append(da_evaluation)
    return evaluation_data


def inter_annotation_agreement(taxonomy, cursor):
    joined_tables = postgres_queries.join_tables(taxonomy, cursor)
    i_number = len(joined_tables)
    arg_i = 0
    sum_nc1k_nc2k = 0
    nc1k = dict() # gold standard
    nc2k = dict() # predictions
    sum_n_k_square = 0
    for result in joined_tables:
        if result[0] == result[1]:
            arg_i += 1
        if result[0] in nc1k:
            nc1k[result[0]] += 1
        else:
            nc1k[result[0]] = 1
            if result[0] not in nc2k:
                nc2k[result[0]] = 0
        if result[1] in nc2k:
            nc2k[result[1]] += 1
        else:
            nc2k[result[1]] = 1
    for da, value in nc1k.iteritems():
        sum_nc1k_nc2k += value * nc2k[da]
        sum_n_k_square += math.pow((value + nc2k[da]), 2)

    a_o = 1/float(i_number)*arg_i # observed agreement
    a_k_e = 1/float(math.pow(i_number, 2)) * sum_nc1k_nc2k
    k = (a_o - a_k_e)/float(1-a_k_e)
    a_pi_e = 1/4*float(math.pow(i_number, 2)) * sum_n_k_square
    pi = (a_o - a_pi_e)/float(1-a_pi_e)
    print 'Individual Coder Distribution k = ' + str(k)
    print 'A Single Distribution pi = ' + str(pi)


def confusion_matrix(taxonomy, cursor):
    gold = list()
    test = list()
    joined_tables = postgres_queries.join_tables(taxonomy, cursor)
    for result in joined_tables:
        if taxonomy == 'full':
            da_gold = postgres_queries.find_da_by_id(result[0], postgres_configuration.fullOntologyTable, cursor)
            da_test = postgres_queries.find_da_by_id(result[1], postgres_configuration.fullOntologyTable, cursor)
        elif taxonomy == 'reduced':
            da_gold = postgres_queries.find_da_by_id(result[0], postgres_configuration.reducedOntologyTable, cursor)
            da_test = postgres_queries.find_da_by_id(result[1], postgres_configuration.reducedOntologyTable, cursor)
        else:
            da_gold = postgres_queries.find_da_by_id(result[0], postgres_configuration.reducedOntologyTable, cursor)
            da_test = postgres_queries.find_da_by_id(result[1], postgres_configuration.reducedOntologyTable, cursor)
        gold.append(da_gold)
        test.append(da_test)
    cm = nltk.ConfusionMatrix(gold, test)
    print 'Confusion matrix'
    print(cm.pp(sort_by_count=True, show_percents=True))







