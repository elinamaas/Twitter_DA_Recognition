__author__ = 'snownettle'
from postgres import postgres_queries
from da_recognition import dialogue_acts_taxonomy
from tabulate import tabulate
from operator import itemgetter


def evaluation_taxonomy_da(taxonomy_name, cursor):
    # taxonomy_tree = dialogue_acts_taxonomy.build_taxonomy(taxonomy_name)
    # da_names = taxonomy_tree.all_nodes()
    da_names = postgres_queries.find_states(taxonomy_name, cursor)
    evaluation_data = list()
    for da_name in da_names:
        # da_name = da.tag
        relevant_docs = len(postgres_queries.find_all_da_occurances_taxonomy('segmentation',
                                                                                     da_name, taxonomy_name, cursor))
        tp, fp = find_tp_fp(taxonomy_name, da_name, cursor)
        # print da_name + '\t' + str(tp + fp) + '\t' + str(tp)
        precision = calculate_precision(tp, fp)
        recall = calculate_recall(tp, relevant_docs)
        f_measure = calculate_f_measure(precision, recall)
        da_evaluation = [da_name, precision, recall, f_measure, tp, fp, relevant_docs]
        evaluation_data.append(da_evaluation)
    # header_data = ['dialogue act name', 'precision', 'recall', 'F-measure']
    evaluation_data = sorted(evaluation_data, key=itemgetter(0))
    print_evaluation(taxonomy_name, evaluation_data)


def find_tp_fp(taxonomy, da_name, cursor):
    tp = 0
    fp = 0
    records = postgres_queries.find_all_da_occurances_taxonomy('Segmentation_Prediction', da_name, taxonomy, cursor)
    for record in records:
        tweet_id = record[0]
        # segments_offset = record[1]
        start_offset = record[1]
        end_offset = record[2]
        da = record[3]
        da_gs = postgres_queries.find_da_for_segment(tweet_id, start_offset, end_offset, taxonomy, cursor)
        if da == da_gs:
            tp += 1
        else:
            fp += 1
    return tp, fp

def calculate_precision(tp, fp):
    if (tp+fp) == 0:
        return 0
    else:
        precision_value = tp/float(tp+fp)
        return precision_value

def calculate_recall(tp, relevant_documents):
    if (tp+relevant_documents) == 0:
        return 0
    else:
        recall_value = tp/float(relevant_documents)
        return recall_value

def calculate_f_measure(precision, recall):
    if (recall + precision) ==0:
        return 0
    else:
        f_measure_value = 2*recall*precision/float(recall + precision)
        return f_measure_value


def print_evaluation(taxonomy, evaluation_data):
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print 'Evaluation for ' + taxonomy + ' taxonomy'
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    print tabulate(evaluation_data, headers=['dialogue act name', 'precision', 'recall', 'F-measure',
                                             'True Positive', 'False Positive', 'Revevant Documents'])

# evaluation_taxonomy('full')
# evaluation_taxonomy('reduced')
# evaluation_taxonomy('min')


def overall_evaluation(taxonomy_name, cursor):
    da_names = postgres_queries.find_states(taxonomy_name, cursor)
    # taxonomy_tree = dialogue_acts_taxonomy.build_taxonomy(taxonomy_name)
    # da_names = taxonomy_tree.all_nodes()
    evaluation_data = list()
    tp = 0
    fp = 0
    relevant_documents = 0
    relevant_documents = len(postgres_queries.find_all_records('segmentation', cursor))
    for da_name in da_names:

        occurance_golden_standard = len(postgres_queries.find_all_da_occurances_taxonomy('segmentation',
                                        da_name, taxonomy_name, cursor))
        tp_da, fp_da = find_tp_fp(taxonomy_name, da_name, cursor)
        tp += tp_da
        fp += fp_da
        # relevant_documents += occurance_golden_standard
    precision = calculate_precision(tp, fp)
    recall = calculate_recall(tp, relevant_documents)
    f_measure = calculate_f_measure(precision, recall)
    da_evaluation = [precision, recall, f_measure, tp, fp, relevant_documents]
    evaluation_data.append(da_evaluation)
    # header_data = ['dialogue act name', 'precision', 'recall', 'F-measure']
    # print_evaluation(taxonomy_name, evaluation_data)
    print 'Overall evaluation for ' + taxonomy_name + ' taxonomy'
    print tabulate(evaluation_data, headers=['precision', 'recall', 'F-measure', 'True Positive', 'False Positive', 'Relevant Documents'])