__author__ = 'snownettle'
# calculate ICA for those tweets where we have the same segmentation
from math import factorial as fac
from math import pow


def chance_corrected_coefficient(list_of_tweets): #overall_observed_agreement
    sum_arg = 0
    i = 0 #number_of items
    number_of_assignments_to_category = dict() # nk
    for tweet in list_of_tweets:
        tokens = tweet.get_tags() #collections.defaultdict(dict)
        for token, tags in tokens.iteritems():
            i += 1
            sum_n_ik = 0
            for tag, agreement in tags.iteritems():
                n_ik = agreement  # stand for the number of times an item i is classified in categoty k
                binomial_n_ik = binomial(n_ik, 2)
                sum_n_ik += binomial_n_ik
                if tag in number_of_assignments_to_category:
                    number_of_assignments_to_category[tag] += agreement
                else:
                    number_of_assignments_to_category[tag] = agreement
            arg_i = sum_n_ik/float(binomial(3, 2))
            sum_arg += arg_i

    overall_observed_agreement = sum_arg/float(i)
    expected_agreement = ea(number_of_assignments_to_category, i)
    ccc = (overall_observed_agreement - expected_agreement)/float(1 - expected_agreement)
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


# print binomial(3,2)