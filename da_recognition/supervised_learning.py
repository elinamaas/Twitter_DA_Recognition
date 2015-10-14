__author__ = 'snownettle'
from tenFoldCrossValidation import split10
from learning import hmm_multinomial, crf, hmm_gaussian
from evaluation import da_evaluation
from analysing_GS.tf_idf import calculate_tf_idf, word_appearance_tfidf
import annotationRule


def train_test_seq(data_set):
    train_test_list = list()
    for i in range(0, 10, 1):
        data_set_copy = data_set.copy()
        train_set, test_set = split10.train_test_sets(data_set_copy, i)
        tokens_full, tokens_reduced, tokens__min = calculate_tf_idf(train_set)
        word_appearance_tfidf(train_set,tokens_full, tokens_reduced, tokens__min)
        word_appearance_tfidf(test_set,tokens_full, tokens_reduced, tokens__min)
        train_test_list.append([train_set, test_set])
    return train_test_list


def hmm_gaussian_algorithm(taxonomy, cursor, connection, train_test_list):
    for train_test in train_test_list:
        train_set = train_test[0]
        test_set = train_test[1]
        hmm_gaussian.calculate_hmm_g(train_set, test_set, taxonomy, cursor, connection)


def hmm_multinomial_algorithm(taxonomy, cursor, connection, train_test_list):
    for train_test in train_test_list:
        train_set = train_test[0]
        test_set = train_test[1]
        hmm_multinomial.calculate_hmm_m(train_set, test_set, taxonomy, cursor, connection)


def conditional_random_fields(taxonomy, cursor, connection, train_test_list):
    for train_test in train_test_list:
        train_set = train_test[0]
        test_set = train_test[1]
        crf.run_crf(train_set, test_set, taxonomy, cursor, connection)


def recognize_da(taxonomy_list, cursor, connection, data_set):
    train_test_set = train_test_seq(data_set)

    print 'Supervised learning: CRF'
    for taxonomy in taxonomy_list:
        print taxonomy + ' Taxonomy'
        conditional_random_fields(taxonomy, cursor, connection, train_test_set)
        da_evaluation.evaluation_taxonomy_da(taxonomy, cursor)
        da_evaluation.inter_annotation_agreement(taxonomy, cursor)
        da_evaluation.confusion_matrix(taxonomy, cursor)

    print '#############################################################'
    print 'With Rules'
    for taxonomy in taxonomy_list:
        print taxonomy + ' Taxonomy'
        annotationRule.assign_zero_da(taxonomy, cursor, connection)
        if taxonomy == 'full':
            annotationRule.assign_choice_q_da(taxonomy, cursor, connection)
        if taxonomy != 'full':
            annotationRule.assign_social_da(taxonomy, cursor, connection)
            annotationRule.assign_it_is_da(taxonomy, cursor, connection)
        da_evaluation.evaluation_taxonomy_da(taxonomy, cursor)
        da_evaluation.inter_annotation_agreement(taxonomy, cursor)
        da_evaluation.confusion_matrix(taxonomy, cursor)

    print 'Supervised learning: HMM Gaussian'

    # hmm_gaussian_algorithm('minimal', cursor, connection, train_test_set) # delete after using

    for taxonomy in taxonomy_list:
        print taxonomy + ' Taxonomy'
        hmm_gaussian_algorithm(taxonomy, cursor, connection, train_test_set)
        da_evaluation.evaluation_taxonomy_da(taxonomy, cursor)
        da_evaluation.inter_annotation_agreement(taxonomy, cursor)
        da_evaluation.confusion_matrix(taxonomy, cursor)

    print '#############################################################'
    print 'With Rules'
    for taxonomy in taxonomy_list:
        print taxonomy + ' Taxonomy'
        annotationRule.assign_zero_da(taxonomy, cursor, connection)
        if taxonomy == 'full':
            annotationRule.assign_choice_q_da(taxonomy, cursor, connection)
        if taxonomy != 'full':
            annotationRule.assign_social_da(taxonomy, cursor, connection)
            annotationRule.assign_it_is_da(taxonomy, cursor, connection)
        da_evaluation.evaluation_taxonomy_da(taxonomy, cursor)
        da_evaluation.inter_annotation_agreement(taxonomy, cursor)
        da_evaluation.confusion_matrix(taxonomy, cursor)

    print 'Supervised learning: HMM Multinomial'
    for taxonomy in taxonomy_list:
        print taxonomy + ' Taxonomy'
        hmm_multinomial_algorithm(taxonomy, cursor, connection, train_test_set)
        da_evaluation.evaluation_taxonomy_da(taxonomy, cursor)
        da_evaluation.inter_annotation_agreement(taxonomy, cursor)
        da_evaluation.confusion_matrix(taxonomy, cursor)

    print '#############################################################'
    print 'With Rules'
    for taxonomy in taxonomy_list:
        print taxonomy + ' Taxonomy'
        annotationRule.assign_zero_da(taxonomy, cursor, connection)
        if taxonomy == 'full':
            annotationRule.assign_choice_q_da(taxonomy, cursor, connection)
        if taxonomy != 'full':
            annotationRule.assign_social_da(taxonomy, cursor, connection)
            annotationRule.assign_it_is_da(taxonomy, cursor, connection)
        da_evaluation.evaluation_taxonomy_da(taxonomy, cursor)
        da_evaluation.inter_annotation_agreement(taxonomy, cursor)
        da_evaluation.confusion_matrix(taxonomy, cursor)
